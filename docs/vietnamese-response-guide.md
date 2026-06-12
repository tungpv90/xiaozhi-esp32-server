# Hướng dẫn để server phản hồi tiếng Việt

Tài liệu này phân tích trực tiếp luồng xử lý trong `main/xiaozhi-server` và chỉ ra nơi nào quyết định ngôn ngữ phản hồi của server.

## Kết luận ngắn

Server không có một cờ “bật tiếng Việt” duy nhất. Ngôn ngữ phản hồi được quyết định bởi 3 lớp:

1. `system prompt` gốc trong `agent-base-prompt.txt`
2. Giá trị `language` được `PromptManager` inject vào prompt
3. Khả năng đa ngôn ngữ của model LLM và cấu hình TTS

Nếu muốn server mặc định trả lời tiếng Việt, bạn phải chỉnh cả prompt lẫn cấu hình TTS, và bảo đảm config thực tế đang được server dùng là config local hoặc config lấy từ `manager-api`.

## Luồng xử lý liên quan đến ngôn ngữ

### 1. Input giọng nói được nhận và đưa vào ASR

ASR chỉ có nhiệm vụ chuyển âm thanh thành văn bản. Nó không quyết định ngôn ngữ mà LLM sẽ trả lời.

Các điểm đáng chú ý:

- `FunASR` đang dùng `language="auto"` để tự nhận diện ngôn ngữ.
- Một số ASR khác như `Qwen3-ASR-Flash` và `DoubaoStreamASR` có thể nhận cấu hình ngôn ngữ riêng.

Kết luận: nếu mục tiêu là “server trả lời tiếng Việt”, ASR chỉ là phần đầu vào.

### 2. Prompt được dựng lại trước khi gọi LLM

Luồng chính nằm ở:

- `main/xiaozhi-server/core/connection.py`
- `main/xiaozhi-server/core/utils/prompt_manager.py`

`ConnectionHandler` gọi:

- `PromptManager.update_context_info(...)`
- `PromptManager.build_enhanced_prompt(...)`

Sau đó prompt này được đẩy vào `Dialogue` bằng `update_system_message(...)`.

Điểm quan trọng nhất là `PromptManager.build_enhanced_prompt()` đang lấy ngôn ngữ từ TTS đang được chọn. Nếu không có cấu hình ngôn ngữ rõ ràng, code mặc định dùng `"中文"`.

### 3. LLM chỉ stream nội dung, không tự dịch

Các provider LLM như `openai`, `ollama`, `dify` chỉ gửi `messages` tới model rồi stream token về.

Nói cách khác:

- Nếu system prompt yêu cầu tiếng Việt, model sẽ ưu tiên tiếng Việt.
- Nếu prompt không rõ, model có thể trả lời theo ngôn ngữ người dùng hoặc ngôn ngữ mặc định của model.

### 4. TTS phải được cấu hình phù hợp

TTS không quyết định nội dung câu trả lời, nhưng ảnh hưởng đến:

- giọng đọc có tự nhiên với tiếng Việt không
- cách `PromptManager` suy ra giá trị `language`

Với các TTS như `EdgeTTS`, `Huoshan`, `GPT-SoVITS`, bạn nên chọn voice và tham số ngôn ngữ phù hợp với tiếng Việt.

## Những file cần xem

- `main/xiaozhi-server/agent-base-prompt.txt`
- `main/xiaozhi-server/core/utils/prompt_manager.py`
- `main/xiaozhi-server/core/connection.py`
- `main/xiaozhi-server/config.yaml`
- `main/xiaozhi-server/config/config_loader.py`

## Chỗ quyết định tiếng Việt

### `agent-base-prompt.txt`

File này chứa rule quan trọng:

- hệ thống phải trả lời bằng `{{language}}`

Vì vậy, nếu `{{language}}` được thay bằng tiếng Trung thì toàn bộ prompt sẽ nghiêng về tiếng Trung.

Muốn server mặc định tiếng Việt, hãy sửa rule này theo hướng:

- luôn trả lời bằng tiếng Việt
- chỉ đổi ngôn ngữ khi người dùng yêu cầu rõ ràng

### `PromptManager.build_enhanced_prompt()`

Đây là nơi ghép biến `language` vào prompt.

Logic hiện tại:

- lấy `language` từ TTS đang được chọn
- nếu không có thì mặc định là `"中文"`

Đây là lý do phổ biến khiến server không tự chuyển sang tiếng Việt dù bạn nghĩ đã đổi cấu hình ở nơi khác.

### `config.yaml`

Hai điểm cần kiểm tra:

- `selected_module.TTS`
- block cấu hình của đúng TTS đang dùng

Ví dụ, nếu đang dùng `EdgeTTS` và voice mặc định là giọng Trung, thì phần nói ra sẽ không tự thành tiếng Việt chỉ nhờ prompt.

### `config/config_loader.py`

Nếu `manager-api.url` được cấu hình, server sẽ ưu tiên lấy config từ API.

Điều này có nghĩa là:

- sửa `main/xiaozhi-server/config.yaml` local chưa chắc đã có tác dụng
- bạn phải sửa config phía API hoặc `data/.config.yaml` đúng chế độ chạy

## Cách cấu hình để ưu tiên tiếng Việt

### Cách 1: Sửa prompt gốc

Trong `agent-base-prompt.txt`, thêm hoặc thay rule để nói rõ:

- luôn phản hồi tiếng Việt
- nếu người dùng nói ngôn ngữ khác, vẫn trả lời tiếng Việt trừ khi được yêu cầu đổi ngôn ngữ

### Cách 2: Đặt `language` rõ ràng ở TTS

Trong block TTS đang được chọn, đặt ngôn ngữ phù hợp với tiếng Việt.

Ví dụ khái quát:

```yaml
selected_module:
  TTS: EdgeTTS

TTS:
  EdgeTTS:
    type: edge
    voice: zh-CN-XiaoxiaoNeural
    language: Tiếng Việt
```

Lưu ý:

- `voice` cần là voice phù hợp với tiếng Việt nếu provider hỗ trợ
- một số provider không dùng key `language` theo đúng nghĩa của model, nhưng `PromptManager` vẫn dùng giá trị này để dựng prompt

### Cách 3: Chọn LLM đa ngôn ngữ tốt

LLM là nơi trả lời cuối cùng. Nên chọn model có chất lượng tốt với tiếng Việt.

Nếu dùng model không mạnh về tiếng Việt:

- prompt tốt vẫn chưa đủ
- câu trả lời có thể lẫn ngôn ngữ hoặc không tự nhiên

### Cách 4: Đảm bảo không bị config từ API ghi đè

Nếu server đang chạy ở chế độ lấy config từ `manager-api`:

- sửa local file sẽ không đủ
- cần chỉnh config do API trả về, hoặc file bootstrap `data/.config.yaml`

## Checklist triển khai

1. Xác định server đang dùng config local hay config từ `manager-api`.
2. Sửa `agent-base-prompt.txt` để yêu cầu trả lời tiếng Việt.
3. Chỉnh `selected_module.TTS` sang provider bạn muốn dùng.
4. Kiểm tra block TTS đó có `language` hoặc tham số tương đương phù hợp.
5. Chọn voice hỗ trợ tiếng Việt.
6. Chọn LLM có chất lượng tiếng Việt tốt.
7. Khởi động lại server và tạo session mới để prompt được dựng lại.

## Dấu hiệu cấu hình đúng

- LLM trả lời tiếng Việt ngay cả khi người dùng hỏi bằng ngôn ngữ khác.
- Prompt log cho thấy `language` đã là tiếng Việt.
- TTS đọc tiếng Việt tự nhiên, không bị voice sai ngôn ngữ.
- Khi đổi config, server mới phải restart thì hiệu lực mới xuất hiện.

## Rủi ro thường gặp

- Chỉnh `config.yaml` local nhưng server đang lấy config từ API.
- Chỉ đổi voice TTS mà quên sửa prompt.
- Chỉ sửa prompt mà model LLM không đủ tốt với tiếng Việt.
- Không restart server sau khi đổi cấu hình.

## Tóm tắt cuối

Muốn server phản hồi tiếng Việt ổn định, cách làm đúng là:

- sửa system prompt để bắt buộc tiếng Việt
- set `language` đúng ở TTS để `PromptManager` inject chuẩn
- chọn LLM đa ngôn ngữ tốt
- bảo đảm config thực tế không bị `manager-api` ghi đè

