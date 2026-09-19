from app.database.database import get_db, init_db
from app.database.models import DocumentMetadata

def save_document_metadata(
    filename: str,
    chunking_strategy: str,
    total_chunks: int,
    extracted_text: str,
    qdrant_collection: str,
) -> int:
    
    init_db()
    db = get_db()
    try:
        record = DocumentMetadata(
            filename=filename,
            chunking_strategy=chunking_strategy,
            total_chunks=total_chunks,
            extracted_text=extracted_text,
            qdrant_collection=qdrant_collection,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record.id
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
