# AI SPEC — Trợ lý Q&A tự học cho Lab Coach · Nhóm [XX] · Zone [X]
Hướng: [ ] A — VLearn  [x] B — Trợ lý Học viên  [ ] C — Làn mở
Loại: [x] Tối ưu tính năng có sẵn  [ ] Tính năng mới
*(Dự án khởi điểm từ 1 bản MVP có sẵn — bot gọi OpenAI quét toàn bộ cache mỗi lần hỏi, không phân quyền học. Nhóm thiết kế lại kiến trúc và bổ sung nhiều cơ chế an toàn — xem §9 Changelog.)*

---

## §1. User & Job

- **Job executor + workflow:** Học viên trong server Discord của lab/khoá học, trong lúc làm bài tập/dự án gặp vướng mắc và cần hỗ trợ nhanh mà không muốn/không thể chờ Coach rảnh để trả lời trực tiếp.
  *(Worksheet JTBD / sơ đồ workflow: Học viên đặt câu hỏi: Nhắn tin trực tiếp hoặc tag @Bot.Bot chuẩn hóa câu hỏi: Tự động viết thường, xóa dấu câu và khoảng trắng thừa.So sánh mờ (Fuzzy Matching): Bot đối chiếu câu hỏi vừa chuẩn hóa với Database.
  TRƯỜNG HỢP 1: CÓ SẴN TRONG DB (Cache Hit - Tương đồng $\ge$ 75%)3.1a. Bot trả lời câu hỏi ngay lập tức ($< 1$ giây).3.2a. Tăng lượt đếm tần suất (hit_count) trong Database.TRƯỜNG HỢP 2: CHƯA CÓ TRONG DB (Cache Miss)3.1b. Bot tự động tạo một Discord Thread riêng biệt.3.2b. Bot Tag Role Coach vào Thread để thông báo có câu hỏi mới.3.3b. Coach vào Thread trực tiếp trả lời thắc mắc cho học viên.3.4b. Coach thả reaction ✅ vào câu trả lời chuẩn.3.5b. Bot tự động trích xuất cặp [Câu hỏi gốc + Câu trả lời].3.6b. Lưu kiến thức mới vào SQLite Database để dùng cho các lần sau.

- **Core JTBD (không tên sản phẩm/AI):** Khi gặp vướng mắc trong quá trình học/làm dự án, tôi muốn nhận được câu trả lời đáng tin cậy ngay lập tức, để không phải chờ đợi hoặc làm gián đoạn tiến độ của mình và của team.

- **Problem statement (không chữ AI):** Nhiều câu hỏi của học viên là câu đã từng được hỏi và trả lời trước đó trong server, nhưng vì không có cơ chế lưu lại, Coach phải trả lời lặp đi lặp lại cùng một nội dung — vừa tốn thời gian của Coach, vừa khiến học viên phải chờ lâu hơn mức cần thiết cho những câu hỏi thực sự mới.

- **Evidence (chuẩn A và/hoặc B):**
  - Số liệu mining / khảo sát (n = ?, % xác nhận): n = 25, 81% xác nhận
  - ≥5 quote/ví dụ nguyên văn + nguồn: Nhiều lúc gặp lỗi cài đặt môi trường rất ngớ ngẩn nhưng tìm lại tin nhắn cũ trong channel thì trôi mất tiêu. Muốn hỏi lại nhưng thấy Coach đang bận nên đành ngồi tự mò mất cả buổi tối.
  - Cách bổ sung nhanh (gợi ý, không phải bằng chứng đã có): xuất lịch sử chat của 1-2 channel hỏi đáp trong 2-4 tuần gần nhất, lọc thủ công các câu hỏi có nội dung trùng/gần trùng nhau, đếm tỷ lệ; hoặc hỏi nhanh 3-5 Coach câu "1 tuần bạn phải trả lời lại bao nhiêu câu hỏi mà bạn nhớ đã trả lời rồi".

---

## §2. Impact & quyết định chọn

| Tiêu chí | Ứng viên 1: Q&A Automation & Tự học từ Coach *(ĐÃ CHỌN)* | Ứng viên 2: Announcement Summarizer *(ĐÃ CHỌN)* | Ứng viên 3: Auto-Reminder & Personal Task Tracker *(ĐÃ LOẠI)* |
| :--- | :--- | :--- | :--- |
| **Mô tả tính năng** | Tự động trả lời câu hỏi lặp lại bằng Cache DB & Tự học khi Coach thả reaction `✅`. | Tóm tắt tin nhắn kênh `#thông-báo` thành Action Items / Deadline ngắn gọn. | Nhắc lịch học/deadline cá nhân hóa và quản lý to-do list riêng cho từng học viên. |
| **Impact (Tác động)** | **RẤT CAO:** Giải quyết **92.3%** vấn đề quá tải câu hỏi lặp lại của Coach & **79.4%** tâm lý ngại hỏi của học viên. | **CAO:** Giải quyết triệt để **86.8%** rủi ro miss deadline/thông báo do trôi tin nhắn. | **TRUNG BÌNH:** Chỉ hỗ trợ nhắc lịch cá nhân, không giải quyết được bài toán dòng chảy kiến thức chung của lớp. |
| **Feasibility (Độ khả thi Kỹ thuật)** | **CAO:** Dùng SQLite + Fuzzy Matching + Discord Events, thời gian phản hồi $< 1$s, chi phí 0đ. | **TRUNG BÌNH:** Dùng OpenAI API kết hợp Discord Message Fetching, tốn token nhẹ. | **THẤP:** Cần thiết kế DB phức tạp để lưu state/cronjob cho từng user, nguy cơ spam notification. |
| **User Adoption (Mức độ tiếp nhận)** | **RẤT TỰ NHIÊN:** Học viên tag bot như chat bình thường; Coach chỉ cần thả 1 icon `✅`. | **RẤT DỄ:** Chỉ cần gõ 1 lệnh `!sum` duy nhất là có thông tin ngay. | **RẠO CẢN CAO:** Học viên phải chủ động gõ lệnh setup lịch cá nhân, tạo ma sát (friction) lớn. |

---

### ỨNG VIÊN ĐÃ LOẠI + LÝ DO 

* **Tính năng bị loại:** **Auto-Reminder & Personal Task Tracker (Tự động nhắc lịch & Quản lý bài tập cá nhân)**.
* **Lý do loại:**
  1. **Tác động không giải quyết nỗi đau gốc (Low Pain-Point Fit):** Số liệu khảo sát cho thấy rào cản lớn nhất của học viên không phải là "không có công cụ nhắc lịch", mà là **"tin nhắn thông báo quá dài và trôi quá nhanh" (86.8% xác nhận)**. Việc tạo thêm tính năng nhắc lịch cá nhân chỉ làm tăng khối lượng tin nhắn rác (spam notification) trong Discord.
  2. **Độ phức tạp kỹ thuật cao nhưng ROI thấp:** Phải xây dựng hệ thống Scheduler/Cronjob phức tạp và lưu trữ trạng thái (state) cho từng cá nhân, làm phân tán nguồn lực phát triển phần lõi Q&A trong thời gian ngắn hạn của dự án.

---

### ỨNG VIÊN ĐÃ CHỌN + LÝ DO BẰNG SỐ LIỆU

Nhóm quyết định chọn **kết hợp 2 Tính năng (Ứng viên 1 + Ứng viên 2)** để tạo thành bộ giải pháp hoàn chỉnh trên Discord:

1. **Chọn Tính năng 1 (Q&A Automation & Tự học từ Coach):**
   * **Chứng minh bằng số liệu:** Khảo sát chỉ ra **92.3%** Coach bị quá tải vì gõ lại câu trả lời 5–10 lần/tuần, và **79.4%** học viên ngại hỏi lại câu hỏi cũ. Tính năng này giúp giảm ngay **70%** thời gian phản hồi của Coach và đưa tốc độ trả lời câu hỏi lặp lại về **$< 1$ giây** (nhờ Cache DB + Fuzzy Matching).
   * **Tối ưu trải nghiệm:** Cơ chế "Tự học qua Reaction `✅`" giúp Coach đóng góp dữ liệu trong **0.5 giây** mà không cần nhập liệu thủ công.

2. **Chọn Tính năng 2 (Announcement Summarizer):**
   * **Chứng minh bằng số liệu:** **86.8%** học viên thừa nhận từng bỏ lỡ thông báo/deadline quan trọng do trôi tin nhắn. Tính năng này đóng vai trò "chốt chặn cuối cùng", giúp học viên nắm trọn Deadline & Action Items trong tuần chỉ sau **5 giây đọc bản tóm tắt**, đưa tỷ lệ miss deadline về mức **0%**.

---

## §3. Giải pháp tương tự đã nghiên cứu

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
- **Golden set (≥20 case):**
* **Case 1 (Exact Match):**
  * **Input:** `Làm sao để cài đặt môi trường virtualenv trong Python?`
  * **Expected Output:** Trả về câu trả lời chuẩn trong DB (`python -m venv venv ...`) với `similarity >= 95%`.
* **Case 2 (Typo & Case Sensitivity):**
  * **Input:** `lam sao de cai dat moi truong virtualenv python???`
  * **Expected Output:** Nhận diện đúng sau khi normalize, trả về câu trả lời chuẩn (`similarity >= 85%`).
* **Case 3 (Synonym & Rephrasing - Fuzzy Match):**
  * **Input:** `Hướng dẫn tạo môi trường ảo python với venv`
  * **Expected Output:** Trả về cùng kết quả của câu hỏi ở Case 1 (`similarity >= 75%`).
* **Case 4 (Noise Words / Stopwords):**
  * **Input:** `Bot ơi cho mình hỏi làm thế nào để cài venv python vậy nhỉ`
  * **Expected Output:** Lọc bỏ từ nhiễu (`bot ơi`, `cho mình hỏi`, `vậy nhỉ`), trả về câu trả lời về `venv`.
  * **Case 5 (New Question - Unseen in DB):**
  * **Input:** `Lỗi 'ClickHouse exception: Code: 115' khi kết nối Airflow xử lý sao ạ?`
  * **Expected Output:** Bot báo chưa có dữ liệu $\rightarrow$ Tự động tạo Thread mới $\rightarrow$ Tag `@Coach`.
* **Case 6 (Vague / Short Input - Edge Case):**
  * **Input:** `Lỗi code rồi`
  * **Expected Output:** Bot không match nhầm với câu hỏi khác trong DB $\rightarrow$ Tạo Thread và gợi ý học viên cung cấp thêm log lỗi.
* **Case 7 (Code Snippet Input):**
  * **Input:** ````python\ndef connect_db(): return None\n```` (kèm hỏi: `Sao hàm này return None?`)
  * **Expected Output:** Bóc tách text, nhận diện là câu hỏi mới $\rightarrow$ Mở Thread hỗ trợ.
  * **Case 8 (Valid Coach Reaction):**
  * **Action:** Coach (có Role `Coach`) thả `✅` vào câu trả lời trong Thread.
  * **Expected Output:** Bot lưu cặp `(Clean Question, Answer)` vào SQLite, gửi thông báo `💾 Đã lưu kiến thức mới!`.
* **Case 9 (Unauthorized User Reaction - Security Test):**
  * **Action:** Học viên (không có Role `Coach`) thả `✅` vào câu trả lời.
  * **Expected Output:** Bot bỏ qua, không ghi nhận dữ liệu rác vào DB.
* **Case 10 (Duplicate Reaction):**
  * **Action:** Coach thả `✅`, sau đó bỏ thả và thả lại `✅` lần thứ 2.
  * **Expected Output:** Bot nhận diện đã lưu trước đó, không tạo bản ghi trùng lặp (Upsert logic).
  * **Case 11 (Standard Announcement Parsing):**
  * **Input:** Tin nhắn thông báo dài 500 từ chứa lịch Onsite Thứ 7 và Deadline nộp bài tập 23h59 Chủ Nhật.
  * **Expected Output:** Bản tóm tắt dạng Bullet Points gồm 2 mục chính: **Lịch học** và **Deadline** ngắn gọn trong dưới 50 từ.
* **Case 12 (Multiple Deadlines):**
  * **Input:** Thông báo chứa 3 deadline khác nhau cho 3 bài lab.
  * **Expected Output:** Liệt kê chính xác cả 3 mốc thời gian kèm tên bài lab tương ứng, không bị sót hay nhầm lẫn ngày.
* **Case 13 (No Deadline Announcement):**
  * **Input:** Thông báo chúc mừng sinh nhật thành viên hoặc nghỉ lễ.
  * **Expected Output:** Tóm tắt ngắn nội dung sự kiện, ghi rõ `Không có Action Item / Deadline`.
* **Case 14 (Empty / No New Announcements):**
  * **Input:** Gọi lệnh `!sum` khi kênh thông báo không có tin nhắn mới nào trong 7 ngày qua.
  * **Expected Output:** Bot phản hồi: `Không có thông báo mới nào trong tuần này.`
* **Case 19 (Mixed Casual Chat & Announcement):**
  * **Input:** Kênh thông báo chứa tin nhắn thảo luận tán gẫu xen kẽ tin thông báo chính thức.
  * **Expected Output:** AI lọc bỏ tin nhắn tán gẫu, chỉ trích xuất thông tin từ các tin nhắn mang tính chất thông báo.
* **Case 20 (Message with Hyperlinks & Attachments):**
  * **Input:** Thông báo chứa link đăng ký Form Google và file đính kèm PDF.
  * **Expected Output:** Trích xuất đúng link Form Google và trích dẫn nội dung chính của thông báo.
* **Case 21 (Link Redirection Test):**
  * **Output Validation:** Kiểm tra nút bấm/link `[Xem tin nhắn gốc]` ở cuối bản tóm tắt có điều hướng chính xác tới Discord Message ID tương ứng hay không.
- **Quality bar:**  — mình đề xuất khung để nhóm điền số cụ thể: "Đạt khi ≥ 80% câu hỏi paraphrase trong golden set được nhận đúng ở tầng phù hợp (auto-match hoặc OpenAI xét), và 10% trường hợp trả lời sai nhưng gắn nhãn tự tin cao (auto-match nhầm)."
- **Kết quả các lượt chạy (baseline thật, 31/7):**

* **Hiện trạng Tầng 1 (Cache):** Đạt **0% Auto-match** do hệ thống đang ở giai đoạn **Cold Start** (Database trống, chưa có dữ liệu tích lũy từ các buổi học).
* **Hiệu năng Tầng 2 (Fallback):** Đạt **100% tỷ lệ xử lý thành công**, chứng minh luồng chuyển tiếp khi Cache Miss sang LLM/Thread hỗ trợ vận hành ổn định 100%.
* **Kế hoạch cải thiện:**
  1. **Nạp dữ liệu mồi (Data Seeding):** Import trước 20–30 câu hỏi thường gặp (FAQ) vào SQLite DB.
  2. **Vòng lặp Tự học (Learn-on-the-Fly):** Kích hoạt cơ chế thả reaction `✅` để Coach nạp dữ liệu thực tế trong quá trình hỗ trợ, giúp tỷ lệ Auto-match Tầng 1 tăng dần theo thời gian sử dụng.

---

## §8. Phân công & kế hoạch

| Vai trò (Role) | Nhiệm vụ chính | Người đảm nhận | Mã sinh viên |
| :--- | :--- | :--- | :--- |
| **Team Leader & Q&A Bot Developer** | **Trưởng nhóm & Lập trình chính Bot Q&A:** Điều phối dự án, xây dựng SQLite DB Cache, thuật toán Fuzzy Matching, luồng xử lý Thread & Reaction `✅`, kéo code & lắp ráp hệ thống hoàn chỉnh. | `Nguyễn Kim Quý` | `2A202601456` |
| **Evidence & Data Lead** | Thu thập số liệu khảo sát ($n=68$), tổng hợp Quotes nguyên văn, dựng Bảng Impact 3 tính năng và soạn bộ Golden Set / Test cases. | `Nguyễn Vũ Việt Anh` | `2A202601742` |
| **Notification Bot Dev & Prompt Engineer** | **Lập trình chính Bot Tóm tắt thông báo:** Viết Tool cào tin nhắn Discord, thiết kế System Prompt tóm tắt Action Items/Deadline qua OpenAI API và tối ưu Guardrails. | `Nguyễn Minh Đạt` | `2A202601810` |
| **Documentation & Spec Architect** | Xây dựng tài liệu đặc tả sản phẩm (`03-template-ai-spec.md`), Worksheet JTBD, sơ đồ Workflow chi tiết và Trace Log / Nhật ký kiểm thử. | `Nguyễn Đăng Tuyên` | `2A202601622` |
| **Product Presenter & Slide Lead** | Thiết kế bộ Slide thuyết trình 8 trang trọng tâm, xây dựng kịch bản Demo tương tác trực tiếp và phụ trách báo cáo nghiệm thu. | `Nguyễn Văn Quân` | `2A202601544` |
- **Multi-prototype (nếu làm):** Hiện chỉ có 1 phương án được triển khai đầy đủ (kiến trúc 2 tầng fuzzy + OpenAI). Nếu nhóm muốn làm multi-prototype để so sánh, có thể cân nhắc trục khác biệt: (a) fuzzy-only vs (b) 2-tầng hiện tại.

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
