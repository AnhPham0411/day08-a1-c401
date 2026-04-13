# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Hoàng Tuấn Anh  
**Vai trò trong nhóm:** Retrieval Owner   
**Ngày nộp:** 13/04/2026  

---

## 1. Em đã làm gì trong lab này?

Trong Sprint 1 và Sprint 3, với vai trò Retrieval Owner, em chịu trách nhiệm thiết kế và tối ưu hoá toàn bộ tầng truy xuất tài liệu (retrieval layer). Điểm khởi đầu là cấu hình chia đoạn văn bản với `CHUNK_SIZE=400` và `CHUNK_OVERLAP=80`. Qua quá trình kiểm thử, em phát hiện mô hình Baseline sử dụng Dense Retrieval thuần túy thường xuyên bỏ sót các câu hỏi chứa thuật ngữ kỹ thuật chính xác — ví dụ như mã lỗi hoặc tên tài liệu cụ thể.

Để khắc phục, em xây dựng Variant bằng cách tích hợp **Hybrid Search**, kết hợp Dense (vector embedding) và Sparse (BM25) thông qua thuật toán **Reciprocal Rank Fusion (RRF)**. Tuy nhiên BM25 mặc định tách token theo khoảng trắng khiến tiếng Việt bị nhiễu nặng. Em xử lý bằng cách điều chỉnh trọng số `dense_weight=0.8, sparse_weight=0.2` để ngữ nghĩa vẫn chiếm ưu thế, đồng thời tích hợp Cross-Encoder `ms-marco-MiniLM-L-6-v2` vào bước Rerank để tinh chỉnh thứ hạng kết quả. Variant cuối cùng vượt trội so với Baseline trên cả ba tiêu chí Faithfulness, Relevance và Completeness.

---

## 2. Điều em hiểu rõ hơn sau lab này

Thứ nhất, em hiểu sâu hơn về **giới hạn thực tế của từng phương pháp retrieval**. Dense Retrieval rất mạnh trong việc nắm bắt ý nghĩa ngữ cảnh rộng, nhưng lại yếu khi cần khớp chính xác mã lỗi hay tên định danh kỹ thuật. Sparse (BM25) thì ngược lại — bắt từ khóa cực chuẩn nhưng dễ trả về nhiễu nếu có nhiều từ trùng lặp trong corpus. RRF giải quyết được mâu thuẫn này bằng cách hợp nhất thứ hạng từ cả hai nguồn, nhưng kỹ sư vẫn cần theo dõi và đo delta liên tục để điều chỉnh hệ số phạt cho phù hợp với từng bộ dữ liệu cụ thể.

Thứ hai, em ngộ ra bài học quan trọng: **Context Recall đạt 100% chưa chắc đã đủ để sinh ra câu trả lời đúng**. Nếu bước Chunking cắt đứt một định nghĩa và điều kiện áp dụng của nó thành hai đoạn riêng biệt, thì dù Retriever lấy được một trong hai đoạn đó, LLM vẫn không có đủ thông tin để trả lời hoàn chỉnh. Đây là giới hạn thuộc về cấu trúc dữ liệu, không phải lỗi của thuật toán retrieval.

---

## 3. Điều em ngạc nhiên hoặc gặp khó khăn

Khó khăn lớn nhất đến từ việc **Hybrid RRF hoạt động tệ hơn Dense thuần túy** ngay sau khi implement — điều hoàn toàn ngược với kỳ vọng ban đầu.

Cụ thể: sau khi implement `retrieve_hybrid()` với `dense_weight=0.6, sparse_weight=0.4` và chạy thử với verbose mode, pipeline trả về kết quả abstain cho câu *"SLA xử lý ticket P1 là bao lâu?"* — trong khi Dense thuần túy trả lời đúng ngay lần đầu. Để xác định nguyên nhân, em viết script `debug_retrieval.py` chạy riêng `retrieve_dense()` và `retrieve_hybrid()` trên cùng query với `top_k=20`, rồi in toàn bộ rank và section của từng chunk:

```
retrieve_dense()  → rank 1 = Phần 2: SLA theo mức độ ưu tiên (score=0.4899) ✓
retrieve_hybrid() → rank 1 = Phần 5: Lịch sử phiên bản                      ✗
```

Dense retrieve đúng hoàn toàn. Hybrid bị sai vì BM25 tokenize tiếng Việt theo whitespace — các từ ngắn như *"xu"*, *"ly"*, *"la"*, *"ticket"* xuất hiện rải rác trong gần như toàn bộ corpus, khiến BM25 cho điểm cao đều cho nhiều chunk không liên quan. Với `sparse_weight=0.4`, RRF bị kéo lệch đủ để đẩy chunk sai lên rank 1, đè lên dense result đúng.

Fix là tăng `dense_weight` từ 0.6 lên 0.8 — tin dense hơn vì đã có bằng chứng dense đúng. Sau khi fix, hybrid hoạt động ổn định và không còn bị noise từ BM25 chi phối.

Bài học rút ra: **implement xong không có nghĩa là đúng — phải debug từng tầng riêng biệt trước khi kết luận**. Nếu chỉ nhìn vào output cuối (abstain) mà không tách `retrieve_dense()` và `retrieve_hybrid()` ra để so sánh, em đã không xác định được đúng tầng gây lỗi và có thể đi sai hướng sang sửa chunking hoặc prompt.

---

## 4. Phân tích một câu hỏi trong scorecard

**Câu hỏi được chọn:** `[gq05] Contractor từ bên ngoài công ty có thể được cấp quyền Admin Access không? Nếu có, cần bao nhiêu ngày và có yêu cầu đặc biệt gì?`

**Kết quả quan sát:** Cả Baseline và Variant đều đạt Context Recall 100% — tức là hệ thống đã lấy đúng file `access-control-sop`. Nhưng điểm Completeness của cả hai đều ở mức thấp, và câu trả lời cuối cùng chỉ là: *"Em không có đủ dữ liệu trong tài liệu nội bộ để trả lời câu hỏi này."*

**Nguyên nhân gốc rễ:** Đây là hậu quả điển hình của **Chunking Context Break**. Định nghĩa về đối tượng "Contractor" nằm ở Section 1 của tài liệu, trong khi quy trình phê duyệt cấp quyền "Admin Level 4" dành cho Contractor lại trải dài ở Section 2. Với `CHUNK_SIZE=400`, hai phần thông tin này bị tách ra thành hai chunk độc lập. Retriever chỉ lấy được chunk chứa quy trình phê duyệt (Section 2), nhưng bỏ mất chunk định nghĩa đối tượng áp dụng (Section 1). Thiếu nửa vế tiền đề, Prompt Grounding khoá chặt LLM lại — đúng như thiết kế — và kết quả là câu Abstain.

Sau khi debug bằng `debug_retrieval.py` với query này, em xác nhận Section 1 nằm ở **rank 4** — bị cắt bởi `top_k_select=3`. Fix là tăng `top_k_select` từ 3 lên 5 để đưa đủ cả hai chunk vào prompt. Sau khi fix, gq05 trả lời đúng với Faithful=5, Relevant=5.

**Tại sao Rerank cũng không cứu được ở config ban đầu:** Cross-Encoder chỉ có thể xếp lại thứ hạng trong tập kết quả đã được retrieve. Khi `top_k_select=3` cắt mất chunk ở rank 4 trước khi vào prompt, Reranker không có cơ hội đưa nó trở lại.

---

## 5. Nếu có thêm thời gian, em sẽ làm gì?

Giải pháp em muốn thử cho bài toán trên là **Parent-Child Chunking**. Ý tưởng cốt lõi: chia document thành các chunk nhỏ (child) để embedding có độ phân giải cao và khớp vector chính xác. Nhưng trước khi đưa context vào bước generation, hệ thống sẽ tự động mở rộng ra "chunk cha" — tức là đoạn văn bản lớn hơn bao quanh chunk đó, thường gấp 2–3 lần kích thước chunk con. Nhờ vậy, LLM sẽ thấy cả định nghĩa "Contractor" ở đầu trang lẫn quy trình "Level 4" ở cuối trang trong cùng một lượt context, không lo đứt đoạn logic.

Bên cạnh đó, em muốn thay thế cách tách token BM25 hiện tại bằng thư viện `underthesea` để xử lý đúng từ ghép tiếng Việt, thay vì tách theo khoảng trắng như hiện nay — điều này sẽ cải thiện đáng kể chất lượng Sparse Retrieval trên corpus tiếng Việt mà không cần tăng `dense_weight` như giải pháp tạm hiện tại.