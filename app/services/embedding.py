from functools import lru_cache

from sentence_transformers import SentenceTransformer

@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer("all-MiniLM-L6-v2")

def generate_embeddings(chunks: list[str]) -> list[list[float]]:
    if not chunks:
        return []
    
    return get_model().encode(chunks, normalize_embeddings=True).tolist()
