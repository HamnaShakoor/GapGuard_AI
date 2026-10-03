"""ChromaDB + embeddings wrapper for GapGuard AI.

Design choices
* We compute embeddings ourselves and pass them to Chroma. This avoids version
  problems with Chroma's embedding-function API.
* Settings are read from environment variables at call time (easy to override in tests):
    CHROMA_DIR           default "data/chroma_db"
    CHROMA_COLLECTION    default "requirements"
    EMBEDDING_BACKEND    "auto" (default) | "sentence-transformers" | "onnx" | "hash"
    EMBEDDING_MODEL      default "all-MiniLM-L6-v2" (sentence-transformers backend only)
    ONNX_MODEL_DIR       optional folder for the downloaded ONNX model (default ~/.cache/chroma)
  auto  = sentence-transformers if installed, otherwise onnx.
  onnx  = same all-MiniLM-L6-v2 model via onnxruntime (bundled with chromadb). No PyTorch
          needed, so the install is much smaller. Downloads ~80 MB model on first use.
  hash  = tiny offline lexical embedder. Use it for unit tests only, NOT for the final demo.
"""
from __future__ import annotations

import hashlib
import math
import os
import re
from typing import Any, Sequence

import chromadb
from chromadb.config import Settings

from rag.chunker import Chunk

HASH_DIM = 384
_STOP = {"a", "an", "the", "of", "and", "or", "to", "in", "on", "for", "is", "are", "be",
         "by", "with", "as", "at", "this", "that", "from", "must", "all", "any"}

_clients: dict[str, Any] = {}
_model = None
_onnx = None


# ------------------------------- settings ---------------------------------- #
def chroma_dir() -> str:
    return os.getenv("CHROMA_DIR", "data/chroma_db")


def collection_name() -> str:
    return os.getenv("CHROMA_COLLECTION", "requirements")


def embedding_backend() -> str:
    """Resolved backend name: sentence-transformers | onnx | hash."""
    name = os.getenv("EMBEDDING_BACKEND", "auto").lower()
    if name == "auto":
        import importlib.util
        has_st = importlib.util.find_spec("sentence_transformers") is not None
        return "sentence-transformers" if has_st else "onnx"
    return name


# ------------------------------- embeddings -------------------------------- #
def _hash_embed(text: str) -> list[float]:
    toks = []
    for t in re.findall(r"[a-z0-9]+", text.lower()):
        if t in _STOP:
            continue
        toks.append(t[:-1] if len(t) > 3 and t.endswith("s") else t)
    feats = toks + [f"{a}_{b}" for a, b in zip(toks, toks[1:])]
    vec = [0.0] * HASH_DIM
    for f in feats:
        h = int(hashlib.md5(f.encode()).hexdigest(), 16)
        vec[h % HASH_DIM] += 1.0 if (h >> 64) & 1 else -1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _load_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as e:  # pragma: no cover
            raise RuntimeError(
                "sentence-transformers is not installed. Run `pip install sentence-transformers` "
                "or set EMBEDDING_BACKEND=hash for offline testing."
            ) from e
        _model = SentenceTransformer(os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))
    return _model


def _onnx_embed(texts: Sequence[str]) -> list[list[float]]:
    global _onnx
    if _onnx is None:
        from pathlib import Path

        from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

        # Optional: keep the ~80 MB model off the C: drive (set ONNX_MODEL_DIR=D:\models)
        custom = os.getenv("ONNX_MODEL_DIR")
        if custom:
            ONNXMiniLM_L6_V2.DOWNLOAD_PATH = Path(custom) / "all-MiniLM-L6-v2"
        _onnx = ONNXMiniLM_L6_V2()
    out = []
    for vec in _onnx(list(texts)):
        v = [float(x) for x in vec]
        norm = math.sqrt(sum(x * x for x in v)) or 1.0
        out.append([x / norm for x in v])
    return out


def embed_texts(texts: Sequence[str]) -> list[list[float]]:
    backend = embedding_backend()
    if backend == "hash":
        return [_hash_embed(t) for t in texts]
    if backend == "onnx":
        return _onnx_embed(texts)
    return _load_model().encode(list(texts), normalize_embeddings=True).tolist()


# ------------------------------- chroma ------------------------------------ #
def get_client():
    path = chroma_dir()
    if path not in _clients:
        os.makedirs(path, exist_ok=True)
        _clients[path] = chromadb.PersistentClient(
            path=path, settings=Settings(anonymized_telemetry=False)
        )
    return _clients[path]


def get_collection():
    return get_client().get_or_create_collection(
        collection_name(), metadata={"hnsw:space": "cosine"}
    )


def reset_collection():
    """Drop and recreate the collection (fresh requirements per application)."""
    client = get_client()
    try:
        client.delete_collection(collection_name())
    except Exception:
        pass  # collection did not exist yet
    return client.create_collection(collection_name(), metadata={"hnsw:space": "cosine"})


def collection_count() -> int:
    return get_collection().count()


def add_chunks(chunks: Sequence[Chunk]) -> int:
    if not chunks:
        return 0
    col = get_collection()
    col.add(
        ids=[c.id for c in chunks],
        documents=[c.embed_text for c in chunks],
        embeddings=embed_texts([c.embed_text for c in chunks]),
        metadatas=[c.to_metadata() for c in chunks],
    )
    return len(chunks)


def query(text: str, k: int = 3, where: dict | None = None) -> list[dict[str, Any]]:
    """Return [{id, metadata, distance}] ordered best-first."""
    col = get_collection()
    n = col.count()
    if n == 0:
        return []
    res = col.query(
        query_embeddings=embed_texts([text]),
        n_results=max(1, min(k, n)),
        where=where,
        include=["metadatas", "distances"],
    )
    return [
        {"id": i, "metadata": m, "distance": d}
        for i, m, d in zip(res["ids"][0], res["metadatas"][0], res["distances"][0])
    ]


def get_all(where: dict | None = None) -> list[dict[str, Any]]:
    """Return every stored chunk in document order (no similarity search)."""
    res = get_collection().get(where=where, include=["metadatas"])
    rows = [{"id": i, "metadata": m} for i, m in zip(res["ids"], res["metadatas"])]
    return sorted(rows, key=lambda r: r["metadata"].get("chunk_index", 0))