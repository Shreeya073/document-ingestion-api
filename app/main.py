from fastapi import FastAPI

from app.api.documents import router as documents_router
from app.database.database import Base, create_database, get_engine, init_db

app = FastAPI(
    title="Document Ingestion API",
    version="1.0.0",
)

app.include_router(
    documents_router,
    prefix="/documents",
)

@app.on_event("startup")
def startup() -> None:

    create_database()
    init_db()

@app.get("/")
def root() -> dict[str, str]:

    return {
        "message": "Document Ingestion API is running"
    }