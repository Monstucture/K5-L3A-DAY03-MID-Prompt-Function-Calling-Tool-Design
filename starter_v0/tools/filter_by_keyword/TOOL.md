---
name: filter_by_keyword
track: core
kind: local_formatter
requires_env: []
inputs: [items, keyword]
outputs: [items, count, error, message]
side_effect: false
---

# Lọc tin theo từ khóa

Dùng để lọc danh sách tin đã có theo từ khóa trong tiêu đề hoặc tóm tắt.

Đầu vào:
- items: danh sách tin, mỗi tin có thể có title và summary.
- keyword: từ khóa không rỗng.

Đầu ra:
- items: các tin chứa từ khóa.
- count: số tin tìm được.
- Nếu lỗi, trả error và message, không làm chương trình dừng.

Không tìm kiếm dữ liệu mới và không truy cập mạng.
Không phân biệt chữ hoa/thường; vẫn phân biệt dấu tiếng Việt.