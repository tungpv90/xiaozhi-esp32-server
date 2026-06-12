# Cấu hình server tùy chỉnh trên firmware Xiaoge build sẵn

## Bước 1: Xác nhận version

Nạp firmware bản `1.6.1` trở lên do Xiaoge build sẵn:
[releases](https://github.com/78/xiaozhi-esp32/releases)

## Bước 2: Chuẩn bị địa chỉ OTA

Nếu bạn dùng full module thì sẽ có địa chỉ OTA.

Mở OTA bằng trình duyệt, ví dụ:

```text
https://2662r3426b.vicp.fun/xiaozhi/ota/
```

Nếu hiện "OTA接口运行正常..." thì tiếp tục.

Nếu không bình thường, có thể bạn chưa cấu hình `Websocket` trong `智控台`.

1. Đăng nhập siêu quản trị viên
2. Vào `参数管理`
3. Tìm `server.websocket` và nhập websocket, ví dụ:

```text
wss://2662r3426b.vicp.fun/xiaozhi/v1/
```

Refresh lại OTA cho đến khi bình thường.

## Bước 3: Vào chế độ cấu hình mạng

Vào chế độ cấu hình của thiết bị, bấm "Advanced options" và nhập địa chỉ `ota` của server, sau đó lưu và reboot.

![Tham khảo cấu hình OTA](../docs/images/firmware-setting-ota.png)

## Bước 4: Đánh thức Xiaozhi và xem log

Đánh thức Xiaozhi để kiểm tra log có chạy bình thường không.

## Câu hỏi thường gặp

1. [Vì sao câu nói bị nhận sai ngôn ngữ?](./FAQ.md)
2. [Vì sao TTS báo file không tồn tại?](./FAQ.md)
3. [TTS hay lỗi hoặc timeout](./FAQ.md)
4. [Wi-Fi được nhưng 4G không vào](./FAQ.md)
5. [Làm sao tăng tốc phản hồi?](./FAQ.md)
6. [Tôi nói chậm, Xiaozhi hay cướp lời](./FAQ.md)
7. [Tôi muốn điều khiển đèn, điều hòa, bật/tắt từ xa](./FAQ.md)
