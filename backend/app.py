from pathlib import Path
import shutil
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from src.pyq_ingestion import run_question_paper_ingestion_pipeline
from src.ingest import run_complete_ingestion_pipeline
from src.rag import generate_final_answer
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class QueryRequest(BaseModel):
    query: str

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


@app.get("/files")
def get_uploaded_files():
    study_files = [
        file.name
        for file in STUDY_DIR.iterdir()
        if file.is_file()
    ]

    pyq_files = [
        file.name
        for file in PYQ_DIR.iterdir()
        if file.is_file()
    ]

    return {
        "study_files": study_files,
        "pyq_files": pyq_files
    }
@app.post("/ingest")
def ingest():
    study_path = Path("./uploads/study_material")
    pyq_path = Path("./uploads/pyqs")

    study_files = list(study_path.glob("*.pdf"))
    pyq_files = list(pyq_path.glob("*.pdf"))

    if not study_files and not pyq_files:
        raise HTTPException(
            status_code=400,
            detail="No files available for ingestion"
        )

    ingested = []

    if study_files:
        run_complete_ingestion_pipeline(
            pdf_path=str(study_path),
            persist_directory="vector_db/study_material"
        )

        ingested.append("study_material")

    if pyq_files:
        run_question_paper_ingestion_pipeline(
            pdf_path=str(pyq_path),
            persist_directory="vector_db/pyqs"
        )

        ingested.append("pyqs")

    return {
        "message": "Knowledge base built successfully",
        "ingested": ingested
    }


@app.post("/ask")
def ask(query: str):
    answer = generate_final_answer(query)

    return {
        "question": query,
        "answer": answer
    }