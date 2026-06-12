# Hướng dẫn tự động nâng cấp firmware OTA cho triển khai đơn module

Tài liệu này hướng dẫn cách bật OTA auto upgrade cho kịch bản đơn module.

Nếu bạn đã dùng full module thì có thể bỏ qua.

## Giới thiệu

Trong đơn module, `xiaozhi-server` có sẵn chức năng quản lý OTA firmware, có thể tự phát hiện phiên bản thiết bị và đẩy firmware mới phù hợp.

## Điều kiện

- Đã chạy thành công `xiaozhi-server` theo kiểu đơn module
- Thiết bị kết nối được tới server

## Bước 1: Chuẩn bị file firmware

### 1. Tạo thư mục firmware

```bash
mkdir -p data/bin
```

### 2. Quy tắc đặt tên

```text
{model}_{version}.bin
```

Ví dụ:

```text
bread-compact-wifi_1.6.6.bin
lichuang-dev_2.0.0.bin
```

### 3. Đặt file firmware

Copy file `xiaozhi.bin` vào `data/bin`, ví dụ:

```bash
cp xiaozhi.bin data/bin/bread-compact-wifi_1.6.6.bin
```

Lưu ý: file nâng cấp là `xiaozhi.bin`, không phải `merged-binary.bin`.

## Bước 2: Cấu hình địa chỉ public

Chỉ cần nếu server của bạn deploy public.

Trong `data/.config.yaml`, đặt:

```yaml
server:
  vision_explain: http://your-domain-or-ip:port/mcp/vision/explain
```

Ví dụ:

```yaml
server:
  vision_explain: http://192.168.1.100:8003/mcp/vision/explain
```

Hoặc:

```yaml
server:
  vision_explain: http://yourdomain.com:8003/mcp/vision/explain
```

Lưu ý:

- Domain/IP phải truy cập được từ thiết bị
- Docker không được dùng địa chỉ nội bộ như `127.0.0.1`
- Nếu dùng Nginx reverse proxy, hãy điền địa chỉ public bên ngoài

## Câu hỏi thường gặp

### 1. Thiết bị không nhận bản cập nhật

Kiểm tra:

- tên file có đúng format `{model}_{version}.bin`
- file có nằm trong `data/bin/`
- model trong tên file có khớp thiết bị
- version firmware mới có cao hơn version hiện tại
- log server có nhận request OTA hay không

### 2. Thiết bị báo không truy cập được đường dẫn tải

Kiểm tra:

- `server.vision_explain` đã đúng chưa
- cổng `8003` có mở chưa
- có phải đang dùng địa chỉ nội bộ Docker không
- firewall / Nginx có chặn không

### 3. Làm sao biết version hiện tại?

Xem log OTA:

```text
[ota_handler] - 设备 AA:BB:CC:DD:EE:FF 固件已是最新: 1.6.6
```

### 4. Đặt file firmware rồi nhưng chưa có hiệu lực

Hệ thống có cache mặc định 30 giây. Có thể:

- chờ 30 giây rồi gửi OTA request lại
- restart `xiaozhi-server`
- giảm `firmware_cache_ttl`
