from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status
from qdrant_client.http.exceptions import ResponseHandlingException, UnexpectedResponse
from sqlalchemy.exc import SQLAlchemyError

from app.services.metadata_store import save_document_metadata
from app.services.extractor import SUPPORTED_SUFFIXES, extract_text
from app.services.chunker import create_chunks
from app.services.embedding import generate_embeddings
from app.services.vector_store import collection_name, store_embeddings

router = APIRouter()

upload_folder = Path("uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024

@router.post("/extract")
async def extract_document_text(file: UploadFile = File(...)) -> dict[str, str]:
    original_name = file.filename or "document"
    suffix = Path(original_name).suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise HTTPException(status_code=415, detail="Only PDF and TXT files are supported.")

    content = await file.read(MAX_FILE_SIZE + 1)
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File must be 10 MB or smaller.")
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    upload_folder.mkdir(parents=True, exist_ok=True)
    file_path = upload_folder / f"{uuid4()}{suffix}"
    file_path.write_bytes(content)
    try:
        text = extract_text(file_path)
    except OSError as error:
        raise HTTPException(status_code=422, detail="The document could not be read.") from error
    finally:
        file_path.unlink(missing_ok=True)

    if not text.strip():
        raise HTTPException(status_code=422, detail="No extractable text was found in this document.")
    return {"filename": original_name, "text": text}

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    strategy: str = Query("fixed", pattern="^(fixed|sentence)$"),
):
    original_name = file.filename or "document"
    suffix = Path(original_name).suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise HTTPException(status_code=415, detail="Only PDF and TXT files are supported.")

    content = await file.read(MAX_FILE_SIZE + 1)
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File must be 10 MB or smaller.")
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    upload_folder.mkdir(parents=True, exist_ok=True)
    file_path = upload_folder / f"{uuid4()}{suffix}"
    file_path.write_bytes(content)
    try:
        text = extract_text(file_path)
        chunks = create_chunks(text, strategy)
        if not chunks:
            raise HTTPException(status_code=422, detail="No extractable text was found in this document.")
        store_embeddings(chunks, generate_embeddings(chunks), original_name)
        metadata_id = save_document_metadata(
            filename=original_name,
            chunking_strategy=strategy,
            total_chunks=len(chunks),
            extracted_text=text,
            qdrant_collection=collection_name,
        )
    except HTTPException:
        raise
    except (ResponseHandlingException, UnexpectedResponse, OSError) as error:
        raise HTTPException(status_code=503, detail="Vector database is unavailable. Start Qdrant and try again.") from error
    except SQLAlchemyError as error:
        raise HTTPException(status_code=503, detail="MySQL is unavailable. Check your database settings and try again.") from error
    finally:
        file_path.unlink(missing_ok=True)

    return {
        "filename": original_name,
        "chunking_strategy": strategy,
        "total_chunks": len(chunks),
        "extracted_text": text,
        "metadata_id": metadata_id,
        "message": "Document processed successfully",
    }
