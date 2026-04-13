# Bảng Phân Công & Checklist Theo Vai Trò (Phiên bản 6 Người)

> Phân công chi tiết bám sát tiến độ dự án, tối ưu hóa năng suất cho 6 thành viên mà không gây conflict code (Git).

---

## 🧑‍💻 1. Tech Lead
**Trách nhiệm chính:** Giữ nhịp, nối code end-to-end, đảm bảo luồng `index.py` ➔ `rag_answer.py` ➔ `eval.py` chạy thông suốt toàn bộ.  
**Sprints:** 1, 2

**Checklist:**
- [x] Khởi tạo dự án, cài đặt `requirements.txt`, thiết lập file `.env` (API Keys).
- [x] **(Sprint 1 - index.py)** Khởi tạo DB (ChromaDB) và hàm `get_embedding()`. Lắp luồng Chunking của Retrieval Owner vào để build DB.
- [x] Đảm bảo gõ lệnh `python index.py` chạy trơn tru, không báo lỗi.
- [x] **(Sprint 2 - rag_answer.py)** Kết nối LLM API (OpenAI/Gemini) qua hàm `call_llm()` với temperature=0.
- [x] Gắn citation (trích dẫn `[1]`) vào câu trả lời của luồng RAG gốc.


---

## 🗃️ 2. Retrieval Owner (Hoàng Tuấn Anh)
**Trách nhiệm chính:** Kỹ sư xử lý dữ liệu lõi (Advanced Document Parsing & Semantic Chunking), và Thiết kế phễu tìm kiếm đa tầng rẽ nhánh (Hybrid RRF & Cross-Encoder).  
**Sprints:** 1, 2, 3

**Checklist:**
- [x] **(Sprint 1 - index.py)** Xây dựng Regex Parser động trích xuất 4 trường Metadata (Source, Department, Effective Date, Access) và bảo tồn nội dung ghi chú `preamble_extra`.
- [x] Cài đặt **Semantic Chunking** cắt đoạn văn theo ranh giới đoạn `\n\n`, chèn overlap 80 tokens để duy trì ngữ cảnh cho câu văn.
- [x] Bàn giao hàm tiền xử lý mượt mà cho Tech Lead.
- [x] **(Sprint 2 - rag_answer.py)** Viết lõi truy xuất Baseline: `retrieve_dense` lấy vector từ ChromaDB.
- [x] **(Sprint 3 - rag_answer.py)** Khởi tạo `BM25Index` và code hàm `retrieve_sparse` giải quyết các câu hỏi Exact Keyword (P1, ERR-403).
- [x] Xây dựng thuật toán **Hybrid RRF Search** lai tạo Dense + Sparse xuất sắc. Cài đặt thêm màng lọc **Rerank Cross-Encoder** ép gọn Top 3 ứng viên.
- [x] Chạy đối chiếu `compare_retrieval_strategies()` giao thông số cấu hình chốt cho Eval Owner.

---

## 📊 3. Eval Owner A
**Trách nhiệm chính:** Thiết kế `test_questions.json`, setup expected evidence, chạy `eval.py` và chịu trách nhiệm xuất file quan trọng `grading_run.json`.  
**Sprints:** 3, 4, Final

**Checklist:**
- [ ] Mở file `data/test_questions.json` và lấp đầy 10 câu hỏi thử nghiệm tự đặt ra kèm Expected Answer và Expected Source dựa vào 5 file docs.
- [ ] Lấy 10 câu testing bắn vào API của Tech Lead xem pipeline nhóm xây có trả lời đúng không.
- [ ] **(17:00 - GIỜ VÀNG)** Nhận bộ câu hỏi `grading_questions.json` được giảng viên public.
- [ ] Đưa bộ câu hỏi mới vào hệ thống và chạy Pipeline (bằng bản code tốt nhất của nhóm).
- [ ] Bắt buộc: Xuất ra script đẩy kết quả trả về vào file **`logs/grading_run.json`** chuẩn định dạng (có trường timestamp trước 18:00).

---

## 📈 4. Eval Owner B
**Trách nhiệm chính:** Chấm scorecard baseline vs variant, chạy hàm `compare_ab()`, xuất dữ liệu ghi vào `tuning-log.md`.  
**Sprints:** 3, 4

**Checklist:**
- [ ] Cùng Owner A chạy bộ test nhưng rẽ nhánh 2 lần: 1 lần cho baseline (Bảo gốc) và 1 lần cho variant (Bản cải tiến của R.Owner).
- [ ] Điền kết quả chạy vào 2 file đánh giá: `results/scorecard_baseline.md` và `scorecard_variant.md`.
- [ ] Chạy hàm `compare_ab()` để tìm ra Delta (thay đổi tích cực/tiêu cực gì khi gắn cải tiến vào).
- [ ] Tổng hợp thông số định lượng chuyển cho Doc Owner.
- [ ] *(Đã nhường khâu viết code LLM-as-Judge tự động cho Prompt Engineer hẫu trợ).*

---

## 📝 5. Documentation Owner
**Trách nhiệm chính:** Tác giả chính của `architecture.md`, `tuning-log.md`, `group_report.md` và kiểm duyệt định dạng toàn bộ dự án trước khi nộp.   
**Sprints:** 4, Final

**Checklist:**
- [ ] Phỏng vấn R.Owner để viết mục "Mô tả chunking decision (kích cỡ, chiến lược, lý do)" vào file `docs/architecture.md`.
- [ ] Lấy số liệu từ Eval B để điền cấu hình vào `architecture.md` và vẽ/chèn sơ đồ pipeline.
- [ ] Viết `docs/tuning-log.md`: Đảm bảo chốt câu kết luận rõ ràng (Variant tốt hay kém hơn Baseline do đâu).
- [ ] Kiểm tra toàn bộ Folder Repo lần cuối (17:45): file `.py` đủ chưa? `grading_run.json` đúng định dạng json chưa?
- [ ] Bấm Nút **Commit Source Code** lần cuối trước mốc 18:00 gắt gao.
- [ ] (Sau 18:00) Viết và commit `reports/group_report.md` bằng cách tổng hợp công sức của cả 5 người còn lại.

---

## ✍️ 6. Prompt Engineer & LLM Judge (Vai trò Mới)
**Trách nhiệm chính:** Cắm rễ ở file `rag_answer.py` và `eval.py`. Kiểm soát văn phong, khóa mõm Hallucination tuyệt đối ở đầu ra LLM, và xây dựng Ban giám khảo AI (LLM-as-a-Judge) để hỗ trợ bộ phận QA.
**Sprints:** 2, 4

**Checklist:**
- [ ] **(Sprint 2 - rag_answer.py):** Nhận bàn giao hàm `build_grounded_prompt` từ Tech Lead.
- [ ] Thiết kế Prompt bọc thép chống suy diễn (Abstain): Ép AI phải trả lời *"Không đủ dữ liệu"* nếu Context rác, bắt buộc chèn đúng số `[1], [2]` theo Source.
- [ ] Định hình tone giọng trả lời phù hợp với chuyên viên CS Helpdesk (Ngắn gọn, rõ rệt, thân thiện).
- [ ] **(Sprint 4 - eval.py):** Nhận bàn giao các hàm `score_faithfulness`, `score_answer_relevance`, `score_completeness` từ Eval Owner B.
- [ ] Viết kịch bản prompt "Đóng vai người chấm thi": Ép mô hình tự đọc Output của hệ thống và phản hồi số điểm từ 1-5 dạng object JSON `{"score": 5, "notes": "..."}` để hệ thống của Eval Owner tự động chạy ra bảng điểm mà không cần chấm tay.
