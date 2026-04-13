# SỔ TAY QUY TẮC SINH TỬ - LAB DAY 08 (BẮT BUỘC ĐỌC)

> Các quy tắc dưới đây được trích xuất trực tiếp từ file `SCORING.md`. Vi phạm có thể dẫn tới việc bị trừ toàn bộ điểm cá nhân (0 điểm) hoặc ảnh hưởng nặng đến quỹ điểm nhóm.

---

## ⏰ 1. QUY ĐỊNH VỀ TIMELINE & DEADLINE (CỰC KỲ NGHIÊM NGẶT)

*   **17:00:** Giảng viên mở khóa File `grading_questions.json`. Bắt đầu tải về và chạy hệ thống của nhóm. Quỹ thời gian là 1 Tiếng.
*   **18:00 (GIỜ CHỐT SỔ): Lệnh Cấm Commit liên quan đến System.**
*   **SAU 18:00:** Commit code sau 18h **Sẽ không được tính**. Chỉ duy nhất được phép đẩy (commit) các file Báo cáo (`reports/group_report.md` và `reports/individual/[ten_ban].md`).

---

## 🚫 2. QUY TẮC BÀN TAY SẮT - ÁP DỤNG HÌNH PHẠT (0/40 ĐIỂM)

Nhóm và cá nhân phải tuyệt đối tránh 4 hành vi sau nếu không muốn nhận 0 điểm:
1.  **Chém gió trong Report (Không khớp Code):** Bạn nói mình làm mục X trong báo cáo cá nhân, nhưng Git commit history không có dấu vân tay hay dòng bình luận nào chứng tỏ bạn làm việc đó ➔ **0 điểm cá nhân**.
2.  **Cướp công người khác:** Báo cáo bản thân làm phần việc mà người khác đã commit ➔ **0 điểm cá nhân**.
3.  **Đạo văn Report (Sao chép nhau):** Báo cáo cá nhân copy nội dung y chang nhau (trong cùng nhóm hoặc khác nhóm) ➔ **0 điểm cho tất cả những người liên quan**.
4.  **Hỏi thi kỹ thuật không trả lời được:** Claim mình viết hàm Reranking nhưng lúc review/vấn đáp giảng viên hỏi tại sao dùng hàm này thì tịt ngòi ➔ **0 điểm cá nhân**.

---

## 🎯 3. LÀM SAO ĐỂ GIÀNH ĐƯỢC 100 ĐIỂM TRỌN VẸN?

*   **Điểm Nhóm (Tối đa 60 điểm):**
    *   **20 điểm (Code):** Code phải **CHẠY ĐƯỢC**. Thà code đơn giản, cùi bắp nhưng bấm `python` không crash thì được điểm cao. Code thần thánh phức tạp nhưng crash giữa chừng là toang hệt.
    *   **30 điểm (Kết quả Grading Question):** Càng chém gió câu hỏi bẫy bịa đặt (Hallucination - Câu gq07) càng ăn penalty đắng (-5 điểm phần raw score). Hãy trả lời "Tôi không biết / Không đủ dữ liệu" khi không tìm thấy tài liệu gốc.
    *   **10 điểm (Document Overview):** Có giải thích rõ ràng `tuning-log` và `architecture` đã chọn.

*   **Điểm Cá Nhân (Tối đa 40 điểm):**
    *   **30 điểm (Report Cá Nhân Mới Lạ):** Thể hiện rõ tư duy trong việc phân tích "Fail Mode/Thất bại" tại sao kết quả chạy Grading Q/A lại sai ở câu A, câu B; từ đó đề xuất cách fix. (Độ dài 500-800 từ).
    *   **10 điểm (Code Evidence):** Tự mình gõ code và chứng minh được quá trình commit code trên nền tảng.

---

## 🔥 4. CÁC ĐIỂM THƯỞNG CỘNG THÊM (+5 BONUS)
1.  (+2 điểm) Cài đặt LLM đóng vai Ban giám khảo (`LLM-as-Judge`) vào file `eval.py` thay vì test bằng mắt thường.
2.  (+1 điểm) Log ra file grading hoàn hảo, không sót 1/10 câu hỏi, timestamp chỉ điểm là trước 18:00.
3.  (+2 điểm) Hệ thống trả lời xuất sắc đạt điểm tuyệt đối câu gq06 (Câu hỏi xoắn não khó nhất bài).
