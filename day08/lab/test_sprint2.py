"""
test_sprint2.py — Chạy lại 4 câu test Sprint 2
So sánh dense (baseline) vs hybrid (variant) trên cùng câu hỏi
"""
from rag_answer import rag_answer

TEST_QUERIES = [
    "SLA xử lý ticket P1 là bao lâu?",
    "Khách hàng có thể yêu cầu hoàn tiền trong bao nhiêu ngày?",
    "Ai phải phê duyệt để cấp quyền Level 3?",
    "ERR-403-AUTH là lỗi gì?",  # Câu không có trong docs → phải abstain
]

def run_test(mode: str):
    print(f"\n{'='*60}")
    print(f"MODE: {mode.upper()}")
    print('='*60)
    for q in TEST_QUERIES:
        print(f"\n[Q]: {q}")
        result = rag_answer(q, retrieval_mode=mode, verbose=False)
        print(f"[A]: {result['answer']}")
        print(f"[Sources]: {result['sources']}")

if __name__ == "__main__":
    run_test("dense")   # Baseline
    run_test("hybrid")  # Variant — so sánh xem delta ở đâu