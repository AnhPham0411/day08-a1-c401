# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Tuấn Anh  
**Vai trò trong nhóm:** Retrieval Owner  
**Ngày nộp:** 13/04/2026  

---

## 1. Tôi đã làm gì trong lab này? (Khoảng 140 từ)

Với vai trò Retrieval Owner trong Sprint 1 và 3, trách nhiệm của tôi là xây dựng, cấu hình và tối ưu hóa hệ thống truy xuất (retrieval) để vượt qua Baseline rập khuôn. Ban đầu, tôi tiến hành chia nhỏ tài liệu nội bộ với tham số `CHUNK_SIZE=400` và `CHUNK_OVERLAP=80`.

Đến quá trình nâng cấp thành bản Variant, tôi đã thiết lập kết hợp thuật toán tìm kiếm vector Dense (text-embedding-3-small) và tìm kiếm từ khóa Sparse (BM25) qua thuật toán Reciprocal Rank Fusion (RRF). Nhận thấy BM25 mặc định tách từ tiếng Việt bằng khoảng trắng rất tệ và tạo ra các điểm rank nhiễu, tôi chủ động điều chỉnh lại trọng số `dense_weight=0.8, sparse_weight=0.2`. Mức nghiêng trọng số này giúp pipeline ưu tiên bắt ngữ nghĩa tài liệu hơn. Sau đó, tôi triển khai tích hợp thêm mô hình `ms-marco-MiniLM-L-6-v2` làm Cross-Encoder để rerank (chấm lại điểm các tài liệu), loại bỏ triệt để tài liệu thừa.

---

## 2. Điều tôi hiểu rõ hơn sau lab này (Khoảng 140 từ)

Thứ nhất, tôi đã nắm được kỹ thuật thiết kế **Hybrid Retrieval** như một hệ thống bù trừ hoàn hảo: Vector DB (Dense) đỉnh cao về việc tìm sự tương đồng ngữ nghĩa nhưng hay bỏ sót các mã lỗi hoặc từ kỹ thuật chính xác do lỗi Embedding; trong khi Sparse (BM25) bắt theo ký tự rất mạnh nhưng dễ đem rác về. Xếp hạng RRF giải quyết vấn đề đó, tuy nhiên tỷ lệ phạt trong RRF cần canh chỉnh thực tế chứ không có công thức chung, nhất là với nhóm ngôn ngữ như tiếng Việt.

Thứ hai, tôi ngộ ra tỷ lệ **Context Recall = 100% (tìm trúng file) không đảm bảo Generation thành công**. Nếu kỹ thuật cắt file (Chunking) ban đầu bị vô duyên, thì dù Retriever lấy được chunk nhưng văn bản chứa trong chunk bị nứt phay, LLM vẫn sẽ không thể sinh ra đủ cấu trúc hoàn chỉnh của thông tin. RAG là một ống nước kín, tắc nghẽn ở Chunking thì Retrieval tinh vi đến mấy cũng trở thành vô nghĩa.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (Khoảng 140 từ)

Trở ngại đáng nhớ nhất với tôi là cấu trúc chấm thi do bị xung đột với quy tắc Grounding do chính team lập ra. 

Sau khi tôi và Tech Lead tinh chỉnh Prompt bắt buộc mô hình phải từ chối trả lời nếu thiếu tài liệu (Abstain) để chống bịa (Hallucination), kết quả in ra `"Tôi không có đủ dữ liệu..."` rất mượt mà. Đáng ngạc nhiên là Evaluate AI (LLM-as-a-judge) lại chấm cơ chế phòng ngự đó là 0 hoặc 1 điểm ở mục **Faithfulness**. Thay vì tính điểm Abstain vào mục an toàn (điểm 5/5), hàm chấm `eval.py` cũ lại bắt buộc chấm "Có" / "Không" do không nhận diện được văn bản từ chối. 

Ngoài ra, quá trình debug hệ thống bị mắc thêm lỗi UnicodeEncodeError trên terminal Windows ở bước in log. Tôi đã phải trực tiếp can thiệp debug, sửa code đổi hệ điểm chấm 5.0, vá LLM-Judge và ép kiểu `sys.stdout` UTF-8 để tự động hoá lại toàn bộ Sprint 4.

---

## 4. Phân tích một câu hỏi trong scorecard (Khoảng 200 từ)

**Câu hỏi:** `[gq05] Contractor từ bên ngoài công ty có thể được cấp quyền Admin Access không? Nếu có, cần bao nhiêu ngày và có yêu cầu đặc biệt gì?`

**Phân tích kỹ thuật:**
- **Điểm số Baseline và Variant:** Cả bản Dense hay Hybrid Reranker đều đạt Context Recall hoàn hảo (5/5). Tuy nhiên, cả hai nhánh đều nhận điểm Completeness cực thấp (1/5) do hệ thống tạo câu trả lời (Generation) bỏ cuộc với thông báo: `"Tôi không có đủ dữ liệu trong tài liệu nội bộ để trả lời..."`
- **Nguyên nhân cốt lõi (Lỗi Chunking):** Dù Retrieve hoàn toàn trúng file đích `access-control-sop.md`, sai sót lại do khoảng cắt của văn bản. Cụm từ "Contractor" quy định phạm vi đối tượng lại nằm tuốt trên Section 1, trong khi nguyên quy trình cấp quyền "Admin Level 4" lại nằm tận Section 2. Mức Chunk Size quy định 400 khiến văn bản bị chẻ thành 2 phần tách biệt. Khi tìm kiếm, thuật toán chỉ gom được đoạn có chữ "Level 4" chứ không thể túm được phần tiền đề Section 1. Do thiếu một nửa vế định danh điều kiện, con LLM Generation bị đưa vào thế kẹt, bắt buộc phải báo hiệu "Abstain" để tránh hallucination.
- **Biến thể:** Kể cả có dùng Rerank mạnh như Cross-Encoder, Hybrid RRF cũng không thể hàn gắn được sự phân mảnh đoạn tách rời về hai Chunk xa nhau. Đó là lý do không có Delta khác biệt. 

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (Khoảng 90 từ)

Nếu có thêm 1 tiếng, tôi sẽ áp dụng kỹ thuật **Parent-Child Chunking (hay Auto-merging Retriever)**. Theo đó, tôi sẽ tách nhỏ theo cấp độ câu (Child doc) rồi Embed để đảm bảo Vector search trúng vùng ngôn từ liên quan mật thiết. Tuy nhiên, khi kết quả được trả về trong bộ chọn lọc của `rag_answer`, hệ thống không đưa mỗi mẩu câu nhỏ này vào prompt mà sẽ kéo nguyên cả cụm văn bản lớn cha (Parent chunk) bọc lấy child-chunk để đưa cho Judge, khắc phục triệt để lỗi đánh rơi chi tiết điều kiện (scope) như trong câu `gq05` định danh Contractor phía trên. Thêm vào đó, tôi sẽ thử nghiệm tích hợp thư viện `underthesea` thay thế Tokenizer tự động của BM25.
