# 📋 Running Guide — eval.py (Sprint 4)

> **Mục đích:** Chạy evaluation pipeline để tạo scorecard baseline vs variant, so sánh A/B, và ghi kết quả vào tuning-log.md

---

## Quick Start

### 1. Chuẩn bị

```bash
# Cài dependencies (nếu chưa)
pip install -r requirements.txt

# Từ shell, chạy từ thư mục day08/lab/
cd day08/lab
```

### 2. Chạy Full Evaluation (Baseline + Variant + A/B Comparison)

```bash
python eval.py
```

**Cái gì sẽ xảy ra:**
1. ✅ Chạy pipeline baseline (dense retrieval) trên 10 test questions
2. ✅ Chạy pipeline variant (hybrid RRF retrieval) trên 10 test questions
3. ✅ Chấm điểm từng câu trả lời (4 metrics):
   - **Faithfulness** — Có bịa sổ liệu hay không? (LLM-as-Judge hoặc manual)
   - **Answer Relevance** — Có trả lời đúng câu hỏi không?
   - **Completeness** — Câu trả lời có đủ thông tin không?
   - **Context Recall** — Expected source có được retrieve không?
   
   Format: Tất cả scores được convert sang **/5 scale**
4. ✅ So sánh delta (Baseline vs Variant)
5. ✅ Xuất kết quả ra:
   - `results/scorecard_baseline.md`
   - `results/scorecard_variant.md`
   - `logs/grading_run_baseline.json`
   - `logs/grading_run_variant.json`
   - Append vào `docs/tuning-log.md`

---

## 3. Chạy Riêng Baseline hoặc Variant

### Chỉ Baseline

```bash
python eval.py --mode baseline
```

**Output:**
- `results/scorecard_baseline.md`
- `logs/grading_run_baseline.json`

### Chỉ Variant

```bash
python eval.py --mode variant
```

**Output:**
- `results/scorecard_variant.md`
- `logs/grading_run_variant.json`

---

## 4. Chế Độ Chấm Điểm

### A. LLM-as-Judge (Tự động) — **Khuyến nghị**

**Điều kiện:** Có `OPENAI_API_KEY` hoặc `GOOGLE_API_KEY` trong `.env`

```bash
python eval.py
```

**Cách hoạt động:**
- Script tự động gọi OpenAI GPT-4o-mini để chấm từng câu
- Faithfulness: Kiểm tra có hallucination không
- Relevance: Kiểm tra câu trả lời có trả lời đúng vấn đề không

### B. Manual Scoring (Tay) — Khi không có API key

**Nếu không có API key:**
```bash
python eval.py
```

Script sẽ tự động chuyển sang chế độ manual:
```
Khong co API key → chuyen sang cham thu cong

=== Cham thu cong (nhap 1=dat / 0=khong dat) ===

[q01] SLA xử lý ticket P1 là bao lâu?
Expected: Ticket P1 có SLA phản hồi ban đầu 15 phút và thời gian xử lý (resolution) là 4 giờ.
Got:  [Câu trả lời từ RAG]
  Faithfulness (1/0): 1
  Relevance    (1/0): 1

[q02] ...
```

**Hướng dẫn chấm:**
- **1 (Đạt)** = câu trả lời tốt theo tiêu chí
- **0 (Không đạt)** = câu trả lời xấu hoặc thiếu

---

## 5. Output Chi Tiết

### 5.1 Scorecard Markdown (`results/scorecard_*.md`)

```markdown
# Scorecard — Baseline (Dense)

**Retrieval mode:** `dense`  
**N questions:** 10  
**Timestamp:** 2026-04-13 16:13

## Tong ket metrics

| Metric         | Score |
| -------------- | ----- |
| Faithfulness   | 80.0% |
| Relevance      | 70.0% |
| Context Recall | 60.0% |

## Chi tiet tung cau

| ID  | Question               | Faithful | Relevant | Recall | Answer preview           |
| --- | ---------------------- | -------- | -------- | ------ | ------------------------ |
| q01 | SLA xử lý ticket P1... | 1        | 1        | ✓      | Ticket P1 có SLA phản... |
| q02 | Khách hàng có thể...   | 1        | 0        | ✓      | Khách hàng có thể yêu... |
...
```

**Cách dùng:** copy nội dung vào `reports/` hoặc ghi vào tuning-log.md

### 5.2 Grading Log JSON (`logs/grading_run_*.json`)

Full details mỗi câu hỏi (cho debug):

```json
[
  {
    "id": "q01",
    "question": "SLA xử lý ticket P1 là bao lâu?",
    "expected_answer": "Ticket P1 có SLA phản hồi ban đầu 15 phút và thời gian xử lý (resolution) là 4 giờ.",
    "expected_sources": ["support/sla-p1-2026.pdf"],
    "answer": "Ticket P1 có SLA phản hồi ban đầu 15 phút và thời gian xử lý (resolution) là 4 giờ.",
    "sources": ["sla_p1_2026.txt"],
    "chunks_retrieved": 3,
    "faithfulness": 1,
    "relevance": 1,
    "context_recall": true,
    "timestamp": "2026-04-13T16:13:00.123456"
  },
  ...
]
```

### 5.3 Tuning Log (`docs/tuning-log.md`)

Append A/B comparison:

```markdown
## A/B Comparison — 2026-04-13

**Baseline:** Baseline (Dense) (dense)
**Variant:** Variant (Hybrid RRF) (hybrid)

**Scorecard Comparison:**

| Metric         | Baseline | Variant | Delta  |
| -------------- | -------- | ------- | ------ |
| faithfulness   | 80.0%    | 85.0%   | +5.0%  |
| relevance      | 70.0%    | 75.0%   | +5.0%  |
| context_recall | 60.0%    | 80.0%   | +20.0% |

**Kết luận:**
Variant tốt hơn ở faithfulness (+5.0%)
Variant tốt hơn ở relevance (+5.0%)
Variant tốt hơn ở context_recall (+20.0%)

---
```

---

## 6. Troubleshooting

### ❌ "Khong tim thay data/test_questions.json"

**Nguyên nhân:** File test_questions.json không tồn tại

**Fix:**
```bash
# Copy từ root data/
cp ../../../data/test_questions.json data/
```

### ❌ "PIPELINE_ERROR: Error code: 429"

**Nguyên nhân:** Rate limit từ OpenAI API hoặc chroma collection chưa được build

**Fix:**
1. Chạy `python index.py` trước để build chroma collection
2. Đợi vài phút rồi chạy lại
3. Hoặc kiểm tra `OPENAI_API_KEY` có đúng không

### ❌ "Loi: ModuleNotFoundError: No module named 'rag_answer'"

**Nguyên nhân:** Chạy từ sai thư mục

**Fix:**
```bash
cd day08/lab
python eval.py  # Chạy từ thư mục này
```

### ❌ "PIPELINE_ERROR: LLM time out"

**Nguyên nhân:** API chậm

**Workaround:** Chạy manual scoring thay vì LLM judge:
- Xóa `OPENAI_API_KEY` từ `.env`
- Chạy `python eval.py`

---

## 7. Expected Results Format

Khi chạy thành công, từng câu hỏi sẽ in như::

```
[1/10] q01: SLA xử lý ticket P1 là bao lâu?...

  Answer:  Ticket P1 có SLA phản hồi ban đầu 15 phút và thời gian xử lý (resolution) là 4 giờ....
  Sources: ['sla_p1_2026.txt']
  Context Recall: PASS
```

Cuối cùng:

```
==============================================================
A/B COMPARISON
  Baseline : Baseline (Dense) (dense)
  Variant  : Variant (Hybrid RRF) (hybrid)

Metric               Baseline    Variant       Delta Ket luan
--------------------------------------------------------------
faithfulness            80.0%       85.0%      +5.0% BETTER ↑
relevance               70.0%       75.0%      +5.0% BETTER ↑
context_recall          60.0%       80.0%     +20.0% BETTER ↑
==============================================================
```

---

## 8. Sửa Thay đổi Thay đổi Config A/B

Để so sánh retrieval strategy khác:

**Edit:** [eval.py](eval.py#L35-L44)

```python
BASELINE_CONFIG = {
    "retrieval_mode": "dense",      # ← Thay từ đây
    "top_k_search":   10,
    "top_k_select":   3,
    "use_rerank":     False,
}

VARIANT_CONFIG = {
    "retrieval_mode": "hybrid",     # ← Hoặc từ đây
    "top_k_search":   10,
    "top_k_select":   3,
    "use_rerank":     False,
}
```

**Ví dụ:** Thay variant thành hybrid + rerank:
```python
VARIANT_CONFIG = {
    "retrieval_mode": "hybrid",
    "top_k_search":   10,
    "top_k_select":   3,
    "use_rerank":     True,         # ← Có rerank
}
```

Rồi chạy:
```bash
python eval.py --mode variant
```

---

## 9. Copy Kết Quả vào tuning-log.md

**eval.py tự động append**, nhưng nếu muốn copy tay:

1. Chạy eval.py (tạo scorecard files)
2. Mở `docs/tuning-log.md`
3. Scroll xuống dưới cùng
4. Xem A/B Comparison print ra lúc chạy
5. Copy vào markdown table

---

## Tóm Tắt Workflow

```
1. python eval.py
   ↓
2. [Tự động] Chạy baseline → scorecard_baseline.md
   (Nếu cần chấm tay: nhập 1 hoặc 0 cho mỗi câu)
   ↓
3. [Tự động] Chạy variant → scorecard_variant.md
   ↓
4. [Tự động] So sánh A/B
   ↓
5. [Tự động] Append vào docs/tuning-log.md
   ↓
6. ✅ Hoàn tất! Kết quả sẵn sàng ghi vào reports/
```

---

**Câu hỏi? Gặp lỗi?** → Xem `eval.py` header hoặc mục Troubleshooting trên.
