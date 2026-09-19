import os
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

collection_name = os.getenv("QDRANT_COLLECTION", "documents")

def get_client() -> QdrantClient:
    qdrant_url = os.getenv("QDRANT_URL")
    if qdrant_url:
        return QdrantClient(url=qdrant_url)
    return QdrantClient(
        path=os.getenv("QDRANT_PATH", "qdrant_data"),
    )

def create_collection(client: QdrantClient):
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE
            )
        )

def store_embeddings(
    chunks: list[str],
    embeddings: list[list[float]],
    filename: str
):

    client = get_client()
    create_collection(client)
    points = []

    for i, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):

        points.append(
            PointStruct(
                id=str(uuid4()),
                vector=embedding,
                payload={
                    "filename": filename,
                    "chunk": chunk,
                },
            )
        )

    if points:
        client.upsert(collection_name=collection_name, points=points, wait=True)
