from pathlib import Path
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException

from src.ingest import run_complete_ingestion_pipeline
from src.rag import generate_final_answer

app = FastAPI()

UPLOAD_DIR = Path("uploads")
# STUDY_DIR = UPLOAD_DIR / "study_material"

# STUDY_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/")
def home():
    return {"message": "RAG Backend Running"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are allowed.")

    destination = UPLOAD_DIR / file.filename

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "Upload successful",
        "filename": file.filename
    }


@app.post("/ingest")
def ingest():

    run_complete_ingestion_pipeline(
        pdf_path="./uploads",
        persist_directory="vector_db"
    )

    return {
        "message": "Vector database created successfully."
    }


@app.post("/ask")
def ask(query: str):

    answer = generate_final_answer(query)

    return {
        "question": query,
        "answer": answer
    }