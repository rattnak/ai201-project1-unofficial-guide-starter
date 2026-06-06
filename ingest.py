"""
Milestone 3: Document ingestion and chunking pipeline.

Loads .txt files from documents/, cleans them, and splits into chunks
using LangChain's RecursiveCharacterTextSplitter (size=1200, overlap=200).
"""

import os
import re
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter


DOCS_DIR = Path(__file__).parent / "documents"
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


def load_documents(docs_dir: Path = DOCS_DIR) -> list[dict]:
    """Load all .txt files from docs_dir, return list of {text, source} dicts."""
    docs = []
    for path in sorted(docs_dir.glob("*.txt")):
        if path.name == ".gitkeep":
            continue
        text = path.read_text(encoding="utf-8")
        docs.append({"text": text, "source": path.name})
    return docs


def clean_text(text: str) -> str:
    """Remove Reddit formatting artifacts and boilerplate noise."""
    # Remove HTML entities
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&#\d+;", "", text)

    # Remove Reddit markdown formatting
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)  # bold
    text = re.sub(r"\*(.*?)\*", r"\1", text)        # italic
    text = re.sub(r"~~(.*?)~~", r"\1", text)        # strikethrough

    # Remove [deleted] and [removed] placeholders
    text = re.sub(r"\[deleted\]", "", text)
    text = re.sub(r"\[removed\]", "", text)

    # Remove URL-only lines
    text = re.sub(r"^https?://\S+$", "", text, flags=re.MULTILINE)

    # Collapse 3+ blank lines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip leading/trailing whitespace per line
    lines = [line.rstrip() for line in text.splitlines()]
    text = "\n".join(lines)

    return text.strip()


def chunk_documents(docs: list[dict]) -> list[dict]:
    """Split documents into chunks, preserving source metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = []
    for doc in docs:
        cleaned = clean_text(doc["text"])
        pieces = splitter.split_text(cleaned)
        for i, piece in enumerate(pieces):
            piece = piece.strip()
            if len(piece) > 50:  # skip fragments too short to be meaningful
                chunks.append({
                    "text": piece,
                    "source": doc["source"],
                    "chunk_index": i,
                })
    return chunks


def run_pipeline(docs_dir: Path = DOCS_DIR) -> list[dict]:
    """Full ingestion pipeline: load → clean → chunk."""
    docs = load_documents(docs_dir)
    if not docs:
        raise ValueError(f"No .txt files found in {docs_dir}")
    chunks = chunk_documents(docs)
    return chunks


if __name__ == "__main__":
    chunks = run_pipeline()
    print(f"Loaded documents, produced {len(chunks)} chunks.\n")
    print("--- 5 sample chunks ---\n")
    import random
    for chunk in random.sample(chunks, min(5, len(chunks))):
        print(f"Source: {chunk['source']} | chunk #{chunk['chunk_index']}")
        print(chunk["text"][:300])
        print("---")
