# Tuning Log — RAG Pipeline (Day 08 Lab)

> A/B Rule: Chỉ đổi MỘT biến mỗi lần.
> Đổi đồng thời chunking + hybrid + rerank + prompt thì không biết biến nào tạo cải thiện.

---

## Baseline (Sprint 2)

**Ngày:** 2026-04-13
**Config:**

```
retrieval_mode = "dense"
chunk_size     = 400 tokens (~1600 ký tự)
overlap        = 80 tokens  (~320 ký tự)
top_k_search   = 10
top_k_select   = 3
use_rerank     = False
llm_model      = gpt-4o-mini
temperature    = 0
```

**Scorecard Baseline:**

| Metric           | Average Score |
|------------------|--------------|
| Faithfulness     | TODO — chạy eval.py |
| Answer Relevance | TODO — chạy eval.py |
| Context Recall   | TODO — chạy eval.py |

**Quan sát định tính (trước eval.py):**

Chạy 4 câu test thủ công:

| Câu hỏi | Kết quả | Đánh giá |
|---------|---------|----------|
| SLA xử lý ticket P1 là bao lâu? | 4 giờ [2] | ✓ Đúng |
| Khách hàng hoàn tiền trong bao nhiêu ngày? | 7 ngày làm việc [1] | ✓ Đúng |
| Ai phê duyệt cấp quyền Level 3? | Line Manager + IT Admin + IT Security [1] | ✓ Đúng |
| ERR-403-AUTH là lỗi gì? | "Tôi không có đủ dữ liệu..." | ✓ Abstain đúng |

**Câu hỏi yếu nhất (giả thuyết trước eval):**
> Chưa có số liệu chính thức. Quan sát thủ công cho thấy baseline dense
> hoạt động tốt trên 4 câu mẫu. Điểm yếu dự kiến ở các câu multi-hop
> hoặc câu hỏi có alias/tên cũ.

**Giả thuyết nguyên nhân (Error Tree):**

- [ ] Indexing: Chunking cắt giữa điều khoản
- [ ] Indexing: Metadata thiếu effective_date
- [x] Retrieval: BM25 tokenize tiếng Việt kém → từ ngắn ("xu", "ly", "la")
      xuất hiện rải rác nhiều chunk → sparse score bị nhiễu
- [ ] Retrieval: Top-k quá ít → thiếu evidence
- [ ] Generation: Prompt không đủ grounding
- [ ] Generation: Context quá dài → lost in the middle

---

## Variant 1 — Tăng dense_weight trong RRF (Sprint 3)

**Ngày:** 2026-04-13
**Biến thay đổi duy nhất:** `dense_weight` trong `retrieve_hybrid()` — từ 0.6 lên 0.8

**Lý do chọn biến này:**

Chạy `debug_retrieval.py` với query `"SLA xu ly ticket P1 la bao lau?"` (top_k=20):

```
retrieve_dense()  → rank 1 = Phần 2: SLA theo mức độ ưu tiên (score=0.4899) ✓ ĐÚNG
retrieve_hybrid() → rank 1 = Phần 5: Lịch sử phiên bản                      ✗ SAI
```

Dense retrieve hoàn toàn đúng. Hybrid bị sai vì BM25 tokenize tiếng Việt
theo whitespace — các từ ngắn không mang nghĩa như "xu", "ly", "la", "ticket"
xuất hiện trong rất nhiều chunk không liên quan → BM25 cho chúng score cao
→ RRF với sparse_weight=0.4 đã kéo chunk sai lên top 1.

Giải pháp: tăng tin tưởng vào dense (đã chứng minh đúng), giảm ảnh hưởng BM25.

**Config thay đổi:**

```
dense_weight  = 0.8   # tăng từ 0.6
sparse_weight = 0.2   # giảm từ 0.4
# Tất cả tham số còn lại giữ nguyên
```

**Bằng chứng debug (top 5 của dense, rank đúng):**

```
[1] score=0.4899 | Phần 2: SLA theo mức độ ưu tiên    ← ĐÚNG, cần lấy chunk này
[2] score=0.4421 | Phần 4: Công cụ và kênh liên lạc
[3] score=0.4370 | Phần 5: Lịch sử phiên bản
[4] score=0.4146 | Điều 4: Quy trình xử lý hoàn tiền
[5] score=0.3881 | Phần 3: Quy trình xử lý sự cố P1
```

**Scorecard Variant 1:**

| Metric           | Baseline | Variant 1 | Delta |
|------------------|----------|-----------|-------|
| Faithfulness     | TODO     | TODO      | TODO  |
| Answer Relevance | TODO     | TODO      | TODO  |
| Context Recall   | TODO     | TODO      | TODO  |

> Điền sau khi chạy: `python eval.py`

**Nhận xét định tính:**

| Query | Baseline dense | Hybrid 0.6/0.4 | Hybrid 0.8/0.2 (kỳ vọng) |
|-------|---------------|----------------|--------------------------|
| SLA P1 | ✓ 4 giờ [1] | ✗ abstain sai | ✓ Phần 2 lên rank 1 |
| Approval Matrix | ✓ tên cũ [1] | ✓ tên cũ [1] | ✓ không đổi |
| ERR-403-AUTH | ✓ abstain | ✓ abstain | ✓ không đổi |

**Kết luận:**

> TODO — điền sau khi chạy eval.py và có số liệu thực.
> Kỳ vọng: Context Recall tăng vì dense rank 1 không còn bị BM25 đè.
> Faithfulness và Relevance giữ nguyên vì prompt không đổi.

---

## Variant 2 — Hybrid + Rerank (nếu có thời gian)

**Biến thay đổi duy nhất:** `use_rerank = True`

**Lý do:**
> Quan sát từ `compare_retrieval_strategies("Approval Matrix la tai lieu nao?")`:
> Hybrid+Rerank trả lời đầy đủ hơn — nêu cả tên cũ lẫn mô tả mục đích tài liệu.
> Rerank (cross-encoder ms-marco-MiniLM-L-6-v2) chấm lại cặp (query, chunk)
> chính xác hơn bi-encoder → kéo chunk mô tả đầy đủ hơn lên top.

**Config:**

```
retrieval_mode = "hybrid"
dense_weight   = 0.8
sparse_weight  = 0.2
use_rerank     = True    # biến duy nhất thay đổi so với Variant 1
top_k_search   = 10
top_k_select   = 3
```

**Lưu ý:** Rerank chậm hơn đáng kể (~2-3 giây/query do load CrossEncoder).
Không dùng làm config mặc định cho grading_questions vì risk timeout.

**Scorecard Variant 2:**

| Metric           | Baseline | Variant 1 | Variant 2 | Best |
|------------------|----------|-----------|-----------|------|
| Faithfulness     | TODO     | TODO      | TODO      | TODO |
| Answer Relevance | TODO     | TODO      | TODO      | TODO |
| Context Recall   | TODO     | TODO      | TODO      | TODO |

---

## Tóm tắt học được (Sprint 4)

**1. Lỗi phổ biến nhất trong pipeline này là gì?**
> BM25 tokenize tiếng Việt bằng whitespace — không tách được morpheme đúng.
> Từ ngắn phổ biến ("xu", "ly", "la") xuất hiện ở mọi chunk → sparse score nhiễu.
> Fix đơn giản nhất: tăng dense_weight. Fix tốt hơn: dùng underthesea tokenizer.

**2. Biến nào có tác động lớn nhất tới chất lượng?**
> TODO — điền sau eval.py

**3. Nếu có thêm 1 giờ, nhóm sẽ thử gì tiếp theo?**
> Thay whitespace tokenizer của BM25 bằng underthesea để tách đúng
> morpheme tiếng Việt — kỳ vọng sparse recall tăng đáng kể mà không
> cần tăng dense_weight như giải pháp tạm hiện tại.