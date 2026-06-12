# Hướng dẫn triển khai MQTT gateway

`xiaozhi-esp32-server` có thể kết hợp với project [xiaozhi-mqtt-gateway](https://github.com/78/xiaozhi-mqtt-gateway) để hỗ trợ kết nối MQTT+UDP cho phần cứng Xiaozhi.

Tài liệu gồm 3 phần:

- Triển khai MQTT gateway
- Cấu hình khi chạy full module
- Cấu hình khi chạy đơn module

## Chuẩn bị

Tạo địa chỉ `mqtt-websocket` bằng cách thêm `?from=mqtt_gateway` vào websocket gốc.

Ví dụ:

```text
ws://127.0.0.1:8000/xiaozhi/v1/?from=mqtt_gateway
```

Nếu chạy Docker:

```text
ws://ip-lan-cua-may-chu:8000/xiaozhi/v1/?from=mqtt_gateway
```

## Lưu ý quan trọng

Nếu triển khai trên server thật, cần mở các cổng:

- `1883`
- `8884`
- `8007`

Trong đó `8884` dùng UDP, các cổng còn lại dùng TCP.

## 1. Triển khai MQTT gateway

### 1. Clone project

```bash
git clone https://ghfast.top/https://github.com/xinnan-tech/xiaozhi-mqtt-gateway.git
cd xiaozhi-mqtt-gateway
```

### 2. Cài dependency

```bash
npm install
npm install -g pm2
```

### 3. Cấu hình `config.json`

```bash
cp config/mqtt.json.example config/mqtt.json
```

Trong `config/mqtt.json`, thay `chat_servers` bằng địa chỉ websocket ở phần chuẩn bị:

```json
{
  "production": {
    "chat_servers": [
      "ws://127.0.0.1:8000/xiaozhi/v1/?from=mqtt_gateway"
    ]
  },
  "debug": false,
  "max_mqtt_payload_size": 8192,
  "mcp_client": {
    "capabilities": {},
    "client_info": {
      "name": "xiaozhi-mqtt-client",
      "version": "1.0.0"
    },
    "max_tools_count": 128
  }
}
```

### 4. Tạo `.env`

```env
PUBLIC_IP=your-ip
MQTT_PORT=1883
UDP_PORT=8884
API_PORT=8007
MQTT_SIGNATURE_KEY=test
SERVER_SECRET=Te1st12134
```

Lưu ý:

- `PUBLIC_IP` phải là IP public hoặc domain thật
- `MQTT_SIGNATURE_KEY` nên đặt đủ mạnh
- `SERVER_SECRET` phải khớp với `server.secret` hoặc `server.auth_key`

### 5. Khởi động MQTT gateway

```bash
pm2 start ecosystem.config.js
pm2 logs xz-mqtt
```

Khi thấy log kiểu:

```text
MQTT 服务器正在监听端口 1883
UDP 服务器正在监听 x.x.x.x:8884
```

là đã chạy xong.

## 2. Full module

Kiểm tra version `智控台` phải từ `0.7.7` trở lên.

Trong `参数管理`, lần lượt set:

- `server.mqtt_gateway` = `PUBLIC_IP:MQTT_PORT`
- `server.mqtt_signature_key` = `MQTT_SIGNATURE_KEY`
- `server.udp_gateway` = `PUBLIC_IP:UDP_PORT`
- `server.mqtt_manager_api` = `PUBLIC_IP:API_PORT`

Sau đó dùng curl kiểm tra OTA có trả cấu hình MQTT hay không.

## 3. Đơn module

Trong `data/.config.yaml`, cấu hình:

- `server.mqtt_gateway`
- `server.mqtt_signature_key`
- `server.udp_gateway`

Sau đó dùng curl kiểm tra OTA trả MQTT config.
