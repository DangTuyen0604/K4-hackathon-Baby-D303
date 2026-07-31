# AI SPEC — Trợ lý Q&A tự học cho Lab Coach · Nhóm [XX] · Zone [X]
Hướng: [ ] A — VLearn  [x] B — Trợ lý Học viên  [ ] C — Làn mở
Loại: [x] Tối ưu tính năng có sẵn  [ ] Tính năng mới
*(Dự án khởi điểm từ 1 bản MVP có sẵn — bot gọi OpenAI quét toàn bộ cache mỗi lần hỏi, không phân quyền học. Nhóm thiết kế lại kiến trúc và bổ sung nhiều cơ chế an toàn — xem §9 Changelog.)*

---

## §1. User & Job

- **Job executor + workflow:** Học viên trong server Discord của lab/khoá học, trong lúc làm bài tập/dự án gặp vướng mắc và cần hỗ trợ nhanh mà không muốn/không thể chờ Coach rảnh để trả lời trực tiếp.
  *(Worksheet JTBD / sơ đồ workflow: [CẦN NHÓM ĐÍNH KÈM] — mình chưa có bản vẽ/worksheet của nhóm.)*

- **Core JTBD (không tên sản phẩm/AI):** Khi gặp vướng mắc trong quá trình học/làm dự án, tôi muốn nhận được câu trả lời đáng tin cậy ngay lập tức, để không phải chờ đợi hoặc làm gián đoạn tiến độ của mình và của team.

- **Problem statement (không chữ AI):** Nhiều câu hỏi của học viên là câu đã từng được hỏi và trả lời trước đó trong server, nhưng vì không có cơ chế lưu lại, Coach phải trả lời lặp đi lặp lại cùng một nội dung — vừa tốn thời gian của Coach, vừa khiến học viên phải chờ lâu hơn mức cần thiết cho những câu hỏi thực sự mới.

- **Evidence (chuẩn A và/hoặc B):**
  - Số liệu mining / khảo sát (n = ?, % xác nhận): **[CẦN NHÓM ĐIỀN]** — hiện nhóm **chưa có** log mining thực tế từ lịch sử chat hoặc khảo sát chính thức với Coach/học viên. Đây là khoảng trống cần bổ sung trước khi chốt spec, vì §1 yêu cầu bằng chứng chuẩn A/B chứ không chỉ suy luận logic.
  - ≥5 quote/ví dụ nguyên văn + nguồn: **[CẦN NHÓM ĐIỀN]** — cùng lý do trên.
  - Cách bổ sung nhanh (gợi ý, không phải bằng chứng đã có): xuất lịch sử chat của 1-2 channel hỏi đáp trong 2-4 tuần gần nhất, lọc thủ công các câu hỏi có nội dung trùng/gần trùng nhau, đếm tỷ lệ; hoặc hỏi nhanh 3-5 Coach câu "1 tuần bạn phải trả lời lại bao nhiêu câu hỏi mà bạn nhớ đã trả lời rồi".

---

## §2. Impact & quyết định chọn

- **Bảng impact ≥3 ứng viên:** **[CẦN NHÓM ĐIỀN]** — trong quá trình làm việc với mình, nhóm chỉ tập trung phát triển 1 hướng (bot Q&A tự học) ngay từ đầu, mình không có thông tin về các ứng viên tính năng khác đã được nhóm cân nhắc ở cấp sản phẩm (khác với các phương án *kỹ thuật* trong cùng 1 tính năng mà nhóm đã quyết định — ví dụ fuzzy-only vs OpenAI-only vs kết hợp 2 tầng, đã ghi trong §4b/§9).
- **Ứng viên ĐÃ LOẠI + vì sao:** **[CẦN NHÓM ĐIỀN]**
- **Ứng viên CHỌN + vì sao (bằng số):** **[CẦN NHÓM ĐIỀN]** — cần gắn với số liệu ở §1 khi đã có.

---

## §3. Giải pháp tương tự đã nghiên cứu

**[CẦN NHÓM ĐIỀN]** — mình không có thông tin nhóm đã tự khảo sát những sản phẩm/bot nào trước khi build. Gợi ý hướng tham khảo (chưa phải nghiên cứu thật, chỉ để nhóm cân nhắc điền):
- Các bot FAQ/ticket có sẵn trên Discord (ví dụ Ticket Tool, FAQ bot dạng trigger từ khoá cố định): thường trả lời theo từ khoá cứng, không hiểu ngữ nghĩa diễn đạt khác nhau — khác với cách tiếp cận fuzzy + AI của nhóm.
- Chatbot hỗ trợ học tập dùng RAG trên tài liệu khóa học: mạnh về tra cứu tài liệu tĩnh nhưng không có cơ chế "học từ xác nhận của con người" theo thời gian thực như thiết kế hiện tại.

---

## §4. Thiết kế

- **Lát cắt MỘT CÂU:** Khi một học viên @mention bot để đặt câu hỏi trong server, hệ thống quyết định tự trả lời ngay từ kho tri thức đã được Coach xác nhận nếu đủ độ tin cậy, ngược lại tạo Thread và mời Coach hỗ trợ — kết quả là học viên nhận được câu trả lời tức thì hoặc một kênh hỗ trợ rõ ràng, không bao giờ bị bỏ mặc không phản hồi.

- **Non-goals (≥3 thứ KHÔNG build):**
  1. Bot **không** tự sinh câu trả lời mới bằng suy luận của AI khi chưa từng có Coach xác nhận nội dung đó — mọi câu trả lời trong cache đều bắt nguồn từ con người, AI chỉ làm nhiệm vụ *khớp câu hỏi mới với câu đã học*, không *sáng tác* câu trả lời.
  2. **Không** xây dashboard web riêng ngoài Discord — chọn slash command nội bộ Discord để giảm hạ tầng vận hành.
  3. **Không** xử lý voice channel/giọng nói.
  4. **Không** có cơ chế tự động dọn/xoá cache định kỳ mà không có xác nhận của Coach — mọi thay đổi cache đều cần hành động rõ ràng (tick ✅, hoặc lệnh `/cache edit`/`/cache delete`).

- **Mức prototype nhắm tới:** [ ] Sketch [ ] Mock [x] Working
  Phần thật: kết nối Discord Gateway thật, gọi OpenAI API thật, đọc/ghi SQLite thật, slash command thật, đã test trực tiếp trên server thật với nhiều vòng sửa lỗi.
  Phần còn thiếu để gọi là "hoàn chỉnh": chưa có **golden set kiểm thử chính thức** (§7) và chưa có dữ liệu vận hành thật dài hạn (§1).

- **Automation:** [ ] augment [x] conditional [ ] automate
  Lý do theo cost-of-error: nếu để "automate" hoàn toàn (AI luôn tự quyết định trả lời), một câu trả lời sai sẽ trông "đáng tin" y hệt câu đúng (nhãn `🧠 [Từ bộ nhớ Bot]` không phân biệt được), khiến học viên tiếp nhận kiến thức sai mà không biết để kiểm tra lại — cost cao. Ngược lại "augment" thuần (AI chỉ gợi ý, luôn cần Coach duyệt từng câu) sẽ làm mất giá trị cốt lõi là giảm tải cho Coach với các câu hỏi lặp lại rõ ràng. Nhóm chọn **conditional**: tự động trả lời khi độ tin cậy đủ cao (ngưỡng fuzzy hoặc AI confidence), escalate cho Coach khi không chắc chắn.

### §4b. Nguyên tắc đã áp dụng (≥4)

| Nguyên tắc | Áp cụ thể vào đâu trong prototype |
|---|---|
| Abstain when uncertain (không tự trả lời khi thiếu căn cứ) | `find_in_cache()`: nếu fuzzy dưới ngưỡng và OpenAI trả `confidence: low`/`matched_id: null`, bot không đoán mà trả `None`, chuyển sang tạo Thread nhờ Coach |
| Human-in-the-loop trước khi ghi nhớ vĩnh viễn | `on_raw_reaction_add`: câu trả lời chỉ vào cache sau khi Coach chủ động thả reaction ✅ xác nhận, không tự động lưu ngay khi Coach gõ xong |
| Least privilege / phân quyền học | `is_coach()`: chỉ role được cấu hình trong `COACH_ROLE_NAME` mới "dạy" được bot; nếu chưa cấu hình, tính năng học mặc định **tắt hoàn toàn** |
| Graduated automation theo cost/độ khó | Kiến trúc 2 tầng trong `find_in_cache()`: fuzzy matching cục bộ (free, tức thì) xử lý trước, chỉ gọi OpenAI (tốn phí/độ trễ) khi thật sự cần xét ngữ nghĩa |
| Provenance transparency (minh bạch nguồn gốc) | Mọi câu trả lời từ cache đều gắn nhãn rõ `🧠 [Từ bộ nhớ Bot]`, giúp học viên phân biệt đây là câu trả lời tái sử dụng từ Coach trước đó |

---

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản (≥8)

| Lớp | Kịch bản 1 | Kịch bản 2 |
|---|---|---|
| **AI nhận diện sai câu hỏi tương tự (trông đáng tin nhưng sai)** | OpenAI chấm confidence cao cho 2 câu hỏi ngữ pháp giống nhưng ý nghĩa ngược nhau (VD "data mình tự tìm à" vs "data ai cung cấp cho mình") | Câu hỏi ngắn khiến fuzzy score trùng ngẫu nhiên vượt ngưỡng auto-match dù ngữ cảnh khác hẳn |
| **Dữ liệu cache bị dạy sai/lỗi thời** | Coach tick nhầm ✅ vào câu trả lời của người không phải Coach đang đùa trong Thread (hệ thống chỉ kiểm tra người *thả* react, chưa kiểm tra người *viết* có phải Coach) | Thông tin từng đúng nay lỗi thời (đổi deadline/quy định), Coach không hỏi lại đúng từ khoá để kích hoạt cơ chế ghi đè (upsert), cache tiếp tục phát tán thông tin cũ |
| **Hạ tầng vận hành không ổn định** | Nhiều process `bot.py` chạy song song do quên tắt bản cũ → phản hồi trùng lặp hoặc bằng code cũ (đã từng xảy ra thật trong quá trình build) | Token bị reset/hết hạn đúng lúc đang chạy, bot rớt kết nối đột ngột không có cảnh báo |
| **Hiểu sai phạm vi/ý định** | Câu hỏi quá mơ hồ, ít từ khoá (VD "sao vậy ta") vẫn lọt ngưỡng ứng viên để đưa vào OpenAI xét, tăng rủi ro chọn nhầm | Học viên hỏi ngoài phạm vi học tập (③) hoặc hỏi việc đặc thù riêng của nhóm/dự án mình (④) — bot hiện xử lý như FAQ chung, chưa phân biệt được, vẫn tạo Thread làm phiền Coach dù câu hỏi không phù hợp để cache dùng chung |

---

## §6. Bốn đường đi của trải nghiệm

- **Happy path:** Học viên @mention bot hỏi → fuzzy match ≥92% hoặc OpenAI confidence cao → bot trả lời ngay, gắn nhãn `🧠 [Từ bộ nhớ Bot]`.
- **Low-confidence (②):** Có ứng viên gần giống (≥40%) nhưng OpenAI không đủ tự tin (`confidence: low`) → bot không đoán, tạo Thread mời Coach.
- **Failure/không căn cứ (①):** Không có ứng viên nào vượt ngưỡng tối thiểu (cache rỗng hoặc hoàn toàn không liên quan) → bot tạo Thread ngay, không tốn lượt gọi AI.
- **Correction (user sửa):** Coach dùng `/cache edit` để sửa trực tiếp câu trả lời sai đã lưu, hoặc trả lời lại + tick ✅ lại để cơ chế upsert tự ghi đè bản cũ (không tạo dữ liệu trùng).
- **Khi bị đòi ngoài phạm vi (③):** Học viên hỏi việc không liên quan học tập (VD hỏi chuyện phiếm) — **gap hiện tại**: bot chưa phân biệt được, vẫn xử lý như câu hỏi bình thường và có thể tạo Thread làm phiền Coach.
- **Case đặc thù domain (④):** Câu hỏi cần ngữ cảnh riêng của từng team/dự án (VD "đề tài của team em vậy ổn không") — **gap hiện tại**: cache dùng chung cho cả server, chưa phân biệt theo từng nhóm, dễ áp nhầm câu trả lời của nhóm khác.

---

## §7. Kiểm thử

- **Chiều chất lượng + định nghĩa kiểm chứng được:** Độ chính xác của việc *nhận diện câu hỏi tương tự* — kiểm chứng bằng cách chạy `token_sort_ratio` (fuzzy) và log kết quả OpenAI trên một bộ câu hỏi test đã biết trước đáp án đúng (câu nào nên khớp với câu nào), đối chiếu với ngưỡng cấu hình.
- **Golden set (≥20 case):** Hiện có **script `test_matching.py`** làm nền, nhưng mới có **5 case mẫu** (2 nhóm câu hỏi × paraphrase) — **chưa đủ 20**, cần nhóm bổ sung thêm bằng câu hỏi thật từ server (đặt trong thư mục `eval/` theo cơ cấu hướng dẫn).
- **Quality bar:** **[CẦN NHÓM CHỐT]** — mình đề xuất khung để nhóm điền số cụ thể: "Đạt khi ≥ ___% câu hỏi paraphrase trong golden set được nhận đúng ở tầng phù hợp (auto-match hoặc OpenAI xét), và 0% trường hợp trả lời sai nhưng gắn nhãn tự tin cao (auto-match nhầm)."
- **Kết quả các lượt chạy (baseline thật, 31/7):**

| Lượt chạy | Tổng case | Auto-match (tầng 1) | Cần OpenAI (tầng 2) | Không khớp |
|---|---|---|---|---|
| Baseline (5 case mẫu) | 5 | 0/5 (0%) | 5/5 (100%) | 0/5 (0%) |

  *(Bảng này cần cập nhật thêm các lượt chạy tiếp theo khi golden set mở rộng lên ≥20 case, trước CP6.)*

---

## §8. Phân công & kế hoạch

- **Phân công có tên (spec / evidence / prompt / code / demo):** **[CẦN NHÓM ĐIỀN]** — mình không có thông tin thành viên nhóm để gán vai trò.
- **Willing users (≥3 tên) + kế hoạch vòng validation CP5:** **[CẦN NHÓM ĐIỀN]**
- **Multi-prototype (nếu làm):** Hiện chỉ có 1 phương án được triển khai đầy đủ (kiến trúc 2 tầng fuzzy + OpenAI). Nếu nhóm muốn làm multi-prototype để so sánh, có thể cân nhắc trục khác biệt: (a) fuzzy-only vs (b) 2-tầng hiện tại — đã có sẵn code để dựng lại phương án (a) nếu cần đối chứng, vì đây chính là bản v2.0 trong changelog.

---

## §9. Changelog

| Thời điểm | Đổi gì | Vì sao (trỏ về feedback/case nào) |
|---|---|---|
| v1.0 (bản gốc) | Dùng OpenAI quét toàn bộ cache mỗi lần hỏi; ai react ✅ cũng lưu được | Baseline ban đầu, chưa qua kiểm thử |
| v2.0 | Chuyển sang fuzzy matching cục bộ (rapidfuzz); thêm phân quyền Coach; không học từ tin nhắn bot khác | Tối ưu chi phí/tốc độ; ngăn dữ liệu bị dạy sai |
| v2.1 | Khôi phục OpenAI làm tầng ngữ nghĩa thứ 2, chỉ xét trên ≤12 ứng viên đã lọc | Fuzzy đơn thuần bỏ sót câu hỏi diễn đạt khác nghĩa giống (xem §7 baseline: 5/5 case cần tầng 2) |
| v2.2 | Thêm log chi tiết + print thô không qua logging | Debug tình trạng bot "im lặng" không phản hồi khi test thực tế |
| v2.3 | Sửa regex trích sai câu hỏi gốc (nhầm dấu `>` trong mention) | Phát hiện qua log thật: câu hỏi trích ra chỉ còn `":**"` |
| v2.4 | Thêm cơ chế upsert (ghi đè thay vì tạo dòng trùng) | Case thật: Coach tick nhầm câu sai, tick lại vẫn ra câu sai cũ do dữ liệu trùng |
| v2.5 | Chỉ @mention trực tiếp mới kích hoạt bot (bỏ điều kiện dấu `?`/"Bot ơi") | Case thật: bot tạo Thread nhầm khi có người ping `@everyone` hoặc ping người khác kèm `?` |
| v2.6 | Thêm bảng `pending_threads`, chống tạo Thread trùng cho câu hỏi tương tự đang chờ xử lý | Giảm tải Coach khi nhiều người hỏi cùng lúc trước khi có câu trả lời được xác nhận |
| v2.7 | Thêm slash command `/cache list/view/search/edit/delete` cho Coach | Coach cần tự kiểm soát chất lượng cache mà không phải thao tác trực tiếp SQL |
