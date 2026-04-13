# Yêu Cầu Quản Lý Dự Án Lab Day 08 - RAG Pipeline (Dưới Góc Độ PM)

Với vai trò Project Manager (PM), để đảm bảo nhóm của chúng ta đạt điểm tối đa (100 điểm) và đáp ứng đúng timeline, tôi đã chia dự án này thành **5 Nhiệm vụ (Missions)** cốt lõi. Mỗi nhiệm vụ có một mục tiêu rõ ràng và một checklist cụ thể cần hoàn thành để vượt qua yêu cầu Definition of Done (DoD) và tiêu chí chấm điểm khắt khe.

> **LƯU Ý QUAN TRỌNG VỀ DEADLINE:**
> - Toàn bộ code (`.py`), log (`grading_run.json`), documents kiến trúc (`architecture.md`, `tuning-log.md`) **PHẢI COMMIT TRƯỚC 18:00**.
> - Report nhóm và report cá nhân được phép commit **SAU 18:00**.
> - Tuyệt đối không gian lận, báo cáo sai sự thật hoặc bịa đặt (hallucination) trong pipeline để tránh nhận điểm 0.

---

## 🚀 Nhiệm Vụ 1: Phân Tích & Xây Dựng Indexing Pipeline (Sprint 1)
**Mục tiêu:** Xây dựng thành công cơ sở dữ liệu vector (ChromaDB) với dữ liệu đã được preprocess, chia nhỏ (chunk) và có đầy đủ metadata. (Trị giá 5 điểm Sprint).

**Checklist:**
- [ ] Cài đặt đầy đủ dependencies (`pip install -r requirements.txt`).
- [ ] Khởi tạo `.env` với API key cần thiết.
- [ ] Cài đặt hàm `get_embedding()` (chọn OpenAI hoặc Sentence Transformers).
- [ ] Xử lý chia chunk cho 5 tài liệu trong thư mục `data/docs/`.
- [ ] Đảm bảo mỗi chunk đính kèm ít nhất **3 metadata fields** (source, section, effective_date) một cách chính xác.
- [ ] Thêm các chunk + metadata vào ChromaDB bằng hàm `build_index()`.
- [ ] Chạy lệnh `python index.py` thành công không lỗi.
- [ ] Kiểm tra bằng hàm `list_chunks()` để đảm bảo chunk hợp lý, không bị cắt ngang điều khoản quan trọng.

---

## 🚀 Nhiệm Vụ 2: Xây Dựng Retrieval & Trả Lời Baseline (Sprint 2)
**Mục tiêu:** Tạo pipeline rút trích (Search) và tạo sinh câu trả lời (Generate) có bằng chứng (citation), đồng thời phải biết nói "Không biết" nếu tài liệu không nhắc đến. (Trị giá 5 điểm Sprint).

**Checklist:**
- [ ] Cài đặt hàm `retrieve_dense()` để query ChromaDB lấy ra các chunks liên quan nhất.
- [ ] Chèn prompt chuẩn và cài đặt `call_llm()` với OpenAI/Gemini.
- [ ] **Kiểm thử tính năng Citation:** `rag_answer("SLA ticket P1?")` phải trả về câu trả lời có trích dẫn `[1]`.
- [ ] **Kiểm thử tính năng Abstain (Chống Hallucinate):** `rag_answer("ERR-403-AUTH")` phải trả lời "Không đủ dữ liệu" chứ tuyệt đối **không tự biên soạn thêm**.
- [ ] Kiểm tra để đảm bảo trường `sources` trong kết quả không rỗng khi query thành công.

---

## 🚀 Nhiệm Vụ 3: Tối Ưu, Cải Tiến (Variant) & Đánh Giá Tác Động (Sprint 3)
**Mục tiêu:** Thay đổi **chỉ một biến** duy nhất trong pipeline để tạo ra biến thể tối ưu (Variant) nhằm so sánh với bản gốc (Baseline). (Trị giá 5 điểm Sprint).

**Checklist:**
- [ ] Xác định một loại kỹ thuật cải tiến để làm Variant (Hybrid Search / Rerank với cross-encoder / Query Transform).
- [ ] Cài đặt Variant được chọn vào mã nguồn (`rag_answer.py`) sao cho có thể chạy mượt mà từ đầu đến cuối.
- [ ] Bật script so sánh `compare_retrieval_strategies()` để ra số liệu chạy Baseline vs Variant.
- [ ] Viết nháp lý do vì sao lại chọn thực hiện phương pháp này để đưa vào `docs/tuning-log.md`.
- [ ] Trích xuất các chỉ số và lập bảng so sánh.

---

## 🚀 Nhiệm Vụ 4: Tự Động Hóa Kiểm Thử & Chốt Tài Liệu Kỹ Thuật (Sprint 4)
**Mục tiêu:** Hoàn thiện bài test, cung cấp điểm Scorecard cho hệ thống cũng như hoàn chỉnh tài liệu mô tả kiến trúc của nhóm. (Trị giá 5 điểm Sprint + 10 điểm Group Docs).

**Checklist:**
- [ ] Hoàn tất 10 câu hỏi test đầu vào tại `data/test_questions.json` (dùng làm cơ sở tự evaluate).
- [ ] (Bonus +2 Điểm cá nhân) Thử nghiệm tính module tự chấm điểm `LLM-as-Judge` (trong `eval.py`) thay vì chấm thủ công.
- [ ] Chạy thành công `python eval.py` quét toàn bộ 10 câu hỏi mà không dính crash.
- [ ] Sinh ra `results/scorecard_baseline.md` và `scorecard_variant.md` hoàn chỉnh.
- [ ] **Hoàn tất `docs/architecture.md` (5đ):**
  - [ ] Mô tả quyết định chunking (size, overlap, why).
  - [ ] Mô tả config baseline vs variant (top_k, mode, rerank).
  - [ ] Có biểu đồ hoặc sơ đồ dạng text/mermaid phác họa lại pipeline.
- [ ] **Hoàn tất `docs/tuning-log.md` (5đ):**
  - [ ] Điền đúng 1 biến đã đổi và lý do vì sao (Sprint 3).
  - [ ] Có bảng so sánh 2 variants theo ít nhất 2 metric.
  - [ ] Viết tóm gọn kết luận.

---

## 🚀 Nhiệm Vụ 5: Ngày Định Đoạt - Grading Testing & Gửi Báo Cáo (#Final)
**Mục tiêu:** Triển khai chạy bộ câu hỏi bí mật "Grading" khi được công bố (17:00), tạo logs và hoàn thành mọi bài test cá nhân để pass 100%. (Trị giá 30 điểm Grading + 40 điểm Cá Nhân).

**Checklist:**
- [ ] **(17:00 -> 18:00)** Cập nhật `data/grading_questions.json` và chạy Pipeline TỐT NHẤT vào file `logs/grading_run.json`.
- [ ] Audit log: Đảm bảo đáp ứng đủ format JSON schema yêu cầu (gồm ID, question, answer, sources, chunks_retrieved, retrieval_mode, timestamp).
- [ ] Audit câu hỏi gq07 (bẫy Hallucinate): Xác minh lại log xem đã chặn được câu hỏi ngoài tài liệu bằng lệnh ngắt "Abstain" chưa. Điểm penalty phần này rất nặng (-5đ raw).
- [ ] (Bonus +1) Log file grading_questions phải có đủ đáp án 10 câu kèm timestamp trước giờ khóa Github (18:00).
- [ ] **Commit Code** trước 18:00: Mọi file `*.py`, JSON logs, Scorecard, `architecture.md`, `tuning-log.md` phải commit xong toàn bộ.
- [ ] Sau 18:00, hoàn thiện `reports/group_report.md` (Báo cáo tổng kết nhóm).
- [ ] Hoàn thiện từng `reports/individual/[ten_thanh_vien].md` (500 - 800 từ/người):
  - [ ] Phải nêu đóng góp cụ thể khớp tuyệt đối với file code (Commit history).
  - [ ] Chọn **1 câu hỏi grading** và phân tích chuyên sâu (Root cause pipeline fail/success chỗ nào).
  - [ ] Viết phần rút luận bài học kinh nghiệm và đề xuất 1-2 cải tiến cá nhân (tham chiếu số liệu Scorecard).
