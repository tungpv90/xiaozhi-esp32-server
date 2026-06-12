# Hướng dẫn dùng nguồn ngữ cảnh

## Tổng quan

`Nguồn ngữ cảnh` là cách bổ sung `data source` vào ngữ cảnh của system prompt cho Xiaozhi.

Khi Xiaozhi được đánh thức, nó sẽ lấy dữ liệu từ hệ thống bên ngoài và chèn động vào `System Prompt`, để nó có thể "cảm nhận" trạng thái của một sự vật tại thời điểm đó.

Điểm khác biệt giữa nó với MCP và bộ nhớ:

- `Nguồn ngữ cảnh` bắt buộc Xiaozhi phải cảm nhận dữ liệu từ thế giới bên ngoài.
- `Bộ nhớ (Mem)` là để nó nhớ đã nói gì trước đó.
- `MCP (function call)` là dùng khi cần gọi một năng lực hay tri thức cụ thể.

Qua tính năng này, ngay lúc Xiaozhi được đánh thức, nó có thể "cảm nhận" được:

- Trạng thái cảm biến sức khỏe con người như nhiệt độ, huyết áp, SpO2
- Dữ liệu thời gian thực của hệ thống nghiệp vụ như tải máy chủ, việc cần làm, giá cổ phiếu
- Bất kỳ thông tin văn bản nào có thể lấy qua HTTP API

**Lưu ý**: tính năng này chủ yếu giúp Xiaozhi cảm nhận trạng thái khi vừa được đánh thức. Nếu bạn muốn nó lấy trạng thái theo thời gian thực sau khi đã thức dậy, nên kết hợp thêm MCP.

## Cách hoạt động

1. **Cấu hình nguồn**: người dùng khai báo một hoặc nhiều địa chỉ HTTP API.
2. **Kích hoạt yêu cầu**: khi hệ thống xây prompt, nếu thấy placeholder `{{ dynamic_context }}`, nó sẽ gọi tất cả API đã cấu hình.
3. **Tự động chèn**: dữ liệu API trả về sẽ được định dạng thành danh sách Markdown và thay thế vào `{{ dynamic_context }}`.

## Quy ước API

Để Xiaozhi phân tích đúng dữ liệu, API của bạn cần đáp ứng:

- **Phương thức**: `GET`
- **Header**: hệ thống sẽ tự thêm trường `device-id` vào Request Header.
- **Định dạng phản hồi**: phải trả về JSON và có các trường `code` và `data`.

### Ví dụ phản hồi

**Trường hợp 1: trả về cặp key-value**
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "客厅温度": "26℃",
    "客厅湿度": "45%",
    "大门状态": "已关闭"
  }
}
```

Kết quả chèn:
```markdown
<context>
- **客厅温度：** 26℃
- **客厅湿度：** 45%
- **大门状态：** 已关闭
</context>
```

**Trường hợp 2: trả về danh sách**
```json
{
  "code": 0,
  "data": [
    "您有10个待办事项",
    "当前汽车的行驶速度是100km每小时"
  ]
}
```

Kết quả chèn:
```markdown
<context>
- 您有10个待办事项
- 当前汽车的行驶速度是100km每小时
</context>
```

## Hướng dẫn cấu hình

### Cách 1: Cấu hình trên智控台

1. Đăng nhập智控台 và vào trang **Cấu hình vai trò**.
2. Tìm mục **Nguồn ngữ cảnh**.
3. Bấm **Thêm**, nhập địa chỉ API.
4. Nếu API cần xác thực, thêm `Authorization` hoặc header khác ở phần header.
5. Lưu cấu hình.

### Cách 2: Cấu hình bằng file

Sửa file `xiaozhi-server/data/.config.yaml` và thêm đoạn `context_providers`:

```yaml
# Cấu hình nguồn ngữ cảnh
context_providers:
  - url: "http://api.example.com/data"
    headers:
      Authorization: "Bearer your-token"
  - url: "http://another-api.com/data"
```

## Kích hoạt tính năng

Mặc định, file prompt hệ thống (`data/.agent-base-prompt.txt`) đã có sẵn placeholder `{{ dynamic_context }}`, bạn không cần thêm thủ công.

**Ví dụ:**

```markdown
<context>
[Quan trọng! Thông tin dưới đây đã được cung cấp theo thời gian thực, không cần gọi công cụ để tra cứu, hãy dùng trực tiếp:]
- **Mã thiết bị:** {{device_id}}
- **Thời gian hiện tại:** {{current_time}}
...
{{ dynamic_context }}
</context>
```

Nếu không cần dùng tính năng này, bạn có thể không cấu hình nguồn ngữ cảnh nào hoặc xóa `{{ dynamic_context }}` khỏi file prompt.

## Phụ lục: ví dụ mock server

Để dễ kiểm thử và phát triển, chúng tôi cung cấp một script Python Mock Server đơn giản. Bạn có thể chạy nó để mô phỏng API tại máy local.

**mock_api_server.py**

```python
import http.server
import socketserver
import json
from urllib.parse import urlparse, parse_qs

# Cấu hình cổng
PORT = 8081

class MockRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Phân tích đường dẫn và tham số
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)

        response_data = {}
        status_code = 200

        print(f"Nhận request: {path}, tham số: {query}")

        # Case 1: mô phỏng dữ liệu sức khỏe (trả về dict)
        if path == "/health":
            device_id = self.headers.get("device-id", "unknown_device")
            print(f"device_id: {device_id}")
            response_data = {
                "code": 0,
                "msg": "success",
                "data": {
                    "测试设备ID": device_id,
                    "心率": "80 bpm",
                    "血压": "120/80 mmHg",
                    "状态": "良好"
                }
            }

        # Case 2: mô phỏng danh sách tin tức (trả về list)
        elif path == "/news/list":
            response_data = {
                "code": 0,
                "msg": "success",
                "data": [
                    "今日头条：Python 3.14 发布",
                    "科技新闻：AI 助手改变生活",
                    "本地新闻：明日有大雨，记得带伞"
                ]
            }

        # Case 3: mô phỏng bản tin thời tiết (trả về chuỗi)
        elif path == "/weather/simple":
            response_data = {
                "code": 0,
                "msg": "success",
                "data": "今日晴转多云，气温 20-25 度，空气质量优，适合出行。"
            }

        # Case 4: mô phỏng chi tiết thiết bị
        elif path == "/device/info":
            device_id = self.headers.get("device-id", "unknown_device")
            response_data = {
                "code": 0,
                "msg": "success",
                "data": {
                    "查询方式": "Header参数",
                    "设备ID": device_id,
                    "电量": "85%",
                    "固件": "v2.0.1"
                }
            }
        else:
            status_code = 404
            response_data = {"error": "接口不存在"}

        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))

# Khởi động dịch vụ
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), MockRequestHandler) as httpd:
    print("==================================================")
    print(f"Mock API Server đã khởi động: http://localhost:{PORT}")
    print("Danh sách API khả dụng:")
    print(f"1. [Dict] http://localhost:{PORT}/health")
    print(f"2. [List] http://localhost:{PORT}/news/list")
    print(f"3. [Text] http://localhost:{PORT}/weather/simple")
    print(f"4. [Param] http://localhost:{PORT}/device/info")
    print("==================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\\nDịch vụ đã dừng")
```
