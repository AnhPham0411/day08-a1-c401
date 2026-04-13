"""
index.py — Sprint 1: Build RAG Index
=====================================
Retrieval Owner : preprocess_document, chunk_document, _split_by_size
Tech Lead TODO  : get_embedding, build_index (phần embed + upsert)
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# CẤU HÌNH
# =============================================================================

DOCS_DIR      = Path(__file__).parent / "data" / "docs"
CHROMA_DB_DIR = Path(__file__).parent / "chroma_db"

CHUNK_SIZE    = 400   # token ≈ 1600 ky tu
CHUNK_OVERLAP = 80    # token ≈ 320 ky tu


# =============================================================================
# STEP 1: PREPROCESS — Hoàng Tuấn Anh (Retrieval Owner)
# =============================================================================

def preprocess_document(raw_text: str, filepath: str) -> Dict[str, Any]:
    """
    Trich xuat metadata tu header bang regex.
    Giu lai dong 'Ghi chu' (alias ten cu) vao content — quan trong cho retrieval.
    Vi du: "Approval Matrix" la ten cu cua "Access Control SOP".
    """
    metadata = {
        "source":         filepath,
        "section":        "",
        "department":     "unknown",
        "effective_date": "unknown",
        "access":         "internal",
    }

    field_patterns = {
        "source":         r"^Source:\s*(.+)$",
        "department":     r"^Department:\s*(.+)$",
        "effective_date": r"^Effective Date:\s*(.+)$",
        "access":         r"^Access:\s*(.+)$",
    }

    lines          = raw_text.strip().split("\n")
    preamble_extra = []   # dong khong phai metadata, khong phai tieu de (vi du: Ghi chu)
    content_lines  = []
    header_done    = False

    for line in lines:
        if not header_done:
            stripped = line.strip()

            # Gap section marker === → ket thuc header
            if re.match(r"^===", stripped):
                header_done = True
                content_lines.extend(preamble_extra)
                content_lines.append(line)
                continue

            # Thu match tung truong metadata
            matched = False
            for field, pattern in field_patterns.items():
                m = re.match(pattern, stripped)
                if m:
                    metadata[field] = m.group(1).strip()
                    matched = True
                    break

            # Khong phai metadata, khong trang, khong toan chu hoa → giu lai
            if not matched and stripped and not stripped.isupper():
                preamble_extra.append(line)
        else:
            content_lines.append(line)

    cleaned = "\n".join(content_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()

    return {"text": cleaned, "metadata": metadata}


# =============================================================================
# STEP 2: CHUNK —  Hoàng Tuấn Anh (Retrieval Owner)
# =============================================================================

def chunk_document(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Split theo section heading (=== ... ===).
    Section qua dai → _split_by_size theo paragraph voi overlap.
    Moi chunk giu day du metadata goc + truong 'section'.
    """
    text          = doc["text"]
    base_metadata = doc["metadata"].copy()
    chunks        = []

    parts                = re.split(r"(===.*?===)", text)
    current_section      = "General"
    current_section_text = ""

    for part in parts:
        if re.match(r"===.*?===", part):
            if current_section_text.strip():
                chunks.extend(_split_by_size(
                    current_section_text.strip(),
                    base_metadata=base_metadata,
                    section=current_section,
                ))
            current_section      = part.strip("= ").strip()
            current_section_text = ""
        else:
            current_section_text += part

    if current_section_text.strip():
        chunks.extend(_split_by_size(
            current_section_text.strip(),
            base_metadata=base_metadata,
            section=current_section,
        ))

    return chunks



# _split_by_size() Hoàng Tuấn Anh (Retrieval Owner)
def _split_by_size(
    text: str,
    base_metadata: Dict,
    section: str,
    chunk_chars: int   = CHUNK_SIZE    * 4,   # 1600 ky tu
    overlap_chars: int = CHUNK_OVERLAP * 4,   # 320 ky tu
) -> List[Dict[str, Any]]:
    """
    Split theo paragraph (\n\n) voi overlap.
    - Uu tien cat tai ranh gioi paragraph tu nhien, khong cat giua cau.
    - Overlap: giu cac paragraph cuoi cua chunk truoc vao dau chunk tiep theo.
    """
    if len(text) <= chunk_chars:
        return [{"text": text, "metadata": {**base_metadata, "section": section}}]

    paragraphs    = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks        = []
    current_parts = []
    current_len   = 0

    def flush_chunk():
        nonlocal current_parts, current_len
        chunks.append({
            "text":     "\n\n".join(current_parts),
            "metadata": {**base_metadata, "section": section},
        })
        # Giu lai cac paragraph cuoi lam overlap
        overlap_parts = []
        overlap_len   = 0
        for p in reversed(current_parts):
            overlap_len += len(p) + 2
            overlap_parts.insert(0, p)
            if overlap_len >= overlap_chars:
                break
        current_parts = overlap_parts
        current_len   = sum(len(p) + 2 for p in current_parts)

    for para in paragraphs:
        add_len = len(para) + (2 if current_parts else 0)
        if current_len + add_len > chunk_chars and current_parts:
            flush_chunk()
        current_parts.append(para)
        current_len += len(para) + 2

    if current_parts:
        chunks.append({
            "text":     "\n\n".join(current_parts),
            "metadata": {**base_metadata, "section": section},
        })

    return chunks or [{"text": text, "metadata": {**base_metadata, "section": section}}]


# =============================================================================
# STEP 3: EMBED + STORE — Tech Lead TODO
# =============================================================================

# Lazy singleton client
_openai_client = None

def get_embedding(text: str) -> List[float]:
    """
    (Tech Lead): Tao embedding vector cho text bang OpenAI text-embedding-3-small.
    """
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        _openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Cleanup text (remove newlines cache issues)
    text = text.replace("\n", " ")
    response = _openai_client.embeddings.create(input=[text], model="text-embedding-3-small")
    return response.data[0].embedding


def build_index(docs_dir: Path = DOCS_DIR, db_dir: Path = CHROMA_DB_DIR) -> None:
    """
    (Tech Lead): Implement phan embed + upsert vao ChromaDB.
    """
    import chromadb
    db_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(db_dir))

    try:
        # Xoa du lieu cu de index moi tu dau
        client.delete_collection("rag_lab")
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name="rag_lab",
        metadata={"hnsw:space": "cosine"}
    )

    doc_files = list(docs_dir.glob("*.txt"))
    if not doc_files:
        print(f"Khong tim thay .txt trong {docs_dir}")
        return

    print(f"Starting indexing for {len(doc_files)} docs...")
    for filepath in doc_files:
        raw    = filepath.read_text(encoding="utf-8")
        doc    = preprocess_document(raw, str(filepath))
        chunks = chunk_document(doc)

        if not chunks:
            continue

        ids        = [f"{filepath.stem}_{i:03d}" for i in range(len(chunks))]
        embeddings = [get_embedding(c["text"]) for c in chunks]
        documents  = [c["text"]     for c in chunks]
        metadatas  = [c["metadata"] for c in chunks]

        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        print(f"  {filepath.name}: {len(chunks)} chunks indexed")

    print("\nDONE: Indexing completed.")


# =============================================================================
# STEP 4: INSPECT
# =============================================================================

def list_chunks(db_dir: Path = CHROMA_DB_DIR, n: int = 5) -> None:
    try:
        import chromadb
        client     = chromadb.PersistentClient(path=str(db_dir))
        collection = client.get_collection("rag_lab")
        results    = collection.get(limit=n, include=["documents", "metadatas"])
        print(f"\n=== Top {n} chunks ===")
        for i, (doc, meta) in enumerate(zip(results["documents"], results["metadatas"])):
            print(f"[{i+1}] {meta.get('source')} | {meta.get('section')} | date={meta.get('effective_date')}")
            print(f"     {doc[:150]}...")
    except Exception as e:
        print(f"Loi: {e} — Chay build_index() truoc.")


def inspect_metadata_coverage(db_dir: Path = CHROMA_DB_DIR) -> None:
    try:
        import chromadb
        client     = chromadb.PersistentClient(path=str(db_dir))
        collection = client.get_collection("rag_lab")
        results    = collection.get(include=["metadatas"])
        print(f"Tong chunks: {len(results['metadatas'])}")
        departments = {}
        missing     = 0
        for meta in results["metadatas"]:
            dept = meta.get("department", "unknown")
            departments[dept] = departments.get(dept, 0) + 1
            if meta.get("effective_date") in ("unknown", "", None):
                missing += 1
        for dept, cnt in sorted(departments.items()):
            print(f"  {dept}: {cnt} chunks")
        print(f"Thieu effective_date: {missing}")
    except Exception as e:
        print(f"Loi: {e}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Sprint 1 — Retrieval Owner: verify chunk quality")
    print("=" * 60)

    doc_files = list(DOCS_DIR.glob("*.txt"))
    print(f"Tim thay {len(doc_files)} tai lieu\n")

    for filepath in doc_files:
        raw    = filepath.read_text(encoding="utf-8")
        doc    = preprocess_document(raw, str(filepath))
        chunks = chunk_document(doc)
        print(f"{filepath.name}: {len(chunks)} chunks | effective_date={doc['metadata']['effective_date']}")
        for i, c in enumerate(chunks[:2]):
            print(f"  [chunk {i+1}] section={c['metadata']['section']!r} | {len(c['text'])} ky tu")
            print(f"  preview: {c['text'][:100].strip()}...")
        print()

    build_index()
    list_chunks()
    inspect_metadata_coverage()