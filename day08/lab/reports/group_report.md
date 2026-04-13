# Báo Cáo Nhóm — Lab Day 08: Full RAG Pipeline

**Tên nhóm:** ___________  
**Thành viên:**
| Tên | Vai trò | Email |
|-----|---------|-------|
| ___ | Tech Lead | ___ |
| Hoàng Tuấn Anh | Retrieval Owner | stephenhtuananh@gmail.com |
| ___ | Eval Owner A | ___ |
| ___ | Eval Owner B | ___ |
| Đàm Lê Văn Toàn | Documentation Owner | damtoan321@gmail.com |
| ___ | Prompt Engineer & LLM Judge | ___ |

**Ngày nộp:** 2026-04-13  
**Repo:** https://github.com/AnhPham0411/day08-a1-c401

---

## 1. Pipeline nhóm đã xây dựng

**Chunking decision:**
Nhóm dùng `chunk_size=400` tokens (~1600 ký tự) và `overlap=80` tokens, thực hiện tách theo section headers (Heading-based) cho những phần có cấu trúc rõ ràng, rồi mới tiếp tục tách nhỏ qua paragraph. Điều này giúp tránh bị ngắt đoạn câu khiến thiếu hụt ngữ cảnh nhưng vẫn duy trì được độ dài chunk tối ưu.

**Embedding model:**
OpenAI `text-embedding-3-small`.

**Retrieval variant (Sprint 3):**
Nhóm chọn Hybrid Retrieval kết hợp Dense (vector embedding) và Sparse (BM25) thông qua thuật toán Reciprocal Rank Fusion (RRF), bổ sung Cross-Encoder `ms-marco-MiniLM-L-6-v2` ở bước Rerank để tinh chỉnh thứ hạng cuối. Do BM25 mặc định tách token theo khoảng trắng gây nhiễu nặng cho tiếng Việt, nhóm điều chỉnh trọng số về `dense_weight=0.8` và `sparse_weight=0.2` để ngữ nghĩa vẫn chiếm ưu thế.

---

## 2. Quyết định kỹ thuật quan trọng nhất

**Quyết định:** Chuyển từ Dense thuần tuý sang Hybrid RRF với trọng số hiệu chỉnh (`dense_weight=0.8`, `sparse_weight=0.2`).

**Bối cảnh vấn đề:**
BM25 tokenizer mặc định tách dãy từ theo khoảng trắng, khiến các từ tiếng Việt bị rời rạc. Những từ ngắn như *"xu"*, *"ly"*, *"la"*, *"ticket"* xuất hiện rải rác trong gần như toàn bộ corpus, khiến BM25 cho điểm cao đều cho nhiều chunk không liên quan. Với `sparse_weight=0.4` ban đầu, RRF bị kéo lệch đủ để đẩy chunk sai lên rank 1, đè lên dense result đúng.

**Các phương án đã cân nhắc:**

| Phương án | Ưu điểm | Nhược điểm |
|-----------|---------|-----------|
| Dense Retrieval thuần | Tránh hoàn toàn nhiễu từ tách từ sai | Bỏ sót query chứa mã lỗi hoặc danh từ riêng chính xác |
| Thêm `underthesea` tokenizer vào BM25 | Xử lý đúng gốc rễ, tách morpheme tiếng Việt chuẩn | Tốn RAM, thời gian chạy quá lâu cho lab |
| Hybrid RRF với `dense_weight=0.8` | Giữ lợi thế keyword matching, dense vẫn giữ vai trò chính | Cần tuning và đo delta để chọn trọng số phù hợp |

**Phương án đã chọn và lý do:**
Nhóm đặt `sparse_weight=0.2` và `dense_weight=0.8`. Biện pháp này tiết kiệm tài nguyên hệ thống, loại bỏ ảnh hưởng tiêu cực của BM25 tokenizer yếu nhưng vẫn giữ được recall cho các query chứa từ khoá hiếm.

**Bằng chứng từ tuning-log:**
Sau khi debug, chunk sai (`Phần 5: Lịch sử phiên bản`) chiếm rank 1 do BM25 noise đã bị đẩy xuống, và chunk đúng (`Phần 2: SLA theo mức độ ưu tiên`) lên rank 1 sau khi cập nhật trọng số.

---

## 3. Kết quả grading questions

**Ước tính điểm raw:** ~90/98 (dựa trên metrics trung bình của variant).

**Câu tốt nhất:** `gq05` — Cấu hình Dense ban đầu bỏ sót context về Contractor do Chunking Context Break (`top_k_select=3` cắt mất chunk cần thiết ở rank 4). Sau khi tăng `top_k_select` lên 5, Hybrid Variant lấy đủ cả hai chunk và trả lời đúng với Faithful=5, Relevant=5.

**Câu fail:** `gq07` — *"Công ty sẽ phạt bao nhiêu nếu team IT vi phạm cam kết SLA P1?"* Hệ thống trả về Abstain vì tài liệu nội bộ không có thông tin về phạt tài chính. Đây là hành vi đúng — pipeline không hallucinate. Vấn đề nằm ở Generation: câu từ chối chưa hướng dẫn user tìm thông tin ở đâu tiếp theo.

**Câu gq07 (abstain):** Hệ thống trả về: *"Tôi không có đủ dữ liệu trong tài liệu nội bộ để trả lời câu hỏi này."* Hành vi này phản ánh đúng thiết kế Prompt Grounding — hạn chế triệt để hallucination của LLM.

---

## 4. A/B Comparison — Baseline vs Variant

**Biến đã thay đổi (chỉ 1 biến):** Retrieval mode — từ `dense` sang `hybrid` với `dense_weight=0.8`, `sparse_weight=0.2` và Rerank bật.

| Metric | Baseline | Variant | Delta |
|--------|---------|---------|-------|
| Faithfulness | 0.80 | 0.90 | +0.10 |
| Answer Relevance | 0.80 | 0.90 | +0.10 |
| Context Recall | 5.00 | 5.00 | +0.00 |

**Kết luận:**
Variant cải thiện Faithfulness và Answer Relevance 10%. Context Recall đã tốt từ baseline (5.0), Hybrid Variant bù thêm khiếm khuyết keyword matching. Điển hình là `gq05` — thay vì abstain như baseline, variant truy xuất đủ context về Contractor và trả lời hoàn chỉnh.

---

## 5. Phân công và đánh giá nhóm

**Phân công thực tế:**

| Thành viên | Phần đã làm | Sprint |
|------------|-------------|--------|
| ___ (Tech Lead) | Khởi tạo project, setup ChromaDB, `get_embedding()`, kết nối LLM API, hàm `call_llm()`, gắn citation `[1]` vào RAG output. | Sprint 1, 2 |
| Hoàng Tuấn Anh | Thiết kế chunking strategy (`CHUNK_SIZE=400`, `CHUNK_OVERLAP=80`); implement Hybrid Search (Dense + BM25) với RRF; tinh chỉnh `dense_weight=0.8 / sparse_weight=0.2`; tích hợp Cross-Encoder `ms-marco-MiniLM-L-6-v2` vào bước Rerank; debug `eval.py` (fix score overwrite từ `score_with_llm`, fix key `expected_sources`). | Sprint 1, 3, 4 |
| ___ (Eval Owner A) | Thiết kế `test_questions.json` (10 câu, expected answer, expected source); chạy pipeline với grading questions lúc 17:00; xuất `logs/grading_run.json` đúng định dạng trước 18:00. | Sprint 3, 4 |
| ___ (Eval Owner B) | Chạy pipeline cho cả baseline và variant; điền kết quả vào `scorecard_baseline.md` và `scorecard_variant.md`; chạy `compare_ab()`; tổng hợp delta chuyển cho Documentation Owner. | Sprint 3, 4 |
| Đàm Lê Văn Toàn | Viết `architecture.md` (chunking decision, sơ đồ pipeline); viết `tuning-log.md`; kiểm tra format toàn bộ repo trước 18:00; commit `group_report.md` sau 18:00. | Sprint 4, Final |
| ___ (Prompt Engineer) | Thiết kế Prompt chống hallucination (Abstain khi context rỗng, citation `[1][2]`); viết LLM-as-Judge cho các hàm `score_faithfulness`, `score_answer_relevance`, `score_completeness` — output JSON `{"score": int, "notes": "..."}`. | Sprint 2, 4 |

**Điều nhóm làm tốt:**
Phân tách vai trò rõ ràng, mỗi người sở hữu một tầng pipeline độc lập — tránh conflict code khi làm Git. Nhóm tuân thủ A/B Testing nghiêm túc: chỉ thay đổi một biến mỗi lần, đo delta thực tế thay vì phỏng đoán.

**Điều nhóm làm chưa tốt:**
Dependency Python chưa đồng nhất giữa các máy (gây lỗi môi trường Windows). Chưa xử lý được gốc rễ của BM25 tokenizer tiếng Việt — giải pháp `dense_weight=0.8` là tạm thời, không phải triệt để.

---

## 6. Nếu có thêm thời gian, nhóm sẽ làm gì?

**Parent-Child Chunking:** Chia document thành chunk nhỏ (child) để embedding chính xác, nhưng trước khi đưa vào generation sẽ mở rộng ra chunk cha (gấp 2–3 lần) để LLM thấy đủ ngữ cảnh hai chiều. Giải pháp này sẽ cứu được các câu như `gq05` mà không cần tăng `top_k_select`.

**`underthesea` Tokenizer:** Thay thế BM25 whitespace tokenizer bằng NLP tokenizer tiếng Việt chuẩn — cải thiện Sparse Retrieval triệt để thay vì chỉ ép `dense_weight` cao như hiện tại.

**Cải thiện câu Abstain:** Từ điểm fail `gq07`, bổ sung Query Expansion để LLM có thể trả về câu từ chối có hướng dẫn (*"Thông tin này không có trong tài liệu nội bộ — vui lòng liên hệ bộ phận X"*) thay vì chỉ từ chối trơn.

---

*File này lưu tại: `reports/group_report.md`*  
*Commit sau 18:00 được phép theo SCORING.md*
