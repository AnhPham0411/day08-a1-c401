# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Nguyễn Quang Trường
**Vai trò trong nhóm:** Eval Owner B  
**Ngày nộp:** 13/04/2026
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

Vai trò của em là **Eval Owner B**, chịu trách nhiệm chấm điểm RAG pipeline qua bộ grading questions. Công việc chính của em trong Sprint 3-4:

- **Sprint 3**: Cùng Eval Owner A chạy test_questions.json qua 2 variant khác nhau — Baseline (Dense Retrieval) và Variant (Hybrid RRF). Em chạy pipeline đầy đủ với cả hai cấu hình retrieval, thu thập output và mapping vào định dạng scorecard.
- **Sprint 4**: Điền kết quả chi tiết vào `scorecard_baseline.md` và `scorecard_variant.md`, ghi lại 4 metrics chính: Faithfulness, Relevance, Context Recall và Completeness (đối với Variant). Chạy hàm `compare_ab()` để tính Delta và phát hiện những câu hỏi mà Hybrid RRF cải thiện được.
- Công việc của em kết nối trực tiếp với phần của Retrieval Owner (chiến lược hybrid RRF) và LLM Judge (scoring logic). Em là cầu nối giữa ranking strategy và đánh giá kết quả cuối cùng.

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

Em hiểu rõ hơn về **Hybrid Retrieval (Kết hợp Dense + Sparse)** và tầm quan trọng của **A/B Testing trong Evaluation Loop**.

Trước đây em nghĩ Dense retrieval (vector embedding) là "tốt hơn tất cả" vì nó nắm được semantic. Nhưng qua lab này thấy Baseline (Dense only) có Relevance chỉ 80%, tức là 2 câu (gq05, gq07) trả lời sai hoặc irrelevant. Khi gắn Hybrid (Dense + BM25 RRF + Rerank), Relevance tăng lên 100%, Completeness đạt 4.0/5. Điều này chứng minh rằng **Keyword matching (BM25) rất quan trọng cho câu hỏi exact-match**, đặc biệt câu hỏi about P1 SLA, access levels, hay policy details. Dense vector dễ "flexible quá" và miss những keyword cụ thể.

Em cũng học được rằng **evaluation metrics phải đa chiều**: không chỉ nhìn Faithfulness (100% cả 2 bộ test) mà phải xem Relevance, Completeness, Context Recall để thay đổi chiến lược retrieval thực sự có ứng dụng.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

**Khó khăn chính**: Debug pipeline chạy 2 lần (Baseline + Variant) mà output format không consistent. Lần chạy Baseline, LLM trả lời format string bình thường; Variant có ý định gắn thêm metadata (source citation [1], [2]). Ban đầu em cố gắng parse output thủ công, nhưng Variant trả về JSON object trong khi Baseline là plain text. Mất khoảng 30 phút để normalize format trước khi input vào scoring function.

**Ngạc nhiên**: Hai câu hỏi gq05 ("Contractor có thể...") và gq07 ("Phạt bao nhiêu...") đều trả lời "không có đủ dữ liệu" trong cả Baseline lẫn Variant — score Completeness = 0. Ban đầu em nghĩ Hybrid sẽ tìm được context nào đó, nhưng suy ra chúng thực sự không có trong 5 docs nên LLM abstain chính xác. Điều tốt ở chỗ **Hallucination = 0** (Faithfulness = 1 trên cả 2).

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

**Câu hỏi:** gq05 - "Contractor từ bên ngoài công ty có thể được cấp Level 3 access không?"

**Phân tích:**

- **Baseline (Dense)**: Faithfulness = 1 ✓, Relevance = 0 ✗. Câu trả lời: "Tôi không có đủ dữ liệu trong tài liệu nội bộ để trả lời câu hỏi này." Hệ thống trích không được context support, nên phải abstain. Điều này đúng vì access_control_sop.txt không rõ ràng nêu qui tắc explicit "Contractor có được cấp Level 3 không". Do vậy Dense Retrieval miss keyword "contractor" hoặc không ranking sao cho context relevant xuất hiện.

- **Variant (Hybrid)**: Faithfulness = 1 ✓, Relevance = 1 ✓, Completeness = 0. Trả lời: "Tôi không có đủ dữ liệu...". Tuy Relevance được cấp điểm 1 nhưng Completeness = 0 (vì answer chỉ là "không biết" không giải thích thêm). Hybrid RRF tìm được context liên quan (nên Relevance = 1) nhưng context không đủ để sinh ra câu trả lời complete.

- **Delta**: Hybrid cải thiện Relevance từ 0 → 1, nhưng không cải thiện Completeness vì dữ liệu thực sự không có. Điều tốt là system tuân theo **"abstain vs. hallucinate"** — thà trả lời không biết (thật thà) còn hơn bịa ra "có" hoặc "không".

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

**Cải tiến 1**: Thêm **Cross-Encoder Reranking cấu hình ngưỡng động** — eval cho thấy Hybrid RRF tìm được context (Relevance ↑) nhưng Completeness = 4.0/5 ứng với vài câu trả lời hơi GenAI. Tôi muốn test reranker với threshold từ 0.5 → 0.7 để chọn out top-3 candidates thực sự high confidence, rồi eval lại Completeness.

**Cải tiến 2**: **Fine-tune BM25 weights** — gq05 miss vì keyword "contractor" không xuất hiện đủ trong doc. Em muốn experiment với BM25 field weights (title: 3x, body: 1x) hoặc thêm synonym dictionary (contractor → external staff) vào preprocessing, rồi chạy eval lại để kiểm tra Relevance có tăng từ 100% → 100% nhưng với confidence score cao hơn không.
