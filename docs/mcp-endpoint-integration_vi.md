# Hướng dẫn dùng MCP endpoint

Tài liệu này dùng ví dụ MCP calculator của Xiaoge để hướng dẫn cách nối service MCP tự viết vào endpoint của bạn.

Điều kiện tiên quyết là `xiaozhi-server` đã bật MCP endpoint. Nếu chưa, hãy làm theo [hướng dẫn này](./mcp-endpoint-enable.md) trước.

## Cách nối một MCP đơn giản như calculator

### Nếu bạn dùng full module

Vào `智控台` -> `智能体管理` -> `配置角色`, rồi bấm `编辑功能` cạnh phần `意图识别`.

Trong cửa sổ hiện ra, kéo xuống cuối sẽ thấy `MCP接入点`. Đó là địa chỉ MCP endpoint của agent, giữ lại để dùng ở bước sau.

### Nếu bạn dùng đơn module

Nếu bạn đã cấu hình MCP endpoint trong file config, khi khởi động sẽ thấy log dạng:

```text
mcp接入点是 ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc
```

Đó chính là `MCP接入点地址`.

## Bước 1: Tải code MCP calculator

Mở repo:
https://github.com/78/mcp-calculator

Tải ZIP, đổi tên thư mục thành `mcp-calculator`, rồi cài dependency:

```bash
cd mcp-calculator
conda remove -n mcp-calculator --all -y
conda create -n mcp-calculator python=3.10 -y
conda activate mcp-calculator
pip install -r requirements.txt
```

## Bước 2: Chạy

Trước khi chạy, lấy địa chỉ MCP endpoint từ agent của bạn, ví dụ:

```text
ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc
```

Thiết lập biến môi trường:

```bash
export MCP_ENDPOINT=ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc
```

Rồi chạy:

```bash
python mcp_pipe.py calculator.py
```

### Nếu bạn dùng cấu hình智控台

Sau khi chạy xong, vào lại `智控台` và refresh trạng thái MCP để thấy danh sách tool.

### Nếu bạn dùng đơn module

Khi thiết bị kết nối thành công, log sẽ có `calculator` trong danh sách function:

```text
250705 -INFO-当前支持的函数列表: [ 'get_time', 'get_lunar', 'play_music', 'get_weather', 'handle_exit_intent', 'calculator']
```

Nếu có `calculator` thì agent có thể gọi tool này theo ý định.
