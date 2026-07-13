from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="nomic-embed-text")

def get_retriever(db_path: str, k: int = 3):

    class EmptyRetriever:
        def invoke(self, query):
            return []

    if not Path(db_path).exists():
        return EmptyRetriever()

    db = Chroma(
        persist_directory=db_path,
        embedding_function=embeddings
    )

    if db._collection.count() == 0:
        return EmptyRetriever()

    return db.as_retriever(
        search_kwargs={"k": k}
    )

def retrieve(query: str):
    study_chunks = get_retriever("vector_db/study_material").invoke(query)
    pyq_chunks = get_retriever("vector_db/pyqs",10).invoke(query)

    return {
        "study_material": study_chunks,
        "pyqs": pyq_chunks
    }