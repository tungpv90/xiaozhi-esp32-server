# Lấy thông tin thiết bị bằng MCP

Tài liệu này hướng dẫn cách lấy `device_id` qua MCP.

## Bước 1: Tùy biến `agent-base-prompt.txt`

Copy file `agent-base-prompt.txt` từ thư mục gốc `xiaozhi-server` vào `data` và đổi tên thành `.agent-base-prompt.txt`.

## Bước 2: Sửa prompt

Tìm thẻ `<context>` và thêm:

```text
- **Mã thiết bị:** {{device_id}}
```

Ví dụ:

```markdown
<context>
[Quan trọng! Thông tin dưới đây đã được cung cấp theo thời gian thực, không cần gọi công cụ để tra cứu, hãy dùng trực tiếp:]
- **Mã thiết bị:** {{device_id}}
- **Thời gian hiện tại:** {{current_time}}
- **Hôm nay là ngày:** {{today_date}} ({{today_weekday}})
- **Âm lịch hôm nay:** {{lunar_date}}
- **Thành phố hiện tại của người dùng:** {{local_address}}
- **Dự báo thời tiết 7 ngày:** {{weather_info}}
</context>
```

## Bước 3: Sửa cấu hình

Trong `data/.config.yaml`, sửa:

```yaml
prompt_template: agent-base-prompt.txt
```

thành:

```yaml
prompt_template: data/.agent-base-prompt.txt
```

## Bước 4: Restart server

## Bước 5: Thêm tham số vào MCP

Thêm tham số tên `device_id`, kiểu `string`, mô tả là `设备ID`.

## Bước 6: Kiểm tra

Đánh thức Xiaozhi và gọi MCP method để xem có nhận được `device_id` hay không.
