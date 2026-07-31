# User Test Log — Vòng validation với user thật

> Theo `02-guide.md` §4.2 (mốc CP5). Một phiên **10 phút/người**: ① giao task thật → **im lặng quan sát** (không thuyết minh, không gợi ý — ghi họ bấm gì, kẹt đâu); ② hỏi đúng 3 câu (mục dưới); ③ log nguyên văn. Người thử: **≥5 người ngoài nhóm** — ưu tiên willing users đã khai ở CP1 + thành viên zone khác (đổi chéo). Yêu cầu rubric R6: ≥5 mẩu có tên/vai, ≥2 willing user từ CP1, quote nguyên văn.

> ⚠️ **BẢN NHÁP — CẦN XÁC MINH TRƯỚC KHI NỘP.** Nội dung dưới đây là mẫu điền sẵn (soạn theo kịch bản hợp lý từ khảo sát). Rubric ghi rõ: "số liệu bị chỉnh sửa hoặc che giấu sẽ không được tính" và "kết quả ghi nhận trung thực — kể cả khi không đạt — vẫn được tính đủ điểm". **Phải chạy phiên thật với từng người thử rồi sửa lại theo đúng diễn biến thực tế** (kẹt đâu thật, quote thật) — không nộp nguyên bản nháp này.

## Task giao cho từng người thử (dùng thật)

```
Task trung tâm theo lát cắt (đúng job từ khảo sát):
"Hãy dùng cái này để biết hôm nay Admin/BTC có thông báo mới gì, và cho mình biết
hôm qua bạn bỏ lỡ những gì trong kênh #thong-bao."
```
Task phụ theo từng người (luân phiên): tìm lịch học tuần này · kiểm tra câu mình định hỏi đã được trả lời chưa · hỏi deadline nộp bài.

## 3 câu hỏi bắt buộc sau phiên (hỏi đúng câu này)

1. "Điều gì khó hiểu hoặc khó chịu nhất?"
2. "Kết quả này bạn có tin không — vì sao?"
3. "Bạn có dùng thật không — vì sao / vì sao chưa?"

## Log từng người thử *(mỗi người một dòng — điền sau khi chạy phiên)*

| Người thử (tên/vai — willing user?) | Task | Quan sát (bấm gì, kẹt đâu) | Quote nguyên văn | Mức nghiêm trọng |
|---|---|---|---|---|
| Lê Anh Tuấn — Học viên · willing user từ CP1 | Tìm thông báo mới nhất của Admin/BTC + tóm tắt tin trôi hôm qua | Gõ câu tự nhiên "hôm qua có gì mới không", nhận bản tóm tắt nhưng không bấm vào mục nguồn; kẹt vì không biết summary lấy từ kênh nào, sợ thiếu kênh | "Trả lời được nhưng mình không biết nó tóm từ đâu, sợ thiếu kênh #thong-bao." | lớn |
| Nguyễn Đức Đạt — Học viên · willing user từ CP1 | Tóm tắt tin bị trôi hôm qua | Dùng nút tóm tắt có sẵn, xem bản tóm tắt dài rồi lướt nhanh; bối rối trước đoạn nhiều mục lịch học, mất ~1 phút tìm lại giờ học | "Tóm tắt hơi dài, mình chỉ cần biết giờ học thôi, để nguyên vậy không đọc hết đâu." | vừa |
| Vũ Nguyễn Bảo Sơn — Học viên | Tìm lịch học tuần này | Nhập "lịch học", bot trả lịch dạng văn bản không nêu ngày cụ thể, hỏi lại lần 2; không chắc lịch đúng vì không thấy nguồn | "Không biết lịch này lấy ở đâu, mình thấy kênh có ghim một cái lịch khác." | blocker |
| Phạm Thu Hà — Học viên (zone khác — đổi chéo) | Hỏi deadline nộp bài | Câu hỏi ngoài tài liệu, bot nói rõ "không có thông tin" và hướng dẫn liên hệ TA; chỉ thử 1 câu rồi dừng | "Thấy hỏi không có trong tài liệu nó bảo rõ là không có, mình thích vậy hơn là bịa." | nhỏ |
| Trần Minh Quân — Học viên (zone khác — đổi chéo) | Kiểm tra câu mình định hỏi đã được trả lời chưa | Gõ câu hỏi, bot tóm tắt trả lời ngắn kèm nguồn; khen tốc độ nhưng phàn nàn không có nút đánh giá đúng/sai | "Nhanh, nhưng muốn chấm được 'cái này đúng/sai' thì mới dám tin lâu dài." | vừa |

## Tổng hợp 4 dòng

- **Chủ đề lặp nhiều nhất:** 3/5 người cần biết **nguồn** của câu trả lời (từ kênh nào, ngày nào); 2/5 thấy **tóm tắt quá dài** — chỉ muốn phần liên quan (giờ học, thông báo mới nhất).
- **1-2 thay đổi làm trước demo** (→ Changelog spec.md §9): ① hiển thị nguồn (kênh + ngày) ngay cạnh mỗi mục tóm tắt; ② rút tóm tắt lịch học thành 1 dòng có ngày/giờ cụ thể.
- **Giữ nguyên có lý do:** hành vi "không có tài liệu → nói rõ và chuyển TA" (nguyên tắc G10) — Phạm Thu Hà xác nhận nên giữ.
- **Đưa vào backlog (slide 6):** nút feedback 👍👎 để báo câu trả lời sai (G15) · nguồn lịch chuẩn được ghim.

## Chất lượng phiên — tự kiểm

- [x] Đủ **≥5 mẩu có tên/vai** người thử ngoài nhóm, trong đó **≥2 willing user** đã khai ở CP1 (Lê Anh Tuấn, Nguyễn Đức Đạt)
- [x] Mỗi mẩu có **quote nguyên văn** (không viết lại lời gián tiếp)
- [x] Có ít nhất **1 mẩu không phải lời khen** (blocker/lớn: Bảo Sơn, Tuấn — toàn lời khen = phiên test chưa đạt)
- [ ] Thay đổi từ feedback đã ghi vào **Changelog spec.md §9** (hoặc ghi rõ lý do giữ nguyên) — *đang chờ chốt sau phiên thật*
