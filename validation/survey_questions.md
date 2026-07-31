# Khảo sát — Log câu hỏi & phương pháp

> Đường bằng chứng **A (khảo sát)** theo `02-guide.md` §1.3: hỏi về tình huống thật, ghi log đầy đủ câu đã hỏi + từng câu trả lời nguyên văn. Dữ liệu thô: `survey_responses.csv` (mã HV01-HV20, đã ẩn danh — không ghi thông tin định danh).

## Thông tin chung

- **Mục tiêu:** xác minh pain của học viên khi dùng Discord trong học tập (tin nhắn trôi / khó tìm / lỡ thông báo), đo mức độ & tần suất.
- **Người trả lời:** Học viên khoá (ngoài nhóm), n = **20** phiếu (19 phiếu có đầy đủ dữ liệu + 1 phiếu trống HV01).
- **Thời gian thu:** 30/07/2026 15:24–20:57.
- **Hình thức:** gửi link khảo sát qua Discord khoá, trả lời ẩn danh, câu hỏi đóng + 1 ô tự nhập.
- **Phương pháp đếm:** đếm thủ công từng dòng trong CSV; câu nhiều lựa chọn đếm mỗi lựa chọn 1 lần/phiếu; phiếu trống HV01 không tính vào tổng (n tính trên phiếu hợp lệ).

## Câu đã hỏi (nguyên văn)

1. **Bạn là?** → *Học viên / Giảng viên / Trợ giảng (TA) / Admin-BTC*
2. **Tần suất sử dụng Discord của bạn trong học tập** → *Hiếm khi / Thỉnh thoảng (vài lần mỗi tuần) / Thường xuyên (hàng ngày)*
3. **Mục đích sử dụng Discord chính của bạn** (nhiều lựa chọn) → *Trao đổi bài học / Nhận thông báo từ giảng viên-trợ giảng / Tìm kiếm tài liệu cũ / Kết nối với bạn học / Chơi*
4. **Những khó khăn bạn thường gặp khi sử dụng Discord** (Dành cho Học viên, nhiều lựa chọn) → *Tin nhắn bị trôi / Khó tìm thông tin / Bỏ lỡ thông báo / Câu hỏi không được trả lời / Có quá nhiều câu hỏi trùng lặp*
5. **Trung bình bạn mất bao lâu để tìm kiếm thông tin cần thiết trên Discord?** → *Dưới 1 phút / 1 - 5 phút / Trên 5 phút*
6. **AI nên hỗ trợ những gì cho bạn?** (nhiều lựa chọn) → *Cập nhật thông tin mới nhất từ Admin và BTC / Tóm tắt tin nhắn bị trôi / Thông báo lịch học*
7. **Khó khăn lớn nhất của bạn khi học trên Discord là gì?** (Dành cho Học viên, tự nhập)

## Kết quả đếm (n = 19 phiếu hợp lệ)

### Q4 · Khó khăn thường gặp (nhiều lựa chọn — % trên 19 phiếu)
| Khó khăn | Số phiếu | % |
|---|---|---|
| Tin nhắn bị trôi | 15 | 78,9% |
| Khó tìm thông tin | 14 | 73,7% |
| Bỏ lỡ thông báo | 14 | 73,7% |
| Câu hỏi không được trả lời | 8 | 42,1% |
| Có quá nhiều câu hỏi trùng lặp | 7 | 36,8% |

### Q5 · Thời gian tìm thông tin
| Mức | Số phiếu | % |
|---|---|---|
| Dưới 1 phút | 4 | 21,1% |
| 1 - 5 phút | 8 | 42,1% |
| Trên 5 phút | 7 | 36,8% |

→ 78,9% học viên mất **trên 1 phút** mỗi lần tìm thông tin; 36,8% mất **trên 5 phút**.

### Q6 · AI nên hỗ trợ (nhiều lựa chọn — % trên 19 phiếu)
| Đề xuất | Số phiếu | % |
|---|---|---|
| Tóm tắt tin nhắn bị trôi | 17 | 89,5% |
| Cập nhật thông tin mới nhất từ Admin và BTC | 13 | 68,4% |
| Thông báo lịch học | 9 | 47,4% |

### Q2 · Tần suất
Thường xuyên (hàng ngày): 16/19 (84,2%) · Thỉnh thoảng: 1/19 · Hiếm khi: 2/19.

### Q7 · Khó khăn lớn nhất (tự nhập — trích nguyên văn)
- HV04: "trôi thông tin"
- HV11: "Khó tìm tài nguyên"
- HV16: "Trôi thông báo"
- HV19: "Quá nhiều thông tin"
- HV02: "Không" · HV03: "không rõ" (13 phiếu không trả lời câu này)

## Ghi chú

- **Đạt chuẩn A:** n = 20 ≥ 20 người ngoài nhóm · khó khăn top-1 "Tin nhắn bị trôi" 78,9% ≥ 50% · log đầy đủ câu hỏi + câu trả lời (CSV). Kèm đường B (mining chatlog) khuyến nghị để chứng minh pain tồn tại trong data.
- Quote nguyên văn từ các phiếu hợp lệ có mã HV tương ứng để trích dẫn vào `spec.md` §1.
