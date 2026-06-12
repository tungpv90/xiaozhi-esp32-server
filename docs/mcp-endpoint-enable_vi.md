# Hướng dẫn triển khai MCP endpoint

Tài liệu này gồm 3 phần:

- Cách triển khai service MCP endpoint
- Cách cấu hình MCP endpoint khi dùng full module
- Cách cấu hình MCP endpoint khi dùng đơn module

## 1. Triển khai service MCP endpoint

### Bước 1: Tải mã nguồn

Mở:
https://github.com/xinnan-tech/mcp-endpoint-server

Tải ZIP rồi đổi tên thư mục thành `mcp-endpoint-server`.

### Bước 2: Chạy chương trình

```bash
cd mcp-endpoint-server

docker compose -f docker-compose.yml down
docker stop mcp-endpoint-server
docker rm mcp-endpoint-server
docker rmi ghcr.nju.edu.cn/xinnan-tech/mcp-endpoint-server:latest

docker compose -f docker-compose.yml up -d
docker logs -f mcp-endpoint-server
```

Log sẽ có dạng:

```text
250705 INFO-=====下面的地址分别是智控台/单模块MCP接入点地址====
250705 INFO-智控台MCP参数配置: http://172.22.0.2:8004/mcp_endpoint/health?key=abc
250705 INFO-单模块部署MCP接入点: ws://172.22.0.2:8004/mcp_endpoint/mcp/?token=def
250705 INFO-=====请根据具体部署选择使用，请勿泄露给任何人======
```

Vì chạy Docker nên không được dùng nguyên địa chỉ nội bộ trên log. Hãy đổi sang IP LAN thật của máy bạn.

Ví dụ IP máy là `192.168.1.25` thì:

```text
http://192.168.1.25:8004/mcp_endpoint/health?key=abc
ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=def
```

Mở `智控台MCP参数配置` bằng trình duyệt để kiểm tra, nếu thấy JSON như sau là đúng:

```json
{"result":{"status":"success","connections":{"tool_connections":0,"robot_connections":0,"total_connections":0}},"error":null,"id":null,"jsonrpc":"2.0"}
```

## 2. Cấu hình khi dùng full module

Trong `智控台`, vào `参数字典` -> `系统功能配置` và bật `MCP接入点`.

Sau đó vào `参数管理`, tìm `server.mcp_endpoint`, dán URL `智控台MCP参数配置` ở trên vào.

## 3. Cấu hình khi dùng đơn module

Trong `data/.config.yaml`, thêm:

```yaml
mcp_endpoint: ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=def
```

Khởi động lại server. Nếu log in ra:

```text
mcp接入点是 ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc
```

thì đã cấu hình thành công.
