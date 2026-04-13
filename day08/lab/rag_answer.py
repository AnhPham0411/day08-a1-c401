"""
rag_answer.py — Sprint 2 + Sprint 3: Retrieval & Grounded Answer
=================================================================
Retrieval Owner : retrieve_dense, retrieve_sparse, retrieve_hybrid, rerank
Tech Lead TODO  : call_llm, build_grounded_prompt, rag_answer

Variant chon: Hybrid RRF (dense + BM25)
Ly do: Corpus co ca van ban tu nhien lan keyword/ten cu (P1, Level 3,
       Flash Sale, "Approval Matrix" → "Access Control SOP").
       Dense manh ve ngu nghia, BM25 manh ve exact match.
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# CAU HINH
# =============================================================================

TOP_K_SEARCH = 10   # Search rong
TOP_K_SELECT = 3    # Dua vao prompt

LLM_MODEL = os.getenv("LLM_MODEL", "qwen/qwen3-next-80b-a3b-instruct:free")

# Lazy singletons
_chroma_collection = None
_bm25_index        = None
_bm25_corpus       = None


def _get_collection():
    global _chroma_collection
    if _chroma_collection is None:
        import chromadb
        from index import CHROMA_DB_DIR
        client             = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
        _chroma_collection = client.get_collection("rag_lab")
    return _chroma_collection


def _get_bm25_index():
    """Cache BM25 index tu ChromaDB. Rebuild 1 lan duy nhat."""
    global _bm25_index, _bm25_corpus
    if _bm25_index is None:
        from rank_bm25 import BM25Okapi
        collection = _get_collection()
        all_data   = collection.get(include=["documents", "metadatas"])
        _bm25_corpus = [
            {"text": doc, "metadata": meta}
            for doc, meta in zip(all_data["documents"], all_data["metadatas"])
        ]
        tokenized  = [doc.lower().split() for doc in all_data["documents"]]
        _bm25_index = BM25Okapi(tokenized)
    return _bm25_index, _bm25_corpus


# =============================================================================
# RETRIEVAL — DENSE — Hoàng Tuấn Anh (Retrieval Owner)
# =============================================================================

def retrieve_dense(query: str, top_k: int = TOP_K_SEARCH) -> List[Dict[str, Any]]:
    """
    Embed query → query ChromaDB → tra ve top_k chunk theo cosine similarity.
    score = 1 - distance (ChromaDB dung cosine distance).
    """
    from index import get_embedding

    collection      = _get_collection()
    query_embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "text":     doc,
            "metadata": meta,
            "score":    round(1.0 - dist, 4),
        })
    return chunks


# =============================================================================
# RETRIEVAL — SPARSE / BM25 — Hoàng Tuấn Anh (Retrieval Owner)
# Sprint 3 — dung trong hybrid
# =============================================================================

def retrieve_sparse(query: str, top_k: int = TOP_K_SEARCH) -> List[Dict[str, Any]]:
    """
    BM25 keyword search.
    Manh o: exact term, ma loi, ten rieng (P1, Level 3, Flash Sale, ERR-403).
    """
    bm25, corpus = _get_bm25_index()

    scores      = bm25.get_scores(query.lower().split())
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

    return [
        {
            "text":     corpus[idx]["text"],
            "metadata": corpus[idx]["metadata"],
            "score":    float(scores[idx]),
        }
        for idx in top_indices if scores[idx] > 0
    ]


# =============================================================================
# RETRIEVAL — HYBRID RRF — Hoàng Tuấn Anh (Retrieval Owner)
# Sprint 3 variant chinh
# =============================================================================

def retrieve_hybrid(
    query: str,
    top_k: int           = TOP_K_SEARCH,
    dense_weight: float  = 0.8, # ban đầu để là 0.6 nhưng test phát hiện "SLA P1" bị abstain sai
    sparse_weight: float = 0.2,
) -> List[Dict[str, Any]]:
    """
    Ket hop dense va BM25 bang Reciprocal Rank Fusion (RRF).

    RRF_score(d) = dense_weight  * 1/(60 + dense_rank)
                 + sparse_weight * 1/(60 + sparse_rank)

    Hang so 60: gia tri tieu chuan RRF (Cormack et al., 2009).
    dense_weight=0.6: corpus chu yeu van ban tu nhien → dense chiem uu the.
    sparse_weight=0.4: BM25 xu ly duoc alias va keyword chinh xac.
    """
    RRF_K = 60

    dense_results  = retrieve_dense(query, top_k=top_k)
    sparse_results = retrieve_sparse(query, top_k=top_k)

    rrf_scores: Dict[str, float] = {}
    doc_map:    Dict[str, Dict]  = {}

    for rank, chunk in enumerate(dense_results):
        key = chunk["text"]
        rrf_scores[key]  = rrf_scores.get(key, 0.0) + dense_weight * (1.0 / (RRF_K + rank + 1))
        doc_map[key]     = chunk

    for rank, chunk in enumerate(sparse_results):
        key = chunk["text"]
        rrf_scores[key]  = rrf_scores.get(key, 0.0) + sparse_weight * (1.0 / (RRF_K + rank + 1))
        doc_map.setdefault(key, chunk)

    sorted_keys = sorted(rrf_scores, key=rrf_scores.__getitem__, reverse=True)[:top_k]
    return [
        {**doc_map[k], "score": round(rrf_scores[k], 6)}
        for k in sorted_keys
    ]


# =============================================================================
# RERANK — Hoàng Tuấn Anh (Retrieval Owner) 
# =============================================================================

def rerank(
    query: str,
    candidates: List[Dict[str, Any]],
    top_k: int = TOP_K_SELECT,
) -> List[Dict[str, Any]]:
    """
    Cross-encoder rerank: chuc nang phu sau hybrid.
    Funnel: search rong (top-10) → rerank → top-3 vao prompt.
    """
    try:
        from sentence_transformers import CrossEncoder
        model  = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        scores = model.predict([[query, c["text"]] for c in candidates])
        ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
        return [c for c, _ in ranked[:top_k]]
    except ImportError:
        print("[rerank] Chua cai sentence-transformers → fallback top-k")
        return candidates[:top_k]


# =============================================================================
# GENERATION — Tech Lead TODO
# =============================================================================

def build_context_block(chunks: List[Dict[str, Any]]) -> str:
    """
    Dong goi chunks thanh context block voi so thu tu [1], [2], ...
    Ham nay dung chung, khong thuoc rieng ai.
    """
    parts = []
    for i, chunk in enumerate(chunks, 1):
        meta     = chunk.get("metadata", {})
        source   = meta.get("source", "unknown")
        section  = meta.get("section", "")
        eff_date = meta.get("effective_date", "")
        score    = chunk.get("score", 0)
        text     = chunk.get("text", "")

        header = f"[{i}] {source}"
        if section:   header += f" | {section}"
        if eff_date:  header += f" | effective: {eff_date}"
        if score > 0: header += f" | score={score:.4f}"

        parts.append(f"{header}\n{text}")
    return "\n\n".join(parts)
def build_grounded_prompt(query: str, context_block: str) -> str:
    return f"""Bạn là trợ lý nội bộ chuyên trả lời dựa trên tài liệu công ty.
Nhiệm vụ của bạn là tổng hợp thông tin từ Context bên dưới và trả lời câu hỏi một cách chính xác, ngắn gọn, có trích dẫn.

════════════════════════════════════
NGUYÊN TẮC BẮT BUỘC
════════════════════════════════════

[GROUNDING]
- Chỉ sử dụng thông tin xuất hiện trong Context.
- Được phép tổng hợp từ nhiều đoạn Context để suy ra câu trả lời,
  nhưng phải trích dẫn đầy đủ các đoạn đã dùng [1][2].
- Nếu câu hỏi hỏi về điều kiện/quy trình, hãy tổng hợp
  từ TẤT CẢ các đoạn Context liên quan, không chỉ đoạn
  đề cập trực tiếp. Trích dẫn đầy đủ [1][2][3].
- Nếu tài liệu quy định phạm vi áp dụng (ai được áp dụng)
  ở một đoạn và điều kiện cụ thể ở đoạn khác, hãy kết hợp
  cả hai để trả lời.
- Tuyệt đối KHÔNG dùng kiến thức ngoài Context.
- Cấm bịa đặt: con số, tên người, ngày tháng, mã lỗi,
  cấp độ, quy trình, chính sách — nếu không có trong Context.

[ABSTAIN]
Nếu Context không chứa đủ thông tin để trả lời, trả lời chính xác câu sau:
  "Tôi không có đủ dữ liệu trong tài liệu nội bộ để trả lời câu hỏi này."

[TRÍCH DẪN]
- Sau mỗi thông tin sử dụng, ghi số thứ tự [N] của đoạn Context ngay liền sau.
  Ví dụ: "SLA xử lý ticket P1 là 4 giờ [1]."
- Nếu tổng hợp từ nhiều đoạn, liệt kê tất cả: [1][3].

[ĐỘ CHÍNH XÁC]
- Giữ nguyên con số, đơn vị, điều kiện đúng như trong Context.
  Ví dụ: "trong vòng 30 ngày kể từ ngày mua" ≠ "khoảng 1 tháng".

[MÂU THUẪN GIỮA CÁC ĐOẠN]
Nếu hai đoạn Context mâu thuẫn nhau:
  1. Nêu cả hai phiên bản kèm trích dẫn [N].
  2. Ưu tiên đoạn có effective_date mới hơn nếu có.
  3. Khuyến nghị người dùng xác nhận lại với bộ phận phụ trách.

[ĐỊNH DẠNG]
- Trả lời bằng tiếng Việt.
- Dùng danh sách có dấu đầu dòng khi liệt kê từ 3 mục trở lên.
- In đậm các giá trị quan trọng: số liệu, tên chính sách, mã lỗi.
- Không thêm lời chào, lời cảm ơn — đi thẳng vào nội dung.

════════════════════════════════════
Context (tài liệu nội bộ đã được truy xuất):
════════════════════════════════════
{context_block}

════════════════════════════════════
Câu hỏi: {query}
════════════════════════════════════

Trả lời:"""


# Lazy singleton LLM client
_llm_client = None

def call_llm(prompt: str) -> str:
    """
    (Tech Lead): Goi LLM (OpenAI) de sinh cau tra loi voi temperature=0.
    """
    global _llm_client
    if _llm_client is None:
        from openai import OpenAI
        _llm_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = _llm_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=512,
    )
    return response.choices[0].message.content.strip()


def rag_answer(
    query: str,
    retrieval_mode: str = "hybrid",
    top_k_search: int   = TOP_K_SEARCH,
    top_k_select: int   = TOP_K_SELECT,
    use_rerank: bool    = False,
    verbose: bool       = False,
) -> Dict[str, Any]:
    """
    (Tech Lead): Ghép các bước thành RAG pipeline hoàn chỉnh.
    """
    # Bước 1: Retrieve
    if retrieval_mode == "dense":
        candidates = retrieve_dense(query, top_k=top_k_search)
    elif retrieval_mode == "sparse":
        candidates = retrieve_sparse(query, top_k=top_k_search)
    else:  # default hybrid
        candidates = retrieve_hybrid(query, top_k=top_k_search)

    # Bước 2: Rerank (optional)
    if use_rerank:
        candidates = rerank(query, candidates, top_k=top_k_select)
    else:
        candidates = candidates[:top_k_select]

    # Bước 3: Build grounded prompt
    context_block = build_context_block(candidates)
    prompt        = build_grounded_prompt(query, context_block)

    if verbose:
        print(f"\n--- PROMPT ---\n{prompt}\n--------------")

    # Bước 4: Generate
    answer = call_llm(prompt)

    # Bước 5: Kết quả
    sources = list({c["metadata"].get("source", "unknown") for c in candidates})
    return {
        "query":       query,
        "answer":      answer,
        "sources":     sources,
        "chunks_used": candidates,
        "config": {
            "retrieval_mode": retrieval_mode,
            "top_k_search":   top_k_search,
            "top_k_select":   top_k_select,
            "use_rerank":     use_rerank,
        },
    }


# =============================================================================
# SPRINT 3: SO SANH BASELINE VS VARIANT — Hoàng Tuấn Anh (Retrieval Owner)
# =============================================================================

def compare_retrieval_strategies(query: str) -> None:
    """
    So sanh dense (baseline) vs hybrid (variant) voi cung query.
    Chi thay doi retrieval_mode, giu nguyen cac tham so khac → dung A/B rule.
    Dung de dien vao docs/tuning-log.md.
    """
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print('='*60)

    configs = [
        ("dense",  False, "Baseline — Dense only"),
        ("hybrid", False, "Variant  — Hybrid RRF"),
        ("hybrid", True,  "Variant  — Hybrid + Rerank"),
    ]

    for mode, use_rr, label in configs:
        print(f"\n--- {label} ---")
        try:
            result = rag_answer(query, retrieval_mode=mode, use_rerank=use_rr, verbose=False)
            print(f"Answer:  {result['answer']}")
            print(f"Sources: {result['sources']}")
            for i, c in enumerate(result["chunks_used"], 1):
                print(f"  [{i}] score={c.get('score', 0):.4f} | {c['metadata'].get('source', '?')}")
        except NotImplementedError as e:
            print(f"Tech Lead chua implement: {e}")
        except Exception as e:
            print(f"Loi: {type(e).__name__}: {e}")


def score_context_recall(
    query: str,
    expected_source: str,
    retrieval_mode: str = "hybrid",
) -> bool:
    """
    Kiem tra expected_source co duoc retrieve khong.
    Dung trong debug tree: False → loi o tang retrieval.
    """
    if retrieval_mode == "dense":
        candidates = retrieve_dense(query, top_k=TOP_K_SEARCH)
    else:
        candidates = retrieve_hybrid(query, top_k=TOP_K_SEARCH)
    retrieved = [c["metadata"].get("source", "") for c in candidates]
    return any(expected_source in s for s in retrieved)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Sprint 2+3 — Retrieval Owner: verify retrieval quality")
    print("=" * 60)

    # Đã implement rag_answer(), chạy test:
    test_queries = [
        "SLA xu ly ticket P1 la bao lau?",
        "Khach hang co the yeu cau hoan tien trong bao nhieu ngay?",
        "Ai phai phe duyet de cap quyen Level 3?",
        "ERR-403-AUTH la loi gi?",   # Kiem tra abstain
    ]

    print("\n--- TEST RAG_ANSWER (Sprint 2) ---")
    for q in test_queries:
        print(f"\n[Q]: {q}")
        res = rag_answer(q, retrieval_mode="hybrid")
        print(f"[A]: {res['answer']}")

    print("\n--- CHAY COMPARE_RETRIEVAL_STRATEGIES (Sprint 3) ---")
    compare_retrieval_strategies('SLA xu ly ticket P1 la bao lau?')
    compare_retrieval_strategies('Approval Matrix la tai lieu nao?')