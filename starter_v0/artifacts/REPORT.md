# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team:
- Members:
- Provider/model:

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL: 

## A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

## A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo kết quả ban đầu |  | 0.65 | runs/v0_B_base_openrouter_20261110T202147518322.json |
| v1 | system_prompt.md | Cải thiện hướng dẫn để giảm lỗi so với v0 | 0.65 | 0.75 | runs/v1_B_base_openrouter_20261110T210108331421.json |
| v2 | system_prompt.md | Bỏ chỉ dẫn tự đoán và làm rõ quy tắc hỏi lại, xác nhận gửi, tham số tìm tin sẽ giảm lỗi | 0.75 | 0.95 | runs/v2_B_base_openrouter_20261110T211224877990.json |
| v3 | Không thay đổi so với v2 | Chạy kiểm tra lại; prompt_hash vẫn giống v2 | 0.95 | 0.95 | runs/v3_B_base_openrouter_20261110T212456409492.json |
| v3 (lần 2) | system_prompt.md | Ưu tiên xác nhận ý định gửi trước khi hỏi nội dung thiếu sẽ khắc phục R12 | 0.95 | 1.00 | runs/v3_B_base_openrouter_20261110T213100839010.json |
| v4 (group) | system_prompt.md | Chỉ xử lý yêu cầu mới nhất, tránh gọi lặp và tôn trọng yêu cầu hủy sẽ khắc phục G06, G08, G10 | 0.70 | 1.00 | runs/v4_B_group_openrouter_20261110T215210488030.json |
| v5 (group) | tools.yaml và công cụ filter_by_keyword | AI biết chọn công cụ mới khi cần lọc dữ liệu đã có | Chưa có mốc cùng bộ 11 câu | 0.8182 | runs/v5_B_group_openrouter_20261110T223227783742.json |

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R10_missing_handle | missing_info | timeline(screenname="sama") | Thiếu tài khoản nhưng AI tự chọn sama, gọi timeline thay vì clarify để hỏi lại | Dự kiến sửa prompt: khi thiếu tài khoản, gọi clarify để hỏi người dùng |
| R11_missing_url | missing_info | fetch | Chưa có đường dẫn nhưng AI tự đoán và gọi fetch thay vì hỏi lại | Dự kiến sửa prompt: khi thiếu đường dẫn, gọi clarify để hỏi người dùng |
| R12_confirm_before_send | wrong_boundary | send | AI gọi công cụ gửi khi chưa hỏi người dùng xác nhận | Dự kiến sửa prompt: dùng clarify để xin xác nhận trước khi gọi send |
| R13_parallel_web_and_tweets | wrong_tool | lookup và social_search | AI chọn đúng hai công cụ nhưng lookup truyền query="AI news" thay vì "AI" và thiếu topic="news" | Dự kiến làm rõ quy tắc truyền từ khóa và loại tin khi tìm trên web |
| R03_web_news_routing | wrong_tool | lookup | Chọn đúng công cụ nhưng truyền query="AI news" thay vì "AI" | Dự kiến làm rõ quy tắc chỉ truyền chủ đề chính trong query |
| R08_out_of_scope | out_of_scope | send | Yêu cầu giải toán ngoài phạm vi nhưng AI vẫn gọi công cụ gửi | Dự kiến quy định phạm vi nghiên cứu; yêu cầu ngoài phạm vi thì không gọi công cụ |
| R14_out_of_scope_coding | out_of_scope | send | Yêu cầu viết code ngoài phạm vi nhưng AI vẫn gọi công cụ gửi | Dự kiến quy định không dùng công cụ cho yêu cầu viết code ngoài phạm vi |
### Phân tích lỗi phiên bản v1

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | wrong_tool | lookup | Chọn đúng công cụ nhưng truyền query="AI news" thay vì "AI" | Dự kiến làm rõ quy tắc query chỉ chứa chủ đề chính |
| R10_missing_handle | missing_info | timeline(screenname="sama") | Thiếu tài khoản nhưng AI tự chọn sama thay vì hỏi lại | Dự kiến yêu cầu gọi clarify với response_type="text" khi thiếu tài khoản |
| R11_missing_url | missing_info | fetch | Chưa có đường dẫn nhưng AI tự đoán và gọi fetch | Dự kiến yêu cầu gọi clarify với response_type="text" khi thiếu đường dẫn |
| R12_confirm_before_send | wrong_boundary | send | AI gọi gửi trước khi hỏi xác nhận | Dự kiến yêu cầu gọi clarify với response_type="yes_no" trước khi gửi |
| R13_parallel_web_and_tweets | wrong_tool | lookup và social_search | Chọn đúng hai công cụ nhưng lookup thiếu topic="news" | Dự kiến yêu cầu truyền rõ topic="news" khi tìm tin tức |
### Phân tích lỗi phiên bản v2

Kết quả: đạt 19/20 câu (95%), tăng từ 75% của v1. R03, R10, R11 và R13 đã đạt. Chỉ còn R12.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R12_confirm_before_send | wrong_boundary | clarify(response_type="text") | AI đã hỏi lại nhưng hỏi xin nội dung; bộ chấm yêu cầu câu xác nhận có/không với response_type="yes_no" | Dự kiến làm rõ thứ tự xác nhận ý định gửi và hỏi nội dung còn thiếu; chỉ gửi sau khi nội dung cụ thể được xác nhận |

AI không gọi send trong câu R12. Hỏi xin nội dung là hành vi có lý khi nội dung chưa được cung cấp, nhưng chưa đạt tiêu chí tự động.

Có 8 lời gọi công cụ X/Twitter trả lỗi: 7 lỗi 403 và 1 lỗi 429. Đây là lỗi hết token

V2 sửa nhiều quy tắc cùng lúc nên chưa xác định được tác động riêng của từng thay đổi.
### Phân tích phiên bản v3

Kết quả: 19/20 câu đạt (95%). Prompt_hash giống v2, nên lần này chưa kiểm chứng bản sửa mới.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R12_confirm_before_send | wrong_boundary | clarify(response_type="text") | AI hỏi xin nội dung, trong khi bộ chấm yêu cầu hỏi xác nhận bằng response_type="yes_no" | Làm rõ xác nhận ý định gửi là bước đầu tiên, được ưu tiên trước câu hỏi nội dung thiếu |

AI không gọi send. Hỏi xin nội dung là hợp lý khi chưa có bản tin, nhưng chưa đạt tiêu chí tự động.
### Kết quả v3 — lần chạy thứ hai

Kết quả: đạt 20/20 câu (100%), tăng từ 95% của lần trước. Không còn câu FAIL trong bộ đánh giá gốc.

R12 đã đạt: AI gọi clarify với response_type="yes_no" để hỏi xác nhận ý định gửi, không gọi send ngay.

Vẫn có 8 lời gọi công cụ X/Twitter trả lỗi 403. Đây là lỗi quyền truy cập dịch vụ; điểm đạt của bộ đánh giá không chứng minh đã lấy được dữ liệu thật.
### Phân tích v3 trên bộ group

Kết quả: 7/10 câu đạt (70%), còn 3 câu lỗi.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| G06_change_topic | wrong_arg_value | lookup cho robotics và AI | AI tìm đúng chủ đề mới nhưng vẫn tìm thêm chủ đề cũ | V4: chỉ thực hiện yêu cầu mới nhất, bỏ yêu cầu đã được thay thế |
| G08_correct_time_and_count | wrong_arg_value | lookup hai lần với cùng tham số | Gọi công cụ trùng lặp | V4: không gọi lặp cùng công cụ và tham số khi không cần thiết |
| G10_cancel_request | unnecessary_tool | send | Người dùng hủy yêu cầu nhưng AI vẫn gọi công cụ gửi | V4: xác nhận hủy bằng lời, không gọi công cụ |

Ba lỗi trên đã đạt khi kiểm tra lại trên cùng bộ group ở v4.
### Kết quả cải thiện bộ group ở v4

V4 đạt 10/10 câu (100%), tăng từ 7/10 câu (70%) của v3 trên cùng bộ group.

- G06: đã chỉ xử lý chủ đề mới, không tìm thêm chủ đề cũ.
- G08: đã tránh gọi trùng công cụ.
- G10: đã xác nhận hủy bằng lời, không gọi công cụ thừa.

Các câu trước đó đạt vẫn tiếp tục đạt. Không có lỗi kết nối model hoặc lỗi công cụ trong lần chạy này.
### Phân tích v5 trên bộ group

Kết quả: 9/11 câu đạt (81,82%). Sáu câu một lượt đều đạt; hội thoại nhiều lượt đạt 3/5.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| G06_change_topic | wrong_arg_value | lookup và social_search | Đã tìm web đúng nhưng gọi thêm social_search dù người dùng chỉ yêu cầu tìm trên web | Dự kiến làm rõ: chỉ dùng nguồn được yêu cầu, không tự mở rộng sang mạng xã hội |
| G08_correct_time_and_count | wrong_arg_value | lookup hai lần với topic news và general | Đã tìm tin tức đúng nhưng tìm thêm thông tin general không cần thiết | Dự kiến quy định chỉ thực hiện lượt tìm cần thiết cho yêu cầu hiện tại |

Hai câu mang nhãn wrong_arg_value của bộ đề, nhưng sai khác thực tế là extra_tool_call: gọi công cụ thừa.

G11_filter_keyword đạt: AI gọi đúng công cụ mới và kết quả giữ lại đúng một tin chứa robotics.

Có một lỗi dịch vụ 403 ở lời gọi social_search thừa trong G06. Đây là vấn đề quyền truy cập riêng.

Không so trực tiếp tỷ lệ tổng với v4 vì bộ đề tăng từ 10 lên 11 câu. Trên 10 câu chung, v5 đạt 8/10 so với 10/10 ở v4.


## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_web_news | Tìm tin đúng chủ đề, thời gian và số lượng | lookup: AI, news, day, 3 kết quả | PASS |
| G02_missing_url | Hỏi lại khi thiếu đường dẫn | clarify với response_type="text" | PASS |
| G03_read_url | Đọc đường dẫn đã có | fetch | PASS |
| G04_capabilities | Giới thiệu chức năng không cần công cụ | Trả lời trực tiếp | PASS |
| G05_format_existing_items | Trình bày dữ liệu đã có | format với template="bullets" | PASS |
| G06_change_topic | Đổi chủ đề, giữ nguồn tìm kiếm | Chỉ dùng lookup tìm robotics trên web | PASS ở v4; FAIL ở v5 vì gọi thêm social_search |
| G07_provide_missing_url | Sử dụng đường dẫn được bổ sung | fetch, không hỏi lại đường dẫn | PASS |
| G08_correct_time_and_count | Cập nhật thời gian và số lượng | Chỉ tìm tin robotics trong tháng, tối đa 2 kết quả | PASS ở v4; FAIL ở v5 vì tìm thêm loại general |
| G09_confirm_before_send | Xin xác nhận trước khi gửi | clarify với response_type="yes_no" | PASS |
| G10_cancel_request | Tôn trọng yêu cầu hủy | Xác nhận bằng lời, không gọi công cụ | PASS ở v4; trước đó FAIL ở v3 |
| G11_filter_keyword | Chọn công cụ mới để lọc dữ liệu đã có | filter_by_keyword với keyword="robotics" | PASS ở v5; công cụ trả đúng 1 tin |

Kết quả bộ group: v3 đạt 7/10 câu (70%); sau khi sửa prompt, v4 đạt 10/10 câu (100%). Gồm 5/5 câu một lượt và 5/5 câu nhiều lượt. Ba lỗi G06, G08 và G10 đã được khắc phục trong lần chạy v4.Bộ group mở rộng có 11 câu. V5 đạt 9/11 câu (81,82%): một lượt đạt 6/6, nhiều lượt đạt 3/5.


## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Bonus Evidence

## B5. Bằng chứng công cụ mới và kiểm thử

Bài làm cá nhân. Phần này ghi những nội dung đã có bằng chứng thực hiện.

| Hạng mục | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Công cụ mới: filter_by_keyword | tools/filter_by_keyword/tool.py; runs/v5_B_group_openrouter_20261110T223227783742.json | G11 đạt: AI chọn đúng công cụ và truyền đúng từ khóa; công cụ lọc đúng còn 1 tin | Chỉ xử lý danh sách đã có, không tìm dữ liệu mới; không phân biệt hoa/thường nhưng vẫn phân biệt dấu tiếng Việt |
| Kiểm thử công cụ mới | tests/test_tools_todo.py | 3 bài kiểm thử đều đạt: dữ liệu bình thường, từ khóa rỗng, dữ liệu tin sai kiểu | Đầu vào không hợp lệ trả thông báo lỗi thay vì làm chương trình dừng |
| UI Streamlit và hội thoại thật | app.py; transcripts/v5_ui_20261110T232625564761.transcript.json | Đã trò chuyện 6 lượt và lưu bản ghi; có gọi công cụ hỏi lại | Vẫn có câu trả lời dùng thời gian cũ; lượt 6 chọn social_search không phù hợp và gặp HTTP 403; chưa có link dùng thử công khai |
| UI Streamlit và hội thoại thật | app.py; transcripts/v5_ui_20261110T232625564761.transcript.json | Ghi nhận 11 lượt hội thoại; đọc trang web, lọc đúng 2 tin và tìm kiếm web đúng tham số ở các lượt thử mới | Còn lỗi chọn công cụ ở lượt 6; lượt 7 hỏi lại bằng văn bản thay vì gọi clarify; lượt 10 thêm diễn giải ngoài dữ liệu gốc; chưa có link dùng thử công khai |

### Chi tiết kiểm thử

- Số bài kiểm thử cho công cụ mới: 3, kết quả 3 passed.
- Chưa ghi nhận bug mới trong các công cụ có sẵn; chưa kết luận các công cụ đó không có lỗi.
- Ví dụ khác biệt giữa unit test và eval: unit test đưa title=None để kiểm tra công cụ trả lỗi TypeError. Tình huống G11 dùng dữ liệu hợp lệ nên không kiểm tra nhánh lỗi này.
- Kết quả 3 passed chỉ áp dụng cho kiểm thử riêng filter_by_keyword, không đại diện cho toàn bộ bộ kiểm thử.
- Chưa ghi nhận hoàn thành các phần gửi Telegram thật, arXiv/company policy mở rộng hoặc giao diện UI.

## B6. Reflection

1. Những lỗi cần sửa trong system_prompt.md
Thêm hướng dẫn hỏi lại khi chưa đủ thông tin, không dự đoán tham số, không gọi thêm công cụ khác,yêu cầu xác nhận trước khi gửi 

2. Những thay đổi cần làm trong tools.yaml
khai báo công cụ mới, mô tả chức năng của công cụ mới để ai biết và sử dụng

3. Trường hợp cần xem xét thủ công
cần đọc cả lời gọi công cụ và kết quả khi chọn công cụ, nếu Ai gọi thêm công cụ khác không cần thiết mà bị báo lỗi 403 thì ghi nhận cả 2 lỗi gọi thừa và lỗi truy cập.

4. Những việc cần cải thiện tiếp
chạy v5 g6 và g8 gọi thêm công cụ không cần thiết. cần xem lại hướng dẫn dùng công cụ và thông tin mới nhất trong hội thoại , giới hạn lời gọi công cụ.

Công cụ mới filter_by_keyword đã vượt qua 3 kiểm thử và tình huống G11. Kết quả này chỉ chứng minh các trường hợp đã kiểm tra, chưa bảo đảm công cụ đúng với mọi đầu vào.

--> Nhận xét từ hội thoại thật

Giao diện đã thực hiện được chuỗi hỏi bổ sung đường dẫn,
đọc trang web, lọc tin bằng công cụ mới và tìm kiếm web.

Cần cải thiện việc gọi clarify khi thiếu thông tin,
chọn đúng công cụ tìm kiếm và chỉ tóm tắt theo dữ liệu có sẵn.
Kết quả hội thoại thật cho thấy vẫn có lỗi dù bộ đánh giá
trước đó từng đạt 100%.

## B7. Small Local Model Challenge (bonus)

Only fill if your team did the local model challenge.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?
