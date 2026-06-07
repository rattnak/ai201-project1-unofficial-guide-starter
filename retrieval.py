"""
Milestone 4: Embedding and retrieval pipeline.

Embeds chunks with all-MiniLM-L6-v2, stores in ChromaDB,
and retrieves top-k relevant chunks for a given query.
"""

import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
from ingest import run_pipeline

CHROMA_DIR = str(Path(__file__).parent / "chroma_db")
COLLECTION_NAME = "boston_housing"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 5

_model: SentenceTransformer | None = None
_collection = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL_NAME)
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def build_index(force_rebuild: bool = False) -> int:
    """
    Embed all chunks and store in ChromaDB.
    Skips rebuild if collection already has documents (unless force_rebuild=True).
    Returns number of chunks indexed.
    """
    collection = _get_collection()

    if not force_rebuild and collection.count() > 0:
        print(f"Index already contains {collection.count()} chunks. Skipping rebuild.")
        return collection.count()

    if force_rebuild:
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        client.delete_collection(COLLECTION_NAME)
        _collection_reset()

    chunks = run_pipeline()
    model = _get_model()

    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32).tolist()

    collection = _get_collection()
    collection.add(
        ids=[f"{c['source']}__chunk{c['chunk_index']}" for c in chunks],
        documents=texts,
        embeddings=embeddings,
        metadatas=[{"source": c["source"], "chunk_index": c["chunk_index"]} for c in chunks],
    )

    print(f"Indexed {len(chunks)} chunks into ChromaDB.")
    return len(chunks)


def _collection_reset():
    """Reset the cached collection reference so it gets recreated."""
    global _collection
    _collection = None


def retrieve(query: str, k: int = TOP_K) -> list[dict]:
    """
    Retrieve top-k chunks most semantically similar to query.
    Returns list of {text, source, chunk_index, distance} dicts.
    """
    model = _get_model()
    collection = _get_collection()

    query_embedding = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "text": doc,
            "source": meta["source"],
            "chunk_index": meta["chunk_index"],
            "distance": round(dist, 4),
        })
    return chunks


if __name__ == "__main__":
    print("Building index...")
    n = build_index()
    print(f"\nIndex ready with {n} chunks.\n")

    test_queries = [
        "What do students say about landlords in Allston?",
        "Is Mission Hill safe for college students at night?",
        "What lease red flags should Boston students watch out for?",
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)
        results = retrieve(query)
        for r in results:
            print(f"  [{r['distance']:.3f}] {r['source']}")
            print(f"  {r['text'][:200]}\n")
