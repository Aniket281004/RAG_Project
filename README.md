# 📚 RAG Question Paper Generator

A modular Retrieval-Augmented Generation (RAG) pipeline built using **FastAPI**, **LangChain**, **ChromaDB**, and **OpenAI/Ollama**. The project allows users to upload study material, build a searchable vector database, and query the uploaded documents using Large Language Models.

This repository currently contains the backend implementation. A JavaScript frontend will be integrated in future updates.

---

## Features

* PDF ingestion using Unstructured
* Automatic document chunking
* Optional chunk summarization
* Vector database creation using ChromaDB
* Semantic search with embeddings
* LLM-powered question answering
* FastAPI backend with REST APIs
* Modular architecture for easy extension

---

## Tech Stack

* Python 3.13+
* FastAPI
* LangChain
* ChromaDB
* OpenAI API / Ollama
* Unstructured
* python-dotenv

---

## Project Structure

```
RAG_Project/
│
├── src/
│   ├── ingest.py
│   ├── retrieve.py
│   ├── rag.py
│   ├── llm.py
│   └── utils.py
│
├── uploads/
│
├── vector_db/
│
├── app.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/<your-username>/<repository-name>.git
cd <repository-name>
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root.

Example:

```env
OPENAI_API_KEY=your_api_key
```

---

## Running the Backend

Start the FastAPI server

```bash
uvicorn app:app --reload
```

The API will be available at

```
http://127.0.0.1:8000
```

Interactive API documentation

```
http://127.0.0.1:8000/docs
```

---

## API Endpoints

### Upload PDF

```
POST /upload
```

Uploads one or more PDF files.

---

### Build Vector Database

```
POST /ingest
```

Runs the complete ingestion pipeline:

* Partition PDFs
* Create chunks
* Generate summaries
* Generate embeddings
* Store embeddings in ChromaDB

---

### Ask Questions

```
POST /ask
```

Queries the vector database and generates answers using the configured LLM.

---

## Pipeline

```
PDF Upload
      │
      ▼
Partition Documents
      │
      ▼
Chunk Documents
      │
      ▼
Summarize Chunks
      │
      ▼
Generate Embeddings
      │
      ▼
Store in ChromaDB
      │
      ▼
Retriever
      │
      ▼
Large Language Model
      │
      ▼
Generated Response
```

---

## Future Work

* User authentication
* JavaScript frontend
* Multiple document collections
* Question paper generation
* Syllabus-aware retrieval
* Citation support
* Streaming responses
* Docker deployment
* Cloud deployment

---

## Notes

* Do not commit your `.env` file.
* The `vector_db` directory is generated automatically.
* Uploaded PDFs should be placed inside the `uploads` directory.

---

## License

This project is intended for educational and research purposes.
