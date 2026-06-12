# Hướng dẫn tích hợp HomeAssistant với server mã nguồn mở Xiaozhi ESP32

[TOC]

---

## Giới thiệu

Tài liệu này hướng dẫn cách tích hợp thiết bị ESP32 với HomeAssistant.

## Điều kiện tiên quyết

- Đã cài và cấu hình `HomeAssistant`
- Model được chọn trong ví dụ là ChatGLM miễn phí, hỗ trợ function call

## Trước khi bắt đầu

### 1. Lấy địa chỉ mạng của HA

Mở Home Assistant bằng địa chỉ IP của bạn, ví dụ:

```text
http://192.168.4.7:8123
```

Nếu Home Assistant và `xiaozhi-server` nằm cùng mạng LAN, bạn có thể xem IP trong:

- `Settings` -> `System` -> `Network`

Hoặc mở trực tiếp nếu có địa chỉ OAuth:

```text
http://homeassistant.local:8123
```

### 2. Lấy API key của Home Assistant

Đăng nhập HomeAssistant, vào avatar góc trái dưới -> `Personal`, chuyển sang tab `Security`, xuống mục `Long-Lived Access Tokens` để tạo API key.

## Cách 1: Dùng tính năng HA do cộng đồng Xiaozhi hỗ trợ

### Mô tả

- Nếu sau này thêm thiết bị mới, bạn phải restart `xiaozhi-esp32-server` để cập nhật.
- Cần đã tích hợp `Xiaomi Home` vào HomeAssistant.
- Cần `智控台` của `xiaozhi-esp32-server` hoạt động bình thường.

### Các bước cấu hình

#### 1. Chuẩn bị danh sách thiết bị trên HomeAssistant

Vào `Settings` -> `Devices & Services` -> `Entities`, tìm entity cần điều khiển.

Khi mở entity, bấm vào nút cài đặt để lấy `entity_id`.

Ghi theo định dạng:

```text
Vị trí,tên thiết bị,entity_id;
```

Ví dụ:

```text
公司,玩具灯,switch.cuco_cn_460494544_cp1_on_p_2_1;
公司,台灯,switch.iot_cn_831898993_socn1_on_p_2_1;
```

#### 2. Đăng nhập `智控台`

Vào `智能体管理`, chọn agent, bấm `配置角色`.

Đặt intent thành `外挂的大模型意图识别` hoặc `大模型自主函数调用`, rồi bấm `编辑功能`.

Tick:

- `HomeAssistant设备状态查询`
- `HomeAssistant设备状态修改`

Sau đó cấu hình địa chỉ HomeAssistant, key và danh sách thiết bị, rồi lưu.

#### 3. Đánh thức thiết bị

Nói với ESP32, ví dụ: "mở đèn XXX".

## Cách 2: Dùng Home Assistant voice assistant như LLM tool

### Mô tả

- Cách này có nhược điểm là không dùng được plugin `function_call` của hệ sinh thái Xiaozhi.
- Bù lại, bạn dùng được thao tác gốc của Home Assistant và chat vẫn giữ nguyên.

### Cấu hình

1. Cấu hình voice assistant / LLM tool trong Home Assistant.
2. Lấy `agent-id` từ `Developer Tools` -> `Actions` -> `conversation.process`.
3. Vào file `config.yaml` của `xiaozhi-esp32-server`, tìm cấu hình Home Assistant trong LLM và nhập:
   - địa chỉ HA
   - API key
   - `agent_id`
4. Đặt `selected_module.LLM = HomeAssistant`
5. Đặt `selected_module.Intent = nointent`
6. Restart server.

## Cách 3: Dùng MCP service của Home Assistant

### Mô tả

- Cần cài `Model Context Protocol Server` trong Home Assistant.
- Cách này vẫn dùng được plugin cộng đồng của Xiaozhi và vẫn có thể dùng bất kỳ LLM nào hỗ trợ `function_call`.

### Các bước

#### 1. Cài MCP service

Làm theo trang chính thức:
[Model Context Protocol Server](https://www.home-assistant.io/integrations/mcp_server/)

Hoặc vào `Settings > Devices & Services`, bấm `Add Integration`, chọn `Model Context Protocol Server`.

#### 2. Cấu hình MCP của server Xiaozhi

Vào thư mục `data`, tìm `.mcp_server_settings.json`.

Nếu chưa có, copy file `mcp_server_settings.json` từ thư mục gốc vào `data` rồi đổi tên thành `.mcp_server_settings.json`.

Sửa phần `mcpServers`:

```json
"Home Assistant": {
  "command": "mcp-proxy",
  "args": [
    "http://YOUR_HA_HOST/mcp_server/sse"
  ],
  "env": {
    "API_ACCESS_TOKEN": "YOUR_API_ACCESS_TOKEN"
  }
}
```

Lưu ý:

- `YOUR_HA_HOST` nếu đã có `http/https` thì chỉ nhập host:port
- `YOUR_API_ACCESS_TOKEN` là API key đã tạo ở bước trước
- Nếu không có cấu hình MCP server nào phía sau, hãy bỏ dấu phẩy cuối cùng

Ví dụ:

```json
"mcpServers": {
  "Home Assistant": {
    "command": "mcp-proxy",
    "args": [
      "http://192.168.1.101:8123/mcp_server/sse"
    ],
    "env": {
      "API_ACCESS_TOKEN": "abcd.efghi.jkl"
    }
  }
}
```

#### 3. Cấu hình hệ thống Xiaozhi

1. Chọn một LLM có hỗ trợ `function_call` làm LLM chính, nhưng không chọn Home Assistant làm LLM tool. Ví dụ: ChatGLM hoặc Doubao.
2. Trong `config.yaml`, cấu hình LLM và đặt `selected_module.Intent` thành `function_call`.
3. Restart server.
