from pathlib import Path
import shutil
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from src.pyq_ingestion import run_question_paper_ingestion_pipeline
from src.ingest import run_complete_ingestion_pipeline
from src.rag import generate_final_answer
from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str
    
app = FastAPI()

UPLOAD_DIR = Path("uploads")
STUDY_DIR = UPLOAD_DIR / "study_material"
PYQ_DIR = UPLOAD_DIR / "pyqs"

STUDY_DIR.mkdir(parents=True, exist_ok=True)
PYQ_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/")
def home():
    return {"message": "RAG Backend Running"}


@app.post("/upload/study-material")
async def upload_study_material(files: List[UploadFile] = File(...)):

    uploaded = []

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(400, "Only PDF files are allowed.")

        destination = STUDY_DIR / file.filename

        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        uploaded.append(file.filename)

    return {
        "message": "Study material uploaded successfully.",
        "files": uploaded
    }

@app.post("/upload/pyqs")
async def upload_pyqs(files: List[UploadFile] = File(...)):

    uploaded = []

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(400, "Only PDF files are allowed.")

        destination = PYQ_DIR / file.filename

        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        uploaded.append(file.filename)

    return {
        "message": "PYQs uploaded successfully.",
        "files": uploaded
    }


@app.post("/ingest")
def ingest():

    run_complete_ingestion_pipeline(
        pdf_path="./uploads/study_material",
        persist_directory="vector_db"
    )

    run_question_paper_ingestion_pipeline(
        pdf_path="./uploads/pyqs",
        persist_directory="question_vector_db"
    )

    return {
        "message": "Knowledge base built successfully."
    }



@app.post("/ask")
def ask(request: QueryRequest):

    answer = generate_final_answer(request.query)

    return {
        "question": request.query,
        "answer": answer
    }