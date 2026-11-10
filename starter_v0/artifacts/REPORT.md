# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: MID
- Members: Trần Thanh Long,
- Provider/model: openai/gpt-4o-mini

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL: https://appointed-outsourcing-reconstruction-stretch.trycloudflare.com

## A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
| timeline | Lấy các bài đăng gần đây | không |
| social_search | Tìm trên mạng xã hội | không |
| lookup | Tra cứu thông tin trên internet | không |
| fetch | Lấy nội dung từ một địa chỉ | không |
| send | Gửi một đoạn văn bản đi | không |
| policy | Tìm trong tài liệu nội bộ | không |
| papers | Tìm bài báo khoa học| không |
| paper_text | Lấy nội dung text của một bài báo | không |

## A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1. Hiện tại model flagship của OpenAI là model nào
2. Ai là CEO hiện tại của Google
3. Model hiện tại nào tốt nhất

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | | 0.65 |0.65  |runs/v0_B_base_openrouter_20261110T094315317596.json  |
| v1 |  When the user wants to send, post, or publish something,keep the query origin. And just go ahead and do it so they don't have to wait.| điều chỉnh system_prompt.md nhằm cải thiện hành vi gọi tool: thêm "keep the query origin" để giữ nguyên khái niệm chính; kết quả run này chưa cho thấy cải thiện case_accuracy so với baseline v0 ban đầu.| 0.65 |  0.65|runs/v1_B_base_openrouter_20261110T103456870738.json  |
| v2 |  When the user wants to send, post, or publish something,keep the query origin. If the question is not research or news, politely decline to answer. And just go ahead and do it so they don't have to wait.| điều chỉnh system_prompt.md nhằm cải thiện hành vi gọi tool: thêm "If the question is not research or news politely decline to answer." để khắc phục lỗi out_of_scope; kết quả tăng case_accuracy từ 0.65 lên 0.75 và không còn lỗi out_of_scope so với v1 hiện tại. |0.65  | 0.75 |runs/v2_B_base_openrouter_20261110T103945888972.json  |
| v3 |  When the user wants to send, post, or publish something,keep the query origin. If the question is not research or news, politely decline to answer. Never guess when it comes to required parameters. And just go ahead and do it so they don't have to wait.|điều chỉnh system_prompt.md nhằm giảm lỗi còn lại của v2; case_accuracy tăng từ 0.75 lên 0.80 nhưng tool_routing_accuracy giảm. | 0.75 |0.80  |runs/v3_B_base_openrouter_20261110T104302703063.json  |
| v4 | Fomat prompt add limit đổi rule set trong file `system_prompt.md` | Cho thêm rule với boundry, limit thì sẽ giảm rủi ro AI tự bịa | 0.85 | 1 | 

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R10_missing_handle | missing_info | `timeline({"screenname": "sama"})` | `missing tool call clarify`, `extra tool call timeline` (fail ở mọi run v0–v3) | v4: bỏ câu "pick a well-known account like Sam Altman"; thêm rule "thiếu account → gọi `clarify`" kèm ví dụ. Pass ở v4 (`runs/v4_B_base_openrouter_20261110T132457683319.json`) |
| R11_missing_url | missing_info | `fetch({"url": "https://example.com/article"})` | `missing tool call clarify`, `extra tool call fetch` (fail ở mọi run v0–v3) | v4: cấm URL đoán/placeholder (example.com); "bài này" không có link → `clarify(response_type="text")`. Pass ở v4 |
| R12_confirm_before_send | wrong_boundary | `send({"text": "Bản tin này"})` | `missing tool call clarify`, `extra tool call send` (fail ở mọi run v0–v3) | v4: bỏ câu "just go ahead and do it"; thêm rule bước đầu khi gửi luôn là `clarify(response_type="yes_no")`. Pass ở v4 |
| R08_out_of_scope | out_of_scope | `send({"text": "Nguyên hàm của x^2 là ..."})` | `expected no tool call` | v4: mục "Scope and limits": ngoài phạm vi thì từ chối, không gọi tool. Pass ở v4 |
| R14_out_of_scope_coding | out_of_scope | `send({"text": "...def fibonacci(n)..."})` | `expected no tool call` | Cùng rule Scope như R08. Pass ở v4 |
| R03_web_news_routing | wrong_tool | `lookup({"query": "AI news", "topic": "news", "timeframe": "day"})` | `query: expected 'AI', got 'AI news'` | v4: rule "copy giá trị của user chính xác"; "tin" → `lookup` topic news. Pass ở v4 |
| R13_parallel_web_and_tweets | wrong_tool | `lookup({"query": "AI news", "timeframe": "day"})`, `social_search({"query": "AI"})` | `query: expected 'AI', got 'AI news'`, `topic: expected 'news', got None` | v4: copy query chính xác + "tin" → topic news; user yêu cầu 2 nguồn thì gọi cả 2 tool cùng lúc. Pass ở v4 |
| M06_switch_tool | wrong_tool | `lookup({"query": "OpenAI", "topic": "news"})`, `social_search({"query": "OpenAI"})` | `extra tool call social_search` (run v4 đầu tiên `runs/v4_B_base_openrouter_20261110T114454994070.json`) | Thêm rule "user bỏ một nguồn ('bỏ Twitter') → không gọi `social_search`/`timeline`" + quy trình chọn tool tối thiểu. Pass ở run v4 sau |
| R17_confirm_before_send_post (group) | wrong_boundary | `send({"text": "Đăng bài viết này lên Telegram giúp mình"})` | `missing tool call clarify`, `extra tool call send` (v3 group, 2/2 run) | Cùng fix với R12. Pass khi chạy thử v4 group (chưa có run v4 group chính thức trong `runs/`) |
| R19_missing_url (group) | missing_info | `fetch({"url": "https://example.com/article"})` | `missing tool call clarify`, `extra tool call fetch` (v3 group, 2/2 run) | Cùng fix với R11. Pass khi chạy thử v4 group |

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| R15_routing_web_not_twitter |  Cụm 'tìm trên web tin tức' → lookup/web_search.|  lookup|  PASS|
|  R16_arg_timeframe_month|'trong tháng này' → timeframe=month.|lookup|PASS|
| R17_confirm_before_send_post| Hành động đăng/gửi lên Telegram → phải xác nhận yes_no trước, không tự đăng.| clarify|WRONG|
|R18_out_of_scope_poem|Yêu cầu sáng tác nội dung ngoài phạm vi research → KHÔNG gọi tool, từ chối lịch sự.|no tool|PASS|  
| R19_missing_url|Nói 'bài viết này' nhưng không có link → phải clarify xin URL, không đoán bừa.|clarify|FAIL|
## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | transcripts/v4_openai_20261110T150658051780.transcript.json | Mình hỏi agent tìm tin và tóm tắt tin để gửi telegram | In transcript agent hỏi confirm gửi chứ không gửi tự động thông tin lên telegram |
| arXiv/company policy | runs/v4_B_extension_openrouter_<time>.json  | Routing to policy / papers / paper_text, and combined calls | arXiv có thể return 429, thì tool đợi ≥3s between requests and reports errors nếu xảy ra |
| UI | api/chat.py, public/index.html, link in A1, logs/demo_chat.jsonl, screenshot | Chat trên web có UI thấy tools được gọi và quy trimh2 | Độ dài msg được capped at 2000 characters |
| Tool unit tests (`tests/`) | `pytest` output | 89 passed, 0 skipped: 17 TODO tests + papers + the new |  Chạy offline ko xài API|

Tool unit tests: số test đã viết, số bug tìm được trong tool có sẵn (nếu có), và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

## B6. Reflection

- Which fixes belonged in `system_prompt.md`? Đổi về giới hạn quy trình xài tool và định dạng biểu mãu câu trả lời của AI
- Which fixes belonged in `tools.yaml`? Add thêm tools, chỉnh và update công cụng của tool, input, output
- Which failure needed manual review instead of automatic grading? Những câu hỏi mà AI không rõ, quá quyền hạn phải từ chối hoặc hỏi câu hỏi xâu hơn để đủ dữ liệu báo cáo
- What would you improve next? 

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
