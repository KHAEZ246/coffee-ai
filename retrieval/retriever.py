import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import chromadb
from config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION


def get_relevant_chunks(query: str, n_results: int = 5) -> list[dict]:
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    collection = client.get_or_create_collection(name=CHROMA_COLLECTION)

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "content": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i] if results["distances"] else None
        })

    return chunks


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python -m retrieval.retriever <query>")
        sys.exit(1)

    query = sys.argv[1]
    results = get_relevant_chunks(query)

    print(f"Query: {query}")
    print(f"Found {len(results)} relevant chunks:\n")
    for i, chunk in enumerate(results, 1):
        print(f"--- Chunk {i} (distance: {chunk['distance']:.4f}) ---")
        print(chunk["content"][:200] + "...")
        print()
