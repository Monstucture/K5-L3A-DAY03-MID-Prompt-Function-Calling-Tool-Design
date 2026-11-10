---
name: format
track: core
kind: local_formatter
requires_env: []
inputs: [items, template, headline, searched_with]
outputs: [markdown, item_count]
side_effect: false
---
# format

Formats already-collected items into a markdown digest. It does not fetch data.

Template `digest_5min` builds a ~5 minute newsletter: a numbered list (`1.`, `2.`, ...) with a short summary and a link per item (max 10),
then a "Nguồn & tài liệu tham khảo" list of every unique source URL, and, if `searched_with` is given, the tools and queries the agent used.
