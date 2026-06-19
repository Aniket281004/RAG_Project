from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

embeddings = OpenAIEmbeddings()

db = Chroma(
    persist_directory="vector_db",
    embedding_function=embeddings
)

retriever = db.as_retriever(
    search_kwargs={"k": 5}
)

def retrieve(query: str):
    return retriever.invoke(query)