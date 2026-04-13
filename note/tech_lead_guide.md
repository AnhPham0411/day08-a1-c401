# CẨM NANG DÀNH RIÊNG CHO TECH LEAD & CHIẾN LƯỢC ĐẠT 100 ĐIỂM

Đây là bản tóm tắt dành riêng cho vị trí **Tech Lead** để bạn nắm rõ mình phải "code" cái gì, "ghép" cái gì và cách quản lý rủi ro ngày nộp bài để đạt max điểm.

---

## 👨‍💻 1. NHIỆM VỤ CỐT LÕI CỦA TECH LEAD (SPRINT 1 & 2)

**Trọng tâm:** Bạn không cần làm những thứ hoa mỹ, nhiệm vụ lớn nhất của bạn là **viết cấu trúc sườn** và đảm bảo luồng code chạy thông suốt từ đầu tới cuối.

**Nhiệm vụ Sprint 1 - Indexing Pipeline (`index.py`):**
- Khởi tạo sườn dự án (cài requirements, set `.env` chứa API KEY).
- Viết hàm `get_embedding()`.
- *Phối hợp:* Hỗ trợ Retrieval Owner để ghép logic Chunking + Metadata của họ vào hàm `build_index()` của bạn.
- Đảm bảo lệnh `python index.py` chạy lên 5 docs vào ChromaDB thành công.

**Nhiệm vụ Sprint 2 - Generation Pipeline (`rag_answer.py`):**
- Viết hàm kết nối Vector DB: `retrieve_dense()`.
- Viết hàm gọi LLM: `call_llm()`.
- **(CỰC KỲ QUAN TRỌNG) Bẫy Hallucination:** Bạn phải tinh chỉnh Prompt cẩn thận nhất có thể. Bắt buộc LLM phải trả lời theo mẫu **có trích dẫn `[1]`**, và nếu không tìm thấy dữ liệu, prompt phải ép LLM nói "Tôi không có thông tin / Không đủ dữ liệu" chứ **không được chém gió**.
- *Phối hợp:* Ở Sprint 3, tạo Interface / Base code để Retrieval Owner có không gian chế cháo Variant (ví dụ Rerank) mà không tàn phá sườn code gốc của bạn.
- Bấm lệnh `python rag_answer.py` trả về đáp án mượt mà.

---

## 📤 2. LƯU Ý SỐNG CÒN VỀ NỘP BÀI (DEADLINE SYSTEM)

Bạn là Tech Lead, hãy nhắc nhở team cực kỳ nghiêm ngặt về các khung giờ này:

*   **17:00 - Bão Bắt Đầu:** Đề file `grading_questions.json` sẽ lên sóng. Lập tức túm áo ông *Eval Owner A* chạy cho ra log liền.
*   **17:30 - Rà Soát Cuối:** Tech Lead rà soát lại repository xem có chạy được trên máy trắng không. Format JSON log đã chuẩn chỉnh chưa (phải có cột timestamp).
*   **18:00 - CỔNG TỬ THẦN (Git Lock):**
    *   Toàn bộ mã nguồn (`*.py`).
    *   File hệ thống, file json log (`grading_run.json`).
    *   Các file design/docs nhóm (`architecture.md`, `tuning-log.md`).
    *   👉 **Tất cả các file trên PHẢI ĐƯỢC COMMIT TRƯỚC 18:00.** (Nếu commit sau giờ này thì commit đó coi như tờ giấy lộn).
*   **SAU 18:00 - Tạm Thơ Phào:** Lúc này file code bị khóa, nhưng bạn vẫn được phép ngồi trau chuốt và nộp 2 file Markdown báo cáo: `group_report.md` và các file `[ten_ban].md`.

---

## 🏆 3. CÔNG THỨC 100 ĐIỂM + 5 BONUS DÀNH CHO BẠN

### 🎯 Cách lấy max 60 điểm Nhóm:
1.  **Chạy được là Vua (20đ):** Cấm đua đòi làm các thuật toán quá phức tạp nếu nó có tỉ lệ Crash cao. Một hệ thống cùi bắp chạy từ đầu tới cuối đem lại điểm tuyệt đối phần System.
2.  **Đừng Bịa Chuyện (30đ):** Ở câu hỏi bẫy `gq07` (Hỏi thông tin không có trong text). Nếu model của bạn chém gió câu đó -> Bạn bị **TRỪ 50% Điểm Câu**. Nếu model dõng dạc nói "Abstain - Tôi không lấy được data" -> Bạn ăn trọn 10 điểm. **Tech Lead phải test cực kỳ khắt khe cơ chế chống Hallucination này bằng prompt.**
3.  **Docs Đàng Hoàng (10đ):** `architecture.md` và `tuning-log.md` cần có số liệu so sánh rõ ràng, giải thích đúng lý lẽ tại sao lại set Top_K là 5 mà không phải 3.

### 🥇 Cách lấy max 40 điểm Cá Nhân của Tech Lead:
1.  **Làm Trò Nào, Báo Trò Đó (- Liều mạng = 0đ):** Bạn code phần `call_llm()` và `retrieve_dense()`. Trong report, cứ nói đúng sự thật là mình làm cái đó. **TUYỆT ĐỐI** không ghi tranh công phần của Retrieval Owner (Ví dụ: "Em code thuật toán Reranking") -> Giảng viên nhìn Commit History không thấy -> Xóa sổ điểm của bạn về 0. (Luật Zero-Tolerance).
2.  **Phân Tích Sâu (Report):** Trong file report cá nhân, hãy bốc 1 câu hỏi test mà hệ thống trả lời ngốc ngếch. Sau đó viết giải trình kiểu: *"Câu X sai vì hàm `retrieve_dense` của tôi lấy ra 3 chunk nhưng lại sót cái chunk chứa ý A, tôi đề xuất mai mốt phải nâng rate chunk overlap lên 150...".* Càng chi tiết dựa trên log càng ăn điểm.

### 🌟 Cách vét luôn 5 điểm Bonus (Giành cho siêu nhân):
1.  **+2đ:** Không chấm điểm baseline/variant bằng mắt. Nhờ GPT/Gemini chấm điểm tự động (LLM-as-Judge) trong hàm `eval.py`.
2.  **+1đ:** Cùng team Eval Owner chạy mượt 10/10 câu grading questions và chốt timestamp trong JSON log **trước 18:00**.
3.  **+2đ:** Prompt của Tech Lead + Chiến lược search của Retrieval Owner xử lý hoàn hảo câu khó nhất đề bài (`gq06` - Cần móc xích dữ liệu nhảy từ doc này sang doc kia).
