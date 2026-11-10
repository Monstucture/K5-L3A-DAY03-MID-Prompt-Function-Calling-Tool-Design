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

Lọc danh sách tin đã có theo từ khóa xuất hiện trong tiêu đề
hoặc tóm tắt.

## Đầu vào

- items: danh sách các tin. Mỗi tin là một đối tượng có thể
  chứa title và summary. Nếu có, hai trường này phải là văn bản.
- keyword: từ khóa dạng văn bản, không được rỗng.

## Đầu ra

- Khi thành công: trả items là danh sách tin phù hợp và count
  là số tin phù hợp. Không có tin phù hợp thì trả danh sách
  rỗng và count bằng 0.
- Khi đầu vào không hợp lệ: trả error và message thay vì
  phát sinh lỗi làm chương trình dừng.

## Đặc điểm

- Không tìm kiếm dữ liệu mới và không truy cập mạng.
- Không phân biệt chữ hoa/thường; vẫn phân biệt dấu tiếng Việt.
- Tìm theo chuỗi ký tự xuất hiện trong title hoặc summary.
- Không thay đổi dữ liệu đầu vào.

## Ví dụ

Đầu vào:

    {
      "items": [
        {"title": "Robotics hôm nay", "summary": "Tin mới"},
        {"title": "Y tế", "summary": "Thông tin sức khỏe"}
      ],
      "keyword": "robotics"
    }

Kết quả:

    {
      "items": [
        {"title": "Robotics hôm nay", "summary": "Tin mới"}
      ],
      "count": 1
    }