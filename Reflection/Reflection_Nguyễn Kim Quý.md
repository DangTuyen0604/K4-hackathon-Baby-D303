# Reflection — Nguyễn Kim Quý (T039 - 01456)

## 1. Phần mình phụ trách chính

Mình trực tiếp làm leader và chạy code, kiểm thử bot BABY trên server thật: đọc log terminal, thao tác thật trên Discord (mention bot, trả lời trong Thread, thả reaction ✅), và báo lại chính xác từng hiện tượng gặp phải để xác định nguyên nhân. Mình cũng là người đưa ra các quyết định thiết kế quan trọng: giữ lại OpenAI làm tầng xét ngữ nghĩa thay vì chỉ dùng fuzzy matching, giới hạn chỉ Coach gõ tay mới được tính là câu trả lời hợp lệ (không chấp nhận câu trả lời từ bot AI khác dù có tick ✅), và giới hạn bot chỉ phản hồi khi bị @mention trực tiếp...

## 2. Khó khăn lớn nhất gặp phải

Khó khăn lớn nhất là chưa phân công công việc được các thành viên trong nhóm nên ôm đồm nhiều công việc. Việc chưa từng làm việc với Bot trong Discord cũng khiến em gặp phải khó khăn trong khi triển khai.

## 3. Nếu làm lại từ đầu, mình sẽ làm khác đi điều gì

Phân công công việc cho nhóm tốt hơn.

## 4. Bài học lớn nhất về thiết kế sản phẩm có AI

Một điều nổi bật qua quá trình build là ranh giới rõ ràng giữa "AI tự động hoàn toàn" và "AI hỗ trợ, con người vẫn quyết định" — ví dụ việc yêu cầu Coach phải chủ động thả tick mới lưu vào cache, hay việcgiới hạn chỉ Coach gõ tay mới được tính hợp lệ. Bạn có thể viết về việc bản
thân đã hiểu ra điều gì về mức độ tin tưởng nên đặt vào AI, hoặc về việc kiểm thử/log chi tiết quan trọng thế nào khi AI là một phần của hệ thống có nhiều bước xử lý nối tiếp nhau.
