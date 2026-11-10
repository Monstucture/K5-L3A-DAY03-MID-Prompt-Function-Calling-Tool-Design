# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: MID
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
| v0 | baseline | | 0.65 |0.65  |runs/v0_B_base_openrouter_20261110T094315317596.json  |
| v1 |  When the user wants to send, post, or publish something,keep the query origin. And just go ahead and do it so they don't have to wait.| điều chỉnh system_prompt.md nhằm cải thiện hành vi gọi tool: thêm "keep the query origin" để giữ nguyên khái niệm chính; kết quả run này chưa cho thấy cải thiện case_accuracy so với baseline v0 ban đầu.| 0.65 |  0.65|runs/v1_B_base_openrouter_20261110T103456870738.json  |
| v2 |  When the user wants to send, post, or publish something,keep the query origin. If the question is not research or news, politely decline to answer. And just go ahead and do it so they don't have to wait.| điều chỉnh system_prompt.md nhằm cải thiện hành vi gọi tool: thêm "If the question is not research or news politely decline to answer." để khắc phục lỗi out_of_scope; kết quả tăng case_accuracy từ 0.65 lên 0.75 và không còn lỗi out_of_scope so với v1 hiện tại. |0.65  | 0.75 |runs/v2_B_base_openrouter_20261110T103945888972.json  |
| v3 |  When the user wants to send, post, or publish something,keep the query origin. If the question is not research or news, politely decline to answer. Never guess when it comes to required parameters. And just go ahead and do it so they don't have to wait.|điều chỉnh system_prompt.md nhằm giảm lỗi còn lại của v2; case_accuracy tăng từ 0.75 lên 0.80 nhưng tool_routing_accuracy giảm. | 0.75 |0.80  |runs/v3_B_base_openrouter_20261110T104302703063.json  |

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|R10_missing_handle  | missing_info | timeline | "missing tool call clarify", "extra tool call timeline" |Dùng clarify để xác nhận trước khi call timeline  |
|R11_missing_url|missing_info|fetch|"missing tool call clarify", "extra tool call fetch"|Gọi clarify trước khi fetch|
|R12_confirm_before_send |wrong_boundary|send|"missing tool call clarify", "extra tool call send"|Clarify bản tin trước khi dùng tool send|  
| R13_parallel_web_and_tweets| wrong_tool| lookup, timeline|"missing tool call social_search", "extra tool call timeline"|khi người dùng yêu cầu tìm thông tin trên web và tweet về cùng một chủ đề, gọi cả lookup và social_search. Chỉ dùng timeline khi yêu cầu xem tweet của một tài khoản cụ thể.|

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
| send (Telegram) |  |  |  |
| arXiv/company policy |  |  |  |
| UI |  |  |  |
| Tool unit tests (`tests/`) | `pytest` output |  |  |

Tool unit tests: số test đã viết, số bug tìm được trong tool có sẵn (nếu có), và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
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
