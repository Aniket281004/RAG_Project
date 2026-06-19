import json
import os
from typing import List 
from src.llm import llm
from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title
from langchain_core.documents import Document 
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage
from langchain_openai import OpenAIEmbeddings 
from langchain_ollama import OllamaEmbeddings
from dotenv import load_dotenv
load_dotenv()

def partition_document(file_path:str):
    """Extract elements from pdf using unstructured"""
    print(f"Partitioning document: {file_path}")

    elements = partition_pdf(
        filename=file_path,
        strategy="hi_res",
        infer_table_structure=True,#keep tables in structured html
        extract_image_block_types=["Image"],
        extract_image_block_to_payload=True#strore img as base64 data

    )
    print(f"Extracted {len(elements)} elements")
    return elements

def create_chunks_by_title(elements):
    """Create intelligent chunks using title-based strategy"""
    print("Creating chunks")
    chunks = chunk_by_title(
        elements,
        max_characters=3000,
        new_after_n_chars=2400,
        combine_text_under_n_chars=500
    )
    print(f"Created {len(chunks)} chunks")
    return chunks

def separate_content_types(chunk):
    """Analyze what types of content are in a chunk"""
    content_data={
        'text': chunk.text,
        'tables':[],
        'images':[],
        'types':['text']
    }
    if hasattr(chunk,'metadata') and hasattr(chunk.metadata,'orig_elements'):
        for element in chunk.metadata.orig_elements:
            element_type = type(element).__name__
            
            if element_type =='Table':
                content_data['types'].append('table')
                table_html = getattr(element.metadata,'text_as_html',element.text)
                content_data['tables'].append(table_html)

            elif element_type == 'Image':
                if hasattr(element, 'metadata') and hasattr(element.metadata, 'image_base64'):
                    content_data['types'].append('image')
                    content_data['images'].append(element.metadata.image_base64)
    content_data['types'] = list(set(content_data['types']))
    return content_data

def create_ai_enhanced_summary(
    text: str,
    tables: List[str],
    images: List[str]
) -> str:
    """Create AI-enhanced summary for mixed content"""

    try:

        prompt = f"""
Summarize the following document chunk.
You are creating a searchable description for document content retrieval.

Main Text:
{text}
"""

        if tables:
            prompt += "Tables:\n"

            for i, table in enumerate(tables):
                prompt += f"Table {i+1}:\n{table}\n\n"

            prompt += """
You are an expert document analyst creating retrieval-optimized summaries for a semantic search system.
Your goal is to maximize FINDABILITY and SEARCH RECALL while remaining concise.
Analyze the provided content and generate a structured summary that captures:

1. Main topic and purpose.
2. Key concepts, technical terms, entities, methods, frameworks, algorithms, products, organizations, people, and domain-specific terminology.
3. Important relationships between concepts.
4. Numerical values, metrics, statistics, percentages, dates, benchmarks, and measurements.
5. Conclusions, findings, recommendations, and takeaways.
6. Alternative terminology, synonyms, abbreviations, and related search phrases that a user might use to find this content.
7. Context that would help semantic search match indirect queries.

For TABLES:
- Extract the meaning of the table, not just the values.
- Describe trends, comparisons, rankings, correlations, outliers, and key metrics.
- Convert structured data into searchable natural language.
- Include important column names, row categories, and business or technical implications.

TOPIC:
<one sentence>

SEARCHABLE SUMMARY:
"""

        message_content = [
            {
                "type": "text",
                "text": prompt
            }
        ]

        for image_base64 in images:
            message_content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }
            )

        message = HumanMessage(content=message_content)

        response = llm.invoke([message])

        return response.content

    except Exception as e:
        print(f"    AI summary failed: {e}")
        return f"{text[:300]}..."
    

def summarise_chunks(chunks):
    """Process chunks with AI Summaries..."""
    print("Processing chunks with AI Summaries...")
    langchain_documents=[]
    total_chunks = len(chunks)
    
    for i ,chunk in enumerate(chunks):
        current_chunk = i+1
        print(f" Processing chunk {current_chunk}/{total_chunks}")

        content_data = separate_content_types(chunk)

        print(f"    Types found: {content_data['types']}")
        print(f"    Tables: {len(content_data['tables'])} , Images: {len(content_data['images'])}")

        if content_data['tables'] or content_data['images']:
            print(f"    Creating AI summary for mixed content...")
            try:
                enhanced_content = create_ai_enhanced_summary(
                    content_data['text'],
                    content_data['tables'],
                    content_data['images']
                )
                print(f"    AI Summary created succesfully")
                print(f"    Enhanced content preview: {enhanced_content[:200]}...")
            except Exception as e:
                print(f"    AI summary failed:{e}")
                enhanced_content = content_data['text']
        else:
            print("        Using raw text (no tables/images)")
            enhanced_content = content_data['text']
        doc = Document(
            page_content=enhanced_content,
            metadata={
                "original_content": json.dumps({
                    "raw_text":content_data['text'],
                    "tables_html":content_data['tables'],
                    "images_base64":content_data['images']
                })
            }
        )

        langchain_documents.append(doc)
    print(f"Processed {len(langchain_documents)} chunks")
    return langchain_documents


def create_vector_store(documents,persist_directory="vector_db"):
    print("Creatng embeddings and storing in ChromaDB...")
    embedding_model = OllamaEmbeddings(
        model="nomic-embed-text"
    )

    print("--- Creating vector store ---")
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=persist_directory,
        collection_metadata={"hnsw:space":"cosine"}
    )
    print("--- Finished creating vector store ---")
    print(f"Vector store created and saved to {persist_directory}")
    return vectorstore


def run_complete_ingestion_pipeline(pdf_path:str = "./uplaods", persist_directory = "vector_db"):
    """Run the complete RAG ingestion pipeline"""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"{pdf_path} does not exist.")
    print("Starting RAG Ingestion Pipeline")
    print("="*50)
    
    elements =[] 
    for filename in os.listdir(pdf_path):
        if(filename.endswith(".pdf")):
            print("Processing:", filename)
            elements.extend(partition_document(os.path.join(pdf_path,filename)))
    
    chunks = create_chunks_by_title(elements)

    summarised_chunks = summarise_chunks(chunks)

    db = create_vector_store(summarised_chunks,persist_directory=persist_directory)

    print("Pipeline completed successfully")
    return db