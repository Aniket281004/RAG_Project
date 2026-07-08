import json
import os
import re
from typing import List
from types import SimpleNamespace
import pandas as pd
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from unstructured.partition.pdf import partition_pdf
from src.llm import llm
load_dotenv()

QUESTION_REGEX = re.compile(
    r"^\s*(?:Q(?:uestion)?\.?\s*)?(\d+)(?:[\.\)]|\b)",
    re.IGNORECASE,
)

def partition_document(file_path: str):
    """
    Extract elements from PDF using Unstructured.
    """

    print(f"Partitioning {file_path}")

    elements = partition_pdf(
        filename=file_path,
        strategy="hi_res",
        infer_table_structure=True,
        extract_image_block_types=["Image"],
        extract_image_block_to_payload=True,
    )

    print(f"Extracted {len(elements)} elements")

    return elements

def extract_question_mapping(elements):
    """
    Reads the question mapping table at the beginning
    of the paper.

    Returns:

    {
        "Q1": {
            "unit": "1"
        },
        "Q2": {
            "unit": "3"
        }
    }
    """

    print("Searching for Question Mapping Table...")

    question_map = {}

    for element in elements:

        if type(element).__name__ != "Table":
            continue

        html = getattr(element.metadata, "text_as_html", None)

        if html is None:
            continue

        try:

            dfs = pd.read_html(html)

            if len(dfs) == 0:
                continue

            df = dfs[0]

            df.columns = [
                str(c).strip().lower()
                for c in df.columns
            ]

            question_col = None
            unit_col = None

            for col in df.columns:

                if "question" in col or col == "q":
                    question_col = col

                if "unit" in col:
                    unit_col = col

            if question_col is None or unit_col is None:
                continue

            for _, row in df.iterrows():

                q = str(row[question_col]).strip().upper()

                if not q.startswith("Q"):
                    q = "Q" + re.findall(r"\d+", q)[0]

                question_map[q] = {
                    "unit": str(row[unit_col]).strip()
                }

            print("Question Mapping Found")
            print(question_map)

            return question_map

        except Exception:
            continue

    print("No Question Mapping Found")

    return question_map

def create_chunks_by_question(elements):
    """
    Creates one chunk per question.

    Everything between

        Q1 .....
        Q2 .....

    belongs to one chunk.

    Images and Tables stay attached because
    orig_elements are preserved.
    """

    print("Creating Question Chunks...")

    chunks = []

    current_chunk = None

    for element in elements:

        text = getattr(element, "text", "")

        text = text.strip() if text else ""

        match = QUESTION_REGEX.match(text)

        # NEW QUESTION

        if match:

            if current_chunk is not None:

                current_chunk.text = current_chunk.text.strip()

                chunks.append(current_chunk)

            current_chunk = SimpleNamespace(

                question_no=f"Q{match.group(1)}",

                text="",

                metadata=SimpleNamespace(
                    orig_elements=[]
                )

            )

        # Ignore everything before first question

        if current_chunk is None:
            continue

        # Preserve original elements

        current_chunk.metadata.orig_elements.append(
            element
        )

        # Append text

        if text:

            current_chunk.text += text + "\n"

    if current_chunk is not None:

        current_chunk.text = current_chunk.text.strip()

        chunks.append(current_chunk)

    print(f"Created {len(chunks)} Question Chunks")

    return chunks

def separate_content_types(chunk):
    """
    Separate text, tables and images from a question chunk.
    """

    content_data = {
        "text": chunk.text,
        "tables": [],
        "images": [],
        "types": ["text"]
    }

    if hasattr(chunk, "metadata") and hasattr(chunk.metadata, "orig_elements"):

        for element in chunk.metadata.orig_elements:

            element_type = type(element).__name__

            if element_type == "Table":

                content_data["types"].append("table")

                table_html = getattr(
                    element.metadata,
                    "text_as_html",
                    element.text
                )

                content_data["tables"].append(table_html)

            elif element_type == "Image":

                image_base64 = getattr(
                    element.metadata,
                    "image_base64",
                    None
                )

                if image_base64:

                    content_data["types"].append("image")

                    content_data["images"].append(image_base64)

    content_data["types"] = list(set(content_data["types"]))

    return content_data

def create_ai_enhanced_summary(
    text: str,
    tables: List[str],
    images: List[str]
):
    """
    Create a retrieval description for a question.
    """

    try:

        prompt = f"""
You are analysing an examination question.
Your job is NOT to answer the question.
Generate a retrieval-optimized description.
Question:

{text}

Return the following information.

Topic:
Subtopic:
Question Type:
Difficulty:
Expected Concepts:
Keywords:
Requires Diagram:
Requires Table:
Requires Numerical:
Short Retrieval Description:

Do not solve the question.
"""

        if tables:

            prompt += "\n\nTables:\n"

            for table in tables:
                prompt += table + "\n\n"

        message_content = [

            {
                "type": "text",
                "text": prompt
            }

        ]

        for image in images:

            message_content.append(

                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image}"
                    }
                }

            )

        response = llm.invoke(

            [
                HumanMessage(
                    content=message_content
                )
            ]

        )

        return response.content

    except Exception as e:

        print(e)

        return text

def build_question_documents(
    chunks,
    question_map
):
    """
    Convert Question Chunks into LangChain Documents.
    """

    print("Building Question Documents...")

    documents = []

    total = len(chunks)

    for i, chunk in enumerate(chunks):

        print(f"Processing {i+1}/{total}")

        content = separate_content_types(chunk)

        print(
            f"Tables: {len(content['tables'])} | Images: {len(content['images'])}"
        )

        retrieval_description = create_ai_enhanced_summary(

            content["text"],
            content["tables"],
            content["images"]

        )

        metadata = {
            "question_no": chunk.question_no,
            **question_map.get(
                chunk.question_no,
                {}
            ),
            "original_content": json.dumps(
                {
                    "raw_text": content["text"],
                    "tables_html": content["tables"],
                    "images_base64": content["images"]
                }
            )
        }
        documents.append(
            Document(
                page_content=retrieval_description,
                metadata=metadata
            )
        )
    print(f"Created {len(documents)} documents")
    return documents

def create_vector_store(
    documents,
    persist_directory="question_vector_db"
):
    """
    Create Chroma Vector Store.
    """

    print("Creating embeddings...")

    embedding_model = OllamaEmbeddings(
        model="nomic-embed-text"
    )

    vectorstore = Chroma.from_documents(

        documents=documents,

        embedding=embedding_model,

        persist_directory=persist_directory,

        collection_metadata={
            "hnsw:space": "cosine"
        }

    )

    print(f"Saved vector store to {persist_directory}")

    return vectorstore

def run_question_paper_ingestion_pipeline(
    pdf_path="./uploads/pyqs",
    persist_directory="question_vector_db"
):
    """
    Complete Question Paper Ingestion Pipeline
    """

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(
            f"{pdf_path} does not exist."
        )

    print("=" * 60)
    print("QUESTION PAPER INGESTION PIPELINE")
    print("=" * 60)

    elements = []

    for filename in os.listdir(pdf_path):

        if filename.lower().endswith(".pdf"):

            print(f"\nProcessing: {filename}")

            pdf_elements = partition_document(
                os.path.join(pdf_path, filename)
            )

            elements.extend(pdf_elements)

    print()

    question_map = extract_question_mapping(
        elements
    )

    chunks = create_chunks_by_question(
        elements
    )

    documents = build_question_documents(
        chunks,
        question_map
    )
 
    db = create_vector_store(
        documents,
        persist_directory=persist_directory
    )

    print("Question Paper Ingestion Complete")
    print(f"Questions Stored : {len(documents)}")
    return db

run_question_paper_ingestion_pipeline()