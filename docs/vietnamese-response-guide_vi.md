# Hướng dẫn để server trả lời tiếng Việt

Tài liệu này chỉ ra các điểm quyết định ngôn ngữ phản hồi trong `main/xiaozhi-server`.

## Kết luận nhanh

Không có một nút đơn lẻ để "bật tiếng Việt". Ngôn ngữ phản hồi được quyết định bởi:

1. `system prompt` trong `agent-base-prompt.txt`
2. Giá trị `language` mà `PromptManager` chèn vào prompt
3. Khả năng đa ngôn ngữ của LLM và cấu hình TTS

Muốn mặc định tiếng Việt, bạn phải chỉnh prompt, chỉnh TTS và đảm bảo server đang dùng đúng config.

## Luồng liên quan

### 1. ASR chỉ đổi giọng nói thành text

ASR không quyết định ngôn ngữ trả lời.

### 2. Prompt được dựng lại trước khi gọi LLM

Luồng chính ở:

- `main/xiaozhi-server/core/connection.py`
- `main/xiaozhi-server/core/utils/prompt_manager.py`

`PromptManager.build_enhanced_prompt()` đang lấy `language` từ TTS đang chọn. Nếu không có cấu hình rõ ràng, code thường mặc định là `"中文"`.

### 3. LLM chỉ stream output

Nếu system prompt yêu cầu tiếng Việt, model sẽ ưu tiên tiếng Việt. Nếu không rõ ràng, model có thể trả lời theo ngôn ngữ mặc định.

### 4. TTS cũng cần đúng

TTS không đổi nội dung câu trả lời, nhưng ảnh hưởng đến:

- chất lượng giọng đọc tiếng Việt
- giá trị `language` mà prompt manager suy ra

## File cần xem

- `main/xiaozhi-server/agent-base-prompt.txt`
- `main/xiaozhi-server/core/utils/prompt_manager.py`
- `main/xiaozhi-server/core/connection.py`
- `main/xiaozhi-server/config.yaml`
- `main/xiaozhi-server/config/config_loader.py`

## Cách cấu hình để ưu tiên tiếng Việt

1. Sửa prompt gốc để yêu cầu luôn trả lời bằng tiếng Việt.
2. Đặt `language` trong TTS thành tiếng Việt.
3. Chọn LLM đa ngôn ngữ tốt.
4. Nếu server lấy config từ `manager-api`, hãy chỉnh ở phía API trả về.

## Checklist

1. Xác định server đang dùng config local hay config từ `manager-api`
2. Sửa `agent-base-prompt.txt`
3. Chọn đúng TTS
4. Chọn voice phù hợp tiếng Việt
5. Chọn LLM mạnh với tiếng Việt
6. Restart server và mở session mới

## Tóm tắt

Muốn server nói tiếng Việt ổn định, hãy:

- bắt buộc tiếng Việt trong system prompt
- set `language` phù hợp ở TTS
- chọn LLM tốt
- đảm bảo config thực tế không bị API ghi đè
