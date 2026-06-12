# Hướng dẫn dùng mô hình thị giác

Tài liệu chia thành 2 phần:

- Cách bật vision khi chạy đơn module
- Cách bật vision khi chạy full module

Trước khi bật vision, bạn cần:

- Một thiết bị có camera và firmware đã có sẵn khả năng gọi camera, ví dụ `立创·实战派ESP32-S3开发板`
- Firmware đã nâng lên `1.6.6` hoặc cao hơn
- Đã chạy thông suốt module hội thoại cơ bản

## Đơn module

### Bước 1: Kiểm tra mạng

Vision mặc định dùng cổng `8003`.

- Nếu chạy Docker, kiểm tra `docker-compose.yml` đã mở cổng `8003` chưa
- Nếu chạy source, kiểm tra firewall đã cho phép cổng `8003` chưa

### Bước 2: Chọn model vision

Mở `data/.config.yaml` và đặt `selected_module.VLLM` thành model vision, ví dụ `ChatGLMVLLM`.

```yaml
selected_module:
  VAD: ..
  ASR: ..
  LLM: ..
  VLLM: ChatGLMVLLM
  TTS: ..
  Memory: ..
  Intent: ..
```

Sau đó lấy `api_key` từ [智谱AI](https://bigmodel.cn/usercenter/proj-mgmt/apikeys) và cấu hình:

```yaml
VLLM:
  ChatGLMVLLM:
    api_key: your_api_key
```

### Bước 3: Khởi động server

```bash
python app.py
```

hoặc:

```bash
docker restart xiaozhi-esp32-server
```

Log sẽ có:

```text
OTA接口是 http://...:8003/xiaozhi/ota/
视觉分析接口是 http://...:8003/mcp/vision/explain
Websocket地址是 ws://...:8000/xiaozhi/v1/
```

Mở `视觉分析接口` bằng trình duyệt hoặc curl:

```bash
curl -i 你的视觉分析接口
```

Nếu đúng sẽ thấy:

```text
MCP Vision 接口运行正常，视觉解释接口地址是：http://xxxx:8003/mcp/vision/explain
```

Nếu bạn chạy public hoặc Docker, hãy sửa:

```yaml
server:
  vision_explain: http://your-ip-or-domain:port/mcp/vision/explain
```

Ví dụ:

```yaml
server:
  vision_explain: http://111.111.111.111:8003/mcp/vision/explain
```

### Bước 4: Đánh thức thiết bị

Nói: "Hãy bật camera, nói cho tôi biết bạn nhìn thấy gì".

## Full module

### Bước 1: Kiểm tra mạng

- Docker: đảm bảo `docker-compose_all.yml` có map cổng `8003`
- Source: đảm bảo firewall cho phép `8003`

### Bước 2: Kiểm tra config

Mở `data/.config.yaml` và নিশ্চিত rằng cấu trúc giống `data/config_from_api.yaml`.

### Bước 3: Cấu hình key vision

Lấy API key từ [智谱AI](https://bigmodel.cn/usercenter/proj-mgmt/apikeys).

Trong `智控台`, vào `模型配置` -> `视觉打语言模型`, tìm `VLLM_ChatGLMVLLM`, bấm sửa và nhập API key.

Sau đó vào agent cần test, mở `配置角色`, kiểm tra `视觉大语言模型(VLLM)` đã chọn đúng model vision chưa.

### Bước 4: Khởi động server

```bash
python app.py
```

hoặc:

```bash
docker restart xiaozhi-esp32-server
```

Sau đó dùng trình duyệt hoặc `curl -i` để kiểm tra `视觉分析接口`.
