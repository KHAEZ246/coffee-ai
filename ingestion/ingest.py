import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pypdf import PdfReader
import chromadb
from config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION, CHUNK_SIZE, CHUNK_OVERLAP


def extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def ingest_pdf(pdf_path: str):
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return

    print(f"Extracting text from {pdf_path}...")
    text = extract_text_from_pdf(pdf_path)

    print("Chunking text...")
    chunks = chunk_text(text)
    print(f"Created {len(chunks)} chunks")

    print("Storing in ChromaDB...")
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    collection = client.get_or_create_collection(name=CHROMA_COLLECTION)

    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            metadatas=[{"source": pdf_path, "chunk_index": i}],
            ids=[f"{Path(pdf_path).stem}_{i}"]
        )

    print(f"Successfully ingested {len(chunks)} chunks into ChromaDB")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python -m ingestion.ingest <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    ingest_pdf(pdf_path)
