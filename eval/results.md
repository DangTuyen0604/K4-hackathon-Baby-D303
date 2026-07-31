# Kết quả đánh giá ViniBot

- Thời điểm chạy: `2026-07-31T16:35:17.238490+07:00`
- Model: `google/gemini-2.5-flash` qua OpenRouter
- Golden set: `ViniBot announcement grounding eval` v1
- Tổng kết: **6/6 case đạt**

## Kết quả từng case

| Case | Chế độ | Số lần chạy | Kết quả | ID nguồn ổn định |
|---|---|---:|---|---|
| official_source_filter | daily_summary | 1 | Đạt | Có |
| ignore_staff_chatter | daily_summary | 1 | Đạt | Có |
| latest_update_wins | latest_announcements | 1 | Đạt | Có |
| preserve_deadline_and_link | specific_question | 1 | Đạt | Có |
| no_official_data | daily_summary | 1 | Đạt | Có |
| stable_repeated_answer | specific_question | 3 | Đạt | Có |

## Trả lời các câu hỏi đánh giá

### Bot có lấy đúng thông báo chính thức không?

**Đạt (1/1 case).** Case kiểm tra trộn tin từ ADMIN, LEARNER và kênh không chính thức; chỉ ID thuộc role và kênh chính thức được phép xuất hiện trong kết quả.

### Có bỏ qua chat linh tinh không?

**Đạt (1/1 case).** Tin cảm ơn của staff, kể cả có ping mọi người, không được coi là thông báo nếu thiếu tín hiệu logistics.

### Có dùng thông báo mới nhất thay cho thông báo cũ không?

**Đạt (1/1 case).** Case Workshop có bản 18:00 và bản cập nhật mới hơn sang 20:00; eval yêu cầu chỉ dùng message ID của bản cập nhật.

### Có bịa deadline, link hoặc thời gian không?

**Đạt (4/4 case).** Runner so khớp nguyên văn các facts bắt buộc, cấm facts đã khai báo sai và đánh dấu mọi thời gian/ngày/URL không có trong nguồn đã chọn là unexpected_facts.

### Khi không có dữ liệu, bot có biết nói “không tìm thấy” không?

**Đạt (1/1 case).** Case không dữ liệu chỉ chứa tin đồn của learner và chat thường của staff; kết quả phải có thông điệp không tìm thấy và không có source ID.

### Kết quả có ổn định qua nhiều lần chạy không?

**Đạt (1/1 case).** Case stability được gọi 3 lần. Tiêu chí ổn định là cùng tập message ID đã xác thực và mọi lần đều qua kiểm tra facts; cách diễn đạt có thể khác nhau.

## Chạy lại

```powershell
.\.venv\Scripts\python.exe eval\run_eval.py
```

Kết quả chi tiết từng lần gọi model nằm trong `raw_results.json`. File này không chứa API key hoặc Discord token.
