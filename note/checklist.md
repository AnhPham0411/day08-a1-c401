# Bảng Phân Công & Checklist Theo Vai Trò (5 Người)

> Phân công chi tiết này bám sát biểu đồ nguồn lực của nhóm, giúp từng cá nhân biết chính xác mình cần đảm bảo code/viết gì trước deadline.

---

## 🧑‍💻 1. Tech Lead
**Trách nhiệm chính:** Giữ nhịp, nối code end-to-end, đảm bảo luồng `index.py` ➔ `rag_answer.py` ➔ `eval.py` chạy thông suốt toàn bộ.  
**Sprints:** 1, 2

**Checklist:**
- [x] Khởi tạo dự án, cài đặt `requirements.txt`, thiết lập file `.env` (API Keys).
- [x] **(Sprint 1 - index.py)** Khởi tạo DB (ChromaDB) và hàm `get_embedding()`. Hỗ trợ Retrieval Owner ghép code chunking vào luồng index.
- [x] Đảm bảo gõ lệnh `python index.py` chạy trơn tru, không báo lỗi.
- [x] **(Sprint 2 - rag_answer.py)** Viết hàm `retrieve_dense()` và kết nối LLM qua `call_llm()`.
- [x] Viết prompt gốc đảm bảo yêu cầu: Nếu không tìm thấy, hệ thống phải **"Abstain"** (trả lời Không đủ dữ liệu, không được bịa).
- [x] Gắn citation (trích dẫn `[1]`) vào câu trả lời của luồng RAG gốc.

---

## 🗃️ 2. Retrieval Owner
**Trách nhiệm chính:** Chunking strategy, metadata schema, implement variant (tối ưu pipeline với hybrid / rerank / query transform).  
**Sprints:** 1, 3

**Checklist:**
- [ ] **(Sprint 1 - index.py)** Quyết định Chunk size và Overlap phù hợp với bộ docs quy chế (để báo cáo cho Doc Owner).
- [ ] Viết bộ parse văn bản lấy ít nhất **3 metadata fields** (source title, section, effective_date).
- [ ] Pass code Metadata và Chunking sang cho Tech Lead để tích hợp vào index.
- [ ] **(Sprint 3 - rag_answer.py)** Quyết định chọn 1 Variant để tối ưu (Ví dụ: code thêm thuật toán BM25 cho Hybrid Search HOẶC code thêm Cross-Encoder Reranking).
- [ ] Cài đặt Variant này thành công vào mã nguồn chạy mượt mà không làm vỡ code của Tech Lead.
- [ ] Báo cáo lại cho Eval Owner B số liệu cấu hình (Top_K, Rerank Threshold, v.v) để chấm điểm.

---

## 📊 3. Eval Owner A
**Trách nhiệm chính:** Thiết kế `test_questions.json`, setup expected evidence, chạy `eval.py` và chịu trách nhiệm xuất file quan trọng `grading_run.json`.  
**Sprints:** 3, 4, Final

**Checklist:**
- [ ] Mở file `data/test_questions.json` và lấp đầy 10 câu hỏi thử nghiệm tự đặt ra kèm Expected Answer và Expected Source dựa vào 5 file docs.
- [ ] Viết/Chỉnh sửa file `eval.py` để file này lấy 10 câu testing ra bắn vào API của Tech Lead xem pipeline nhóm xây có trả lời đúng không.
- [ ] **(17:00 - GIỜ VÀNG)** Nhận bộ câu hỏi `grading_questions.json` được giảng viên public.
- [ ] Đưa bộ câu hỏi mới vào hệ thống và chạy Pipeline (bằng bản code tốt nhất của nhóm).
- [ ] Bắt buộc: Xuất ra script đẩy kết quả trả về vào file **`logs/grading_run.json`** chuẩn định dạng (có trường timestamp trước 18:00).
- [ ] (Bonus): Đảm bảo log đủ 10 câu, có timestamp hợp lệ.

---

## 📈 4. Eval Owner B
**Trách nhiệm chính:** Chấm scorecard baseline vs variant, chạy hàm `compare_ab()`, xuất dữ liệu ghi vào `tuning-log.md`.  
**Sprints:** 3, 4

**Checklist:**
- [ ] Cùng Owner A chạy bộ test nhưng rẽ nhánh 2 lần: 1 lần cho baseline (Bản chuẩn) và 1 lần cho variant (Bản cải tiến của R.Owner).
- [ ] Điền kết quả chạy vào 2 file đánh giá: `results/scorecard_baseline.md` và `scorecard_variant.md`.
- [ ] Chạy hàm `compare_ab()` để tìm ra Delta (thay đổi tích cực/tiêu cực gì khi gắn cải tiến vào).
- [ ] Tổng hợp thông số định lượng chuyển cho Doc Owner.
- [ ] **(Bonus Nhiệm vụ)**: Thử nghiệm chuyển code `eval.py` từ kiểm tra thủ công thành `LLM-as-Judge` (Để ăn thêm +2 điểm thưởng nhóm).

---

## 📝 5. Documentation Owner
**Trách nhiệm chính:** Tác giả chính của `architecture.md`, `tuning-log.md`, `group_report.md` và kiểm duyệt định dạng toàn bộ dự án trước khi nộp.   
**Sprints:** 4, Final

**Checklist:**
- [ ] Phỏng vấn R.Owner để viết mục "Mô tả chunking decision (kích cỡ, chiến lược, lý do)" vào file `docs/architecture.md`.
- [ ] Lấy số liệu từ Eval B để điền cấu hình vào `architecture.md` và vẽ/chèn sơ đồ pipeline.
- [ ] Viết `docs/tuning-log.md`: Đảm bảo chốt câu kết luận rõ ràng (Variant tốt hay kém hơn Baseline do đâu).
- [ ] Kiểm tra toàn bộ Folder Repo lần cuối (17:45): file `.py` đủ chưa? `grading_run.json` đúng json chưa?
- [ ] Bấm Nút **Commit Source Code** lần cuối trước mốc 18:00 gắt gao.
- [ ] (Sau 18:00) Viết và commit `reports/group_report.md` bằng cách tổng hợp công sức của cả 4 người còn lại.
