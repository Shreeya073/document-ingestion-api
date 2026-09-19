# Document Ingestion API

A FastAPI-based REST API for uploading and processing documents for a RAG system.

## Features

* Upload PDF and text documents
* Extract document content
* Split content into chunks
* Generate embeddings
* Store document chunks and embeddings in Qdrant

## Technologies 

* Python
* FastAPI
* Qdrant
* Sentence Transformers
* PyPDF

## Run Qdrant
`http://localhost:6333`

## Run the API

```bash
uvicorn app.main:app --reload
```

API documentation:

`http://127.0.0.1:8000/docs`
