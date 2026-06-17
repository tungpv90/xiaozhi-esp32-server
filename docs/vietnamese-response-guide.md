# Hướng dẫn chi tiết để server nhận và trả lời bằng tiếng Việt

Mục tiêu của tài liệu này là cấu hình để server:

1. Nhận đầu vào tiếng Việt từ thiết bị.
2. Giữ nguyên ngữ nghĩa tiếng Việt sau ASR.
3. Trả lời bằng tiếng Việt.
4. Đọc câu trả lời bằng giọng tiếng Việt tự nhiên.

Trong dự án này, ngôn ngữ không nằm ở một chỗ duy nhất. Muốn chạy ổn định, bạn phải chỉnh đồng thời:

- ASR
- system prompt
- `PromptManager`
- TTS
- nguồn config thực tế mà server đang đọc

## 1. Luồng xử lý ngôn ngữ

### Bước 1: Thiết bị gửi âm thanh lên server

Server nhận audio từ micro của thiết bị.

### Bước 2: ASR chuyển âm thanh thành văn bản

ASR quyết định câu đầu vào có được nhận đúng tiếng Việt hay không. Nếu ASR nhận sai, LLM sẽ trả lời sai theo.

### Bước 3: Prompt được dựng lại

Luồng dựng prompt nằm ở:

- `main/xiaozhi-server/core/connection.py`
- `main/xiaozhi-server/core/utils/prompt_manager.py`

Trong `PromptManager.build_enhanced_prompt()`, ngôn ngữ được lấy từ block TTS đang chọn. Nếu không có cấu hình rõ ràng, code mặc định dùng `中文`.

### Bước 4: LLM sinh câu trả lời

LLM chỉ là tầng sinh text. Nếu prompt yêu cầu tiếng Việt, model sẽ ưu tiên tiếng Việt.

### Bước 5: TTS phát âm câu trả lời

TTS không đổi nội dung, nhưng quyết định câu trả lời có được đọc ra bằng giọng tiếng Việt đúng hay không.

## 2. Chỉnh để server hiểu tiếng Việt

### 2.1 Chọn ASR hỗ trợ tiếng Việt

ASR cần nhận tiếng Việt tốt. Nếu đang dùng provider có hỗ trợ ngôn ngữ, hãy cấu hình để nó nhận tiếng Việt hoặc tự động nhận diện đa ngôn ngữ.

Trong `main/xiaozhi-server/config.yaml`, một số ASR có các trường kiểu:

- `language`
- `language_hints`
- `text_language`

Nếu provider của bạn hỗ trợ tiếng Việt, hãy cấu hình theo giá trị mà backend đó chấp nhận.

### 2.2 Kiểm tra log ASR

Khi test, hãy đọc log để xác nhận:

- câu tiếng Việt có được nhận đúng không
- có bị biến thành tiếng Trung, tiếng Anh, hoặc sai dấu quá nặng không

Nếu ASR chưa đúng, đừng vội chỉnh prompt. Hãy sửa tầng nhận dạng trước.

## 3. Chỉnh để server trả lời tiếng Việt

### 3.1 Sửa prompt gốc

Mở `main/xiaozhi-server/agent-base-prompt.txt`.

Trong file này có rule ngôn ngữ dạng:

```text
无论用户使用何种语言提问，你都必须默认使用 {{language}}进行回复
```

Đây là chỗ rất quan trọng. Bạn có 2 cách:

1. Giữ `{{language}}` nhưng đảm bảo giá trị được chèn vào là tiếng Việt.
2. Viết cứng rule là luôn trả lời bằng tiếng Việt.

Khuyến nghị thực tế:

- nếu muốn mặc định tiếng Việt, nên viết rõ trong prompt là "luôn trả lời bằng tiếng Việt"
- nếu muốn linh hoạt, hãy giữ biến `{{language}}` và set `language` đúng ở TTS

### 3.2 Đảm bảo `PromptManager` lấy đúng `language`

Trong `main/xiaozhi-server/core/utils/prompt_manager.py`, đoạn này quyết định giá trị `language`:

```python
self.config.get("TTS", {}) \
  .get(self.config.get("selected_module", {}).get("TTS", ""), {}) \
  .get("language") or "中文"
```

Điều này có nghĩa:

- `selected_module.TTS` chọn block TTS nào
- block đó phải có trường `language`
- nếu không có thì mặc định là `中文`

Vì vậy, muốn ra tiếng Việt, bạn phải đặt `language` cho đúng block TTS đang dùng.

### 3.3 Ví dụ cấu hình TTS

```yaml
selected_module:
  TTS: EdgeTTS

TTS:
  EdgeTTS:
    language: Tiếng Việt
```

Nếu provider TTS của bạn có voice riêng, hãy chọn voice hỗ trợ tiếng Việt và vẫn đặt `language` để prompt manager chèn đúng.

### 3.4 Chọn LLM mạnh với tiếng Việt

Nếu LLM yếu với tiếng Việt, bạn sẽ thấy:

- câu trả lời lẫn ngôn ngữ
- câu chữ gượng
- không bám sát yêu cầu

Khuyến nghị:

- dùng model đa ngôn ngữ tốt
- nếu có model tối ưu cho tiếng Việt thì càng tốt

## 4. Chỉnh để server đọc tiếng Việt

### 4.1 Đặt TTS ở đúng module

Trong `main/xiaozhi-server/config.yaml`, tìm:

```yaml
selected_module:
  TTS: EdgeTTS
```

Rồi mở đúng block TTS tương ứng và cấu hình ngôn ngữ/voice tiếng Việt.

### 4.2 Với provider có `language`

Nhiều block TTS có comment kiểu:

```yaml
# language: "中文"
```

Nếu provider đó hỗ trợ tiếng Việt, hãy đổi sang tiếng Việt hoặc giá trị mà backend chấp nhận.

### 4.3 Với GPT-SoVITS V3

File `main/xiaozhi-server/core/providers/tts/gpt_sovits_v3.py` cho thấy provider này dùng:

- `prompt_language`
- `text_language`

Nghĩa là:

- reference audio nên là tiếng Việt nếu muốn clone giọng Việt
- `text_language` phải khớp với ngôn ngữ đầu ra

Ví dụ logic cấu hình:

```yaml
TTS:
  GPTSoVITSV3:
    prompt_language: vi
    text_language: vi
```

Giá trị cụ thể còn phụ thuộc backend bạn dùng, nhưng nguyên tắc là phải đồng nhất ngôn ngữ đầu vào và đầu ra.

## 5. Nếu server lấy config từ `manager-api`

Đây là lỗi hay gặp nhất.

Nếu server của bạn đang chạy qua `manager-api`, thì:

- sửa `main/xiaozhi-server/config.yaml` local chưa chắc có tác dụng
- server có thể đang lấy config từ API trả về
- bạn phải sửa đúng nơi sinh ra config thực tế

Nếu đổi xong mà không thấy hiệu lực, hãy kiểm tra lại:

1. Server đang dùng config local hay config từ API.
2. `data/.config.yaml` có ghi đè gì không.
3. `selected_module.TTS` có trỏ đúng block không.

## 6. Cấu hình mẫu gợi ý

### Mẫu 1: Ưu tiên tiếng Việt

```yaml
selected_module:
  ASR: FunASR
  LLM: MyLLM
  TTS: EdgeTTS

TTS:
  EdgeTTS:
    language: Tiếng Việt

LLM:
  MyLLM:
    type: openai
    base_url: http://127.0.0.1:8000/v1
    model_name: your-model-name
    api_key: dummy-key
```

### Mẫu 2: Buộc prompt trả lời tiếng Việt

Trong `agent-base-prompt.txt`, thêm rule:

```text
Luôn trả lời bằng tiếng Việt, ngắn gọn, tự nhiên, trừ khi người dùng yêu cầu ngôn ngữ khác.
```

## 7. Cách kiểm tra nhanh

### Kiểm tra 1: ASR

Nói:

```text
Hôm nay thời tiết thế nào?
```

Xem log xem ASR có nhận đúng tiếng Việt không.

### Kiểm tra 2: LLM

Nếu ASR đúng nhưng LLM trả lời tiếng Trung, lỗi nằm ở prompt hoặc `language`.

### Kiểm tra 3: TTS

Nếu text đã tiếng Việt mà giọng đọc vẫn không phải tiếng Việt, lỗi nằm ở TTS.

## 8. Checklist cuối

1. ASR nhận tiếng Việt đúng.
2. `agent-base-prompt.txt` yêu cầu trả lời tiếng Việt.
3. `PromptManager` đang chèn `language` đúng.
4. `selected_module.TTS` trỏ đúng block.
5. Block TTS có `language` hoặc tham số ngôn ngữ phù hợp.
6. LLM đủ mạnh với tiếng Việt.
7. Nếu có `manager-api`, sửa đúng nơi server thật sự đọc config.
8. Restart server và mở session mới sau khi đổi cấu hình.

## 9. Kết luận

Muốn server nhận và trả lời tiếng Việt ổn định, hãy làm đủ 4 việc:

- chọn ASR tốt cho tiếng Việt
- ép prompt mặc định tiếng Việt
- đặt `language` của TTS thành tiếng Việt
- đảm bảo config thật sự đang được server dùng
