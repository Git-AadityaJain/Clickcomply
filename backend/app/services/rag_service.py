"""
Vector RAG using ChromaDB for DPDP knowledge and per-document chunks.
"""

from __future__ import annotations

import hashlib
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection

from app.core.config import settings
from app.core.logging import logger
from app.dpdp.dpdp_rules import COMPLIANCE_RULES
from app.dpdp.dpdp_rules_2025 import DPDP_RULES_2025
from app.dpdp.dpdp_sections import DPDP_SECTIONS
from app.services.llm_client import embed_texts

DPDP_COLLECTION = "dpdp_knowledge"
DOCUMENT_COLLECTION = "document_chunks"

_chroma_client: chromadb.PersistentClient | None = None
_dpdp_seeded = False


def _get_client() -> chromadb.PersistentClient:
    global _chroma_client
    if _chroma_client is None:
        settings.CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=str(settings.CHROMA_DIR))
    return _chroma_client


def _chunk_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> list[str]:
    size = chunk_size or settings.RAG_CHUNK_SIZE
    ov = overlap or settings.RAG_CHUNK_OVERLAP
    text = text.strip()
    if not text:
        return []
    if len(text) <= size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - ov
    return chunks


def _get_dpdp_collection() -> Collection:
    return _get_client().get_or_create_collection(
        name=DPDP_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )


def _get_document_collection() -> Collection:
    return _get_client().get_or_create_collection(
        name=DOCUMENT_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )


def init_dpdp_knowledge_base() -> None:
    """Seed Chroma with DPDP sections and compliance rules (idempotent)."""
    global _dpdp_seeded

    fp = knowledge_base_fingerprint()
    client = _get_client()

    try:
        collection = client.get_collection(DPDP_COLLECTION)
        stored_fp = (collection.metadata or {}).get("content_fingerprint")
        if collection.count() > 0 and stored_fp == fp:
            _dpdp_seeded = True
            logger.info("DPDP knowledge base already seeded in Chroma")
            return
        client.delete_collection(DPDP_COLLECTION)
        logger.info("DPDP knowledge base content changed: re-seeding Chroma")
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name=DPDP_COLLECTION,
        metadata={"hnsw:space": "cosine", "content_fingerprint": fp},
    )

    documents: list[str] = []
    metadatas: list[dict[str, Any]] = []
    ids: list[str] = []

    for key, section in DPDP_SECTIONS.items():
        doc_text = (
            f"{section['section']}: {section['title']}\n"
            f"{section['description']}"
        )
        doc_id = f"section-{key}"
        documents.append(doc_text)
        metadatas.append({"type": "section", "section_key": key, "section_ref": section["section"]})
        ids.append(doc_id)

    for rule in COMPLIANCE_RULES:
        doc_text = (
            f"Rule {rule['rule_id']} ({rule['section_ref']}): {rule['description']}\n"
            f"Evaluation hint: {rule['ai_prompt_hint']}"
        )
        doc_id = f"rule-{rule['rule_id']}"
        documents.append(doc_text)
        metadatas.append(
            {
                "type": "rule",
                "rule_id": rule["rule_id"],
                "section_ref": rule["section_ref"],
                "severity": rule["severity"],
            }
        )
        ids.append(doc_id)

    for rule in DPDP_RULES_2025:
        doc_text = (
            f"DPDP Rules 2025 {rule['rule_ref']} ({rule['act_ref']}): {rule['title']}\n"
            f"{rule['description']}"
        )
        doc_id = f"r2025-{rule['rule_key']}"
        documents.append(doc_text)
        metadatas.append(
            {
                "type": "dpdp_rule_2025",
                "rule_ref": rule["rule_ref"],
                "act_ref": rule["act_ref"],
                "rule_key": rule["rule_key"],
            }
        )
        ids.append(doc_id)

    embeddings = embed_texts(documents)
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )
    _dpdp_seeded = True
    logger.info(f"Seeded {len(documents)} DPDP knowledge chunks into Chroma")


def index_document_text(document_id: str, text: str) -> None:
    """Chunk and index uploaded document text for retrieval."""
    collection = _get_document_collection()

    # Remove prior chunks for this document (re-upload / re-analysis)
    existing = collection.get(where={"document_id": document_id})
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    chunks = _chunk_text(text)
    if not chunks:
        logger.warning(f"No chunks to index for document {document_id}")
        return

    ids = [f"{document_id}-{i}" for i in range(len(chunks))]
    metadatas = [{"document_id": document_id, "chunk_index": i} for i in range(len(chunks))]
    embeddings = embed_texts(chunks)

    collection.add(
        ids=ids,
        documents=chunks,
        metadatas=metadatas,
        embeddings=embeddings,
    )
    logger.info(f"Indexed {len(chunks)} chunks for document {document_id}")


def query_dpdp_context(query: str, n_results: int | None = None) -> str:
    """Retrieve relevant DPDP Act provisions for a compliance query."""
    n = n_results or settings.RAG_TOP_K_DPDP
    collection = _get_dpdp_collection()
    if collection.count() == 0:
        init_dpdp_knowledge_base()

    query_embedding = embed_texts([query])[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n, collection.count()),
    )
    return _format_results(results)


def query_document_context(document_id: str, query: str, n_results: int | None = None) -> str:
    """Retrieve relevant excerpts from an uploaded document."""
    n = n_results or settings.RAG_TOP_K_DOCUMENT
    collection = _get_document_collection()

    filtered = collection.get(where={"document_id": document_id})
    if not filtered["ids"]:
        return "(No indexed document excerpts available.)"

    query_embedding = embed_texts([query])[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n, len(filtered["ids"])),
        where={"document_id": document_id},
    )
    return _format_results(results)


def _format_results(results: dict[str, Any]) -> str:
    docs = results.get("documents", [[]])[0]
    if not docs:
        return "(No relevant context retrieved.)"
    return "\n\n---\n\n".join(docs)


def clear_document_vectors(document_id: str) -> None:
    """Remove all vector chunks for a single document."""
    collection = _get_document_collection()
    existing = collection.get(where={"document_id": document_id})
    if existing["ids"]:
        collection.delete(ids=existing["ids"])
        logger.info(f"Cleared vector chunks for document {document_id}")


def clear_document_index() -> None:
    """Remove all indexed document chunks (keeps DPDP knowledge base)."""
    client = _get_client()
    try:
        client.delete_collection(DOCUMENT_COLLECTION)
        logger.info("Cleared document vector index")
    except Exception:
        pass


def knowledge_base_fingerprint() -> str:
    """Stable hash to detect knowledge base content changes."""
    parts = [DPDP_COLLECTION, "v2-rules-2025"]
    for key in sorted(DPDP_SECTIONS.keys()):
        section = DPDP_SECTIONS[key]
        parts.append(key + section["section"] + section["title"])
    for rule in COMPLIANCE_RULES:
        parts.append(rule["rule_id"] + rule["description"] + rule["ai_prompt_hint"])
    for rule in DPDP_RULES_2025:
        parts.append(rule["rule_key"] + rule["description"])
    return hashlib.sha256("".join(parts).encode()).hexdigest()[:16]
