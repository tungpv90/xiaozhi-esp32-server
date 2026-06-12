# Hướng dẫn dùng LLM của riêng bạn

Tài liệu này mô tả cách thay thế LLM mặc định bằng một model do bạn tự vận hành trong `main/xiaozhi-server`.

## Cách hiểu nhanh

Trong dự án này, LLM được chọn qua:

- `selected_module.LLM`
- block cấu hình tương ứng trong `LLM:`

Luồng khởi tạo nằm ở `main/xiaozhi-server/core/utils/modules_initialize.py`. Khi server khởi động, nó đọc `selected_module.LLM`, tìm block cùng tên trong `LLM`, rồi tạo provider tương ứng dựa trên trường `type`.

Nói ngắn gọn:

- `type: openai` dùng cho mọi endpoint có API tương thích OpenAI
- `type: ollama` dùng cho Ollama
- `type: xinference` dùng cho Xinference
- `type: dify`, `type: fastgpt`, `type: gemini`, `type: coze`, `type: AliBL`, `type: homeassistant` dùng cho backend tương ứng

## Cách dễ nhất

Nếu model của bạn có API OpenAI-compatible, đây là cách đơn giản nhất.

### Điều kiện

- Có một endpoint trả về `/v1/chat/completions`
- Hỗ trợ `messages`
- Tốt hơn nếu hỗ trợ `stream`
- Nếu bạn muốn function call, endpoint đó phải hỗ trợ `tools`

### Cấu hình mẫu

```yaml
selected_module:
  LLM: MyLLM

LLM:
  MyLLM:
    type: openai
    base_url: http://127.0.0.1:8000/v1
    model_name: your-model-name
    api_key: dummy-key
```

### Ý nghĩa từng trường

- `type`: chọn provider `openai` trong code
- `base_url`: địa chỉ API của model, nếu chưa có `/v1` thì nên thêm rõ ràng
- `model_name`: tên model mà server LLM của bạn nhận
- `api_key`: nhiều server tự host không cần key thật, nhưng client OpenAI trong code vẫn cần chuỗi bất kỳ

### Điểm cần lưu ý

File `main/xiaozhi-server/core/providers/llm/openai/openai.py` sẽ:

- khởi tạo client OpenAI
- gọi `chat.completions.create(...)`
- stream token ra ngoài

Nếu server của bạn không hỗ trợ OpenAI-compatible thật sự, provider này sẽ không dùng được.

## Các backend tự host phổ biến

### 1. Ollama

Provider đã có sẵn trong code: `type: ollama`

```yaml
selected_module:
  LLM: OllamaLLM

LLM:
  OllamaLLM:
    type: ollama
    model_name: qwen2.5
    base_url: http://localhost:11434
```

Ghi chú:

- code sẽ tự nối thêm `/v1` nếu thiếu
- phù hợp khi bạn chạy model local bằng Ollama
- có nhánh riêng cho Qwen3: nếu model bắt đầu bằng `qwen3`, code sẽ thêm `/no_think` vào user prompt để hạn chế suy nghĩ dài

### 2. Xinference

Provider đã có sẵn: `type: xinference`

```yaml
selected_module:
  LLM: XinferenceLLM

LLM:
  XinferenceLLM:
    type: xinference
    model_name: qwen2.5:72b-AWQ
    base_url: http://127.0.0.1:9997
```

Ghi chú:

- code sẽ tự nối `/v1`
- dùng được theo kiểu OpenAI-compatible

### 3. LM Studio

Trong `config.yaml` có sẵn mẫu `LMStudioLLM`, nhưng provider vẫn dùng `type: openai`.

```yaml
selected_module:
  LLM: LMStudioLLM

LLM:
  LMStudioLLM:
    type: openai
    model_name: deepseek-r1-distill-llama-8b@q4_k_m
    base_url: http://127.0.0.1:1234/v1
    api_key: lm-studio
```

### 4. vLLM hoặc server OpenAI-compatible tự viết

Đây cũng dùng `type: openai`.

Ví dụ:

```yaml
selected_module:
  LLM: MyLocalVllm

LLM:
  MyLocalVllm:
    type: openai
    model_name: my-model
    base_url: http://127.0.0.1:8000/v1
    api_key: dummy
    temperature: 0.7
    max_tokens: 1024
```

Nếu bạn tự viết server, chỉ cần đảm bảo:

- request nhận đúng schema OpenAI chat completion
- response stream ra từng delta text
- nếu muốn tool call, trả `tool_calls` theo format OpenAI

## Khi nào cần `function call`

Nếu bạn muốn server điều khiển thiết bị, gọi plugin, lấy thời tiết, phát nhạc, hoặc thực hiện tác vụ công cụ, model phải hỗ trợ function call/tool call.

Trong repo:

- provider `openai` có `response_with_functions(...)`
- provider `xinference` cũng có `response_with_functions(...)`
- `Gemini` có mapping riêng cho tools
- `Ollama` có xử lý `tools`
- `AliBL` và `FastGPT` có mức hỗ trợ hạn chế hơn hoặc chưa đầy đủ tùy backend
- `Home Assistant` không dùng function call kiểu XianZhi AI, nó tự xử lý theo luồng riêng

Nếu model của bạn không hỗ trợ tool calling:

- server vẫn có thể chat bình thường
- nhưng các chức năng như gọi plugin, điều khiển thiết bị, intent phức tạp sẽ bị giới hạn

## Cách bật một LLM riêng trong dự án

### Bước 1: Chọn kiểu backend

Chọn một trong hai nhóm:

- `OpenAI-compatible` nếu bạn tự host bằng vLLM, LM Studio, endpoint riêng, hoặc một service giống OpenAI
- provider chuyên biệt như `Ollama` hoặc `Xinference` nếu bạn dùng đúng hệ sinh thái đó

### Bước 2: Thêm block cấu hình

Thêm một mục mới trong `LLM:` theo kiểu backend bạn chọn.

Ví dụ cho endpoint riêng:

```yaml
LLM:
  MyLLM:
    type: openai
    base_url: http://127.0.0.1:8000/v1
    model_name: your-model-name
    api_key: dummy
```

### Bước 3: Đổi `selected_module.LLM`

```yaml
selected_module:
  LLM: MyLLM
```

### Bước 4: Kiểm tra prompt và ngôn ngữ

LLM chỉ là engine trả lời. Muốn nó trả lời đúng tiếng Việt, bạn phải:

- sửa prompt gốc nếu cần
- bảo đảm `language` trong prompt là tiếng Việt
- chọn model đủ mạnh với tiếng Việt

### Bước 5: Restart server

Prompt hệ thống được build lại khi có session mới. Sau khi đổi config:

- restart Python server
- mở session mới trên thiết bị

## Nếu server lấy config từ `manager-api`

Đây là điểm rất dễ nhầm.

Nếu `manager-api.url` có trong `data/.config.yaml` hoặc config bootstrap, server sẽ lấy cấu hình từ API thay vì chỉ dùng file local.

Khi đó:

- sửa `main/xiaozhi-server/config.yaml` local chưa chắc có tác dụng
- bạn phải sửa config ở phía API trả về
- hoặc sửa file bootstrap `data/.config.yaml` đúng chế độ deploy

## Mẫu khuyến nghị

### Cấu hình local, dễ thử nghiệm

```yaml
selected_module:
  LLM: OllamaLLM

LLM:
  OllamaLLM:
    type: ollama
    model_name: qwen2.5
    base_url: http://127.0.0.1:11434
```

### Cấu hình OpenAI-compatible cho model tự host

```yaml
selected_module:
  LLM: MyLLM

LLM:
  MyLLM:
    type: openai
    base_url: http://127.0.0.1:8000/v1
    model_name: my-model
    api_key: dummy
    temperature: 0.7
    top_p: 0.9
```

### Cấu hình dùng Xinference

```yaml
selected_module:
  LLM: XinferenceLLM

LLM:
  XinferenceLLM:
    type: xinference
    base_url: http://127.0.0.1:9997
    model_name: qwen2.5:7b
```

## Lỗi hay gặp

- `base_url` thiếu `/v1` với endpoint OpenAI-compatible
- `model_name` không đúng tên model server đang expose
- server tự host không hỗ trợ `stream`
- model không hỗ trợ `tools` nhưng lại bật luồng plugin/function call
- sửa local config trong khi hệ thống đang lấy config từ `manager-api`

## Cách kiểm tra nhanh

1. Bật server LLM riêng của bạn.
2. Gọi thử endpoint bằng một client OpenAI-compatible.
3. Đảm bảo `selected_module.LLM` trỏ đúng block mới.
4. Khởi động server Xiaozhi.
5. Mở log và kiểm tra provider đã được init đúng block chưa.

## Kết luận

Muốn dùng LLM riêng trong dự án này, cách ổn định nhất là:

- làm model của bạn lộ ra API OpenAI-compatible
- cấu hình `LLM:<Tên>` với `type: openai`
- đổi `selected_module.LLM` sang block đó
- nếu cần tool call, bảo đảm backend có hỗ trợ `tools`
- nếu hệ thống lấy config từ `manager-api`, chỉnh ở nơi API trả về chứ không chỉ sửa file local

