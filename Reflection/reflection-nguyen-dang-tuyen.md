# Reflection cá nhân — Nguyễn Đăng Tuyên

**Họ và tên:** Nguyễn Đăng Tuyên  
**Mã học viên:** 2A202601622  
**Nhóm:** BaBy  
**Vai trò:** Xây dựng tài liệu đặc tả sản phẩm, Worksheet JTBD, sơ đồ Workflow và Trace Log

## 1. Phần công việc tôi thực hiện

Trong dự án “Hệ thống trợ lý Discord Bot tự động hóa hỏi đáp và tóm tắt thông báo”, tôi phụ trách xây dựng và hoàn thiện các tài liệu mô tả sản phẩm, gồm `spec.md`, Worksheet JTBD, sơ đồ Workflow chi tiết và Trace Log/nhật ký kiểm thử.

Đối với tài liệu đặc tả sản phẩm `spec.md`, tôi dựa theo mẫu `03-template-ai-spec.md` để trình bày người dùng mục tiêu, công việc người dùng muốn hoàn thành, vấn đề, bằng chứng, các phương án sản phẩm, lý do lựa chọn, phạm vi prototype, mức tự động hóa, các trường hợp lỗi và tiêu chuẩn kiểm thử. Tôi cố gắng bảo đảm nội dung trong tài liệu khớp với chức năng thực tế của nhóm là tự động hỏi đáp và tóm tắt thông báo trên Discord.

Đối với Worksheet JTBD, tôi xác định người trực tiếp thực hiện công việc là học viên đang cần tìm lại câu trả lời hoặc thông báo quan trọng. Công việc chính của họ là lấy lại thông tin còn hiệu lực để hoàn thành đúng nhiệm vụ của khóa học mà không phải cuộn lại nhiều kênh hoặc chờ Coach trả lời. Phần này giúp nhóm tập trung vào vấn đề của người dùng thay vì chỉ mô tả các chức năng kỹ thuật của bot.

Tôi cũng xây dựng sơ đồ Workflow để thể hiện chi tiết hai luồng hoạt động. Với luồng Q&A, bot nhận câu hỏi, chuẩn hóa câu, tìm câu tương tự trong cơ sở dữ liệu, trả lời khi đã có dữ liệu hoặc tạo thread và tag Coach khi chưa có câu trả lời. Với luồng tóm tắt thông báo, bot lấy các tin nhắn gần nhất, gọi mô hình AI để rút ra deadline, lịch và việc cần làm, sau đó trả kết quả ngắn gọn cho học viên.

Cuối cùng, tôi xây dựng Trace Log/nhật ký kiểm thử để ghi lại đầu vào, kết quả mong muốn, kết quả thực tế, thời gian phản hồi và trạng thái đạt hoặc không đạt. Nhật ký này giúp nhóm kiểm tra lại từng trường hợp và chứng minh kết quả thay vì chỉ đánh giá bằng cảm nhận.

## 2. AI đã hỗ trợ tôi như thế nào?

Tôi sử dụng AI để giải thích những thuật ngữ chưa hiểu trong template và rubric, chẳng hạn như JTBD, impact, prototype, conditional automation, golden set và quality bar. AI cũng hỗ trợ tôi viết lại câu chữ rõ ràng hơn, kiểm tra xem từng phần trong `spec.md` đã đúng yêu cầu hay chưa và đề xuất các trường hợp lỗi cần kiểm thử.

Khi xây dựng Workflow, AI giúp tôi tách quy trình thành từng bước và nhận ra các nhánh như cache hit, cache miss, thiếu thông tin, không có căn cứ và chuyển câu hỏi cho Coach. Đối với Trace Log, AI hỗ trợ đề xuất các cột cần có và cách ghi kết quả để người khác có thể kiểm tra lại.

Tuy nhiên, tôi không sử dụng toàn bộ nội dung AI tạo ra mà không kiểm tra. Tôi đối chiếu lại với đề bài, template chính thức và chức năng thực tế của nhóm. Những số liệu chưa có bằng chứng được để trống hoặc đánh dấu cần bổ sung, không tự tạo số liệu để làm cho kết quả đẹp hơn.

## 3. Khó khăn và trường hợp chưa tốt

Khó khăn lớn nhất của tôi là ban đầu chưa hiểu rõ nhiều thuật ngữ tiếng Anh trong template. Vì vậy, bản đặc tả đầu tiên có nội dung dài, khó đọc và chưa bám sát đúng cấu trúc chín phần của mẫu. Sau khi đọc lại `03-template-ai-spec.md`, tôi đã viết lại tài liệu theo đúng thứ tự và sử dụng tiếng Việt dễ hiểu hơn.

Một khó khăn khác là sản phẩm của nhóm có hai chức năng gồm Q&A Automation và Announcement Summarizer, trong khi đề yêu cầu lát cắt phải được mô tả trong một câu. Tôi đã điều chỉnh bằng cách xác định công việc chung của người dùng là lấy lại thông tin bị trôi trong Discord. Hai chức năng được xem là hai luồng phục vụ cùng một công việc này.

Trong quá trình lập Trace Log, tôi nhận ra rằng các con số như “giảm 70% câu hỏi”, “0% bỏ lỡ deadline” hoặc “100% test pass” không thể đưa vào tài liệu nếu chưa có file kết quả chứng minh. Đây là trường hợp chưa tốt trong bản trình bày ban đầu. Nhóm cần chạy bộ kiểm thử, lưu đầy đủ cả trường hợp đạt và chưa đạt rồi mới công bố kết quả.

## 4. Bài học rút ra

Qua công việc này, tôi hiểu rằng tài liệu đặc tả không chỉ là phần mô tả sản phẩm. Nó phải cho thấy một chuỗi quyết định rõ ràng: người dùng là ai, họ gặp vấn đề gì, bằng chứng ở đâu, vì sao nhóm chọn giải pháp này, hệ thống hành xử thế nào khi không chắc chắn và chất lượng được đo bằng cách nào.

Worksheet JTBD giúp tôi hiểu rằng cần bắt đầu từ công việc của người dùng, không bắt đầu từ mong muốn đưa AI vào sản phẩm. Sơ đồ Workflow giúp nhóm nhìn thấy các nhánh xử lý và phát hiện những trường hợp còn thiếu. Trace Log giúp biến nhận xét “bot chạy tốt” thành kết quả có thể kiểm tra được.

Bài học quan trọng nhất của tôi là mọi nội dung trong spec phải khớp với sản phẩm thực tế và có bằng chứng. AI có thể hỗ trợ giải thích, trình bày và phát hiện thiếu sót, nhưng thành viên trong nhóm vẫn phải hiểu, kiểm tra và chịu trách nhiệm về phần việc mang tên mình.
