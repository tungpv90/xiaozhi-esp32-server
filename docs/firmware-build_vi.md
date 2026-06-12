# Biên dịch firmware ESP32

## Bước 1: Chuẩn bị địa chỉ OTA

Từ phiên bản `0.3.12`, dù là triển khai đơn giản hay full module, dự án đều có địa chỉ OTA.

Vì cách cấu hình OTA ở hai chế độ khác nhau nên hãy chọn đúng phần phù hợp.

### Nếu bạn dùng triển khai đơn giản

Mở địa chỉ OTA của bạn bằng trình duyệt, ví dụ:

```text
http://192.168.1.25:8003/xiaozhi/ota/
```

Nếu hiện "OTA接口运行正常..." thì dùng `test_page.html` để kiểm tra websocket được trả về.

Nếu không truy cập được, hãy sửa `server.websocket` trong `.config.yaml`, restart rồi thử lại cho đến khi `test_page.html` mở được.

### Nếu bạn dùng full module

Mở địa chỉ OTA, ví dụ:

```text
http://192.168.1.25:8002/xiaozhi/ota/
```

Nếu hiện "OTA接口运行正常..." thì tiếp tục.

Nếu báo không bình thường, có thể bạn chưa cấu hình `Websocket` trong `智控台`.

1. Đăng nhập bằng siêu quản trị viên
2. Vào `参数管理`
3. Tìm `server.websocket` và nhập websocket của bạn, ví dụ:

```text
ws://192.168.1.25:8000/xiaozhi/v1/
```

Sau đó refresh lại OTA để kiểm tra.

## Bước 2: Cấu hình môi trường

Làm theo hướng dẫn này để dựng môi trường ESP IDF:
[Windows dựng môi trường ESP IDF 5.3.2 và biên dịch Xiaozhi](https://icnynnzcwou8.feishu.cn/wiki/JEYDwTTALi5s2zkGlFGcDiRknXf)

## Bước 3: Mở file cấu hình

Tải source `xiaozhi-esp32` của Xiaoge.

Mở file `xiaozhi-esp32/main/Kconfig.projbuild`.

## Bước 4: Sửa địa chỉ OTA

Tìm `OTA_URL` và đổi giá trị `default` từ:

```text
https://api.tenclass.net/xiaozhi/ota/
```

thành địa chỉ OTA của bạn, ví dụ:

```text
http://192.168.1.25:8002/xiaozhi/ota/
```

## Bước 5: Đặt tham số biên dịch

```bash
cd xiaozhi-esp32
idf.py set-target esp32s3
idf.py menuconfig
```

Vào `Xiaozhi Assistant`, đặt `BOARD_TYPE` đúng với model board của bạn rồi lưu.

## Bước 6: Biên dịch firmware

```bash
idf.py build
```

## Bước 7: Đóng gói firmware bin

```bash
cd scripts
python release.py
```

File `merged-binary.bin` sẽ được tạo trong thư mục `build`. Đây là file để nạp vào thiết bị.

Nếu lệnh đóng gói báo lỗi liên quan `zip`, có thể bỏ qua miễn là `merged-binary.bin` đã được tạo.

## Bước 8: Nạp firmware

Kết nối ESP32 với máy tính, rồi mở:

```text
https://espressif.github.io/esp-launchpad/
```

Làm theo hướng dẫn trong bài:
[Flash tool / nạp firmware trên web](https://ccnphfhqs21z.feishu.cn/wiki/Zpz4wXBtdimBrLk25WdcXzxcnNS)

Sau khi nạp và kết nối mạng thành công, đánh thức Xiaozhi và xem log phía server.

## Câu hỏi thường gặp

1. [Vì sao câu nói bị nhận sai ngôn ngữ?](./FAQ.md)
2. [Vì sao TTS báo file không tồn tại?](./FAQ.md)
3. [TTS hay lỗi hoặc timeout](./FAQ.md)
4. [Wi-Fi được nhưng 4G không vào](./FAQ.md)
5. [Làm sao tăng tốc phản hồi?](./FAQ.md)
6. [Tôi nói chậm, Xiaozhi hay cướp lời](./FAQ.md)
7. [Tôi muốn điều khiển đèn, điều hòa, bật/tắt từ xa](./FAQ.md)
