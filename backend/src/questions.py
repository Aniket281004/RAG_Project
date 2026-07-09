from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

embedding = OllamaEmbeddings(model="nomic-embed-text")

db = Chroma(
    persist_directory="question_vector_db",
    embedding_function=embedding
)

data = db.get()

print("Number of documents:", len(data["documents"]))

for i in range(len(data["documents"])):
    print("=" * 50)
    print("Document:", i + 1)
    print("Content:")
    print(data["documents"][i])
    print("\nMetadata:")
    print(data["metadatas"][i])