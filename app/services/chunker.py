import re

def fixed_size_chunking(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> list[str]:

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks

def sentence_chunking(
    text: str,
    sentences_per_chunk: int = 5
) -> list[str]:

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text.strip()
    )

    chunks = []

    for i in range(
        0,
        len(sentences),
        sentences_per_chunk
    ):
        chunk = " ".join(
            sentences[i:i + sentences_per_chunk]
        ).strip()

        if chunk:
            chunks.append(chunk)

    return chunks

def create_chunks(
    text: str,
    strategy: str
) -> list[str]:

    if strategy == "fixed":
        return fixed_size_chunking(text)

    elif strategy == "sentence":
        return sentence_chunking(text)

    else:
        raise ValueError(
            "Invalid chunking strategy. "
            "Use 'fixed' or 'sentence'."
        )