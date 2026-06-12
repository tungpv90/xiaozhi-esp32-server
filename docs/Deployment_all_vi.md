# Sơ đồ kiến trúc triển khai
![Tham khảo kiến trúc full module](../docs/images/deploy2.png)

# Cách 1: Docker chạy full module

Từ phiên bản `0.8.2`, image Docker phát hành của dự án chỉ hỗ trợ `x86`. Nếu cần `arm64`, hãy tự build theo [hướng dẫn này](docker-build.md).

## 1. Cài Docker

Nếu máy chưa có Docker, có thể cài theo [hướng dẫn này](https://www.runoob.com/docker/ubuntu-docker-install.html).

Có hai cách cài full module:

- [Dùng script tự động](./Deployment_all.md#11-lenh-tu-dong) (tác giả [@VanillaNahida](https://github.com/VanillaNahida))
- [Triển khai thủ công](./Deployment_all.md#12-trien-khai-thu-cong)

### 1.1 Script tự động

Có thể tham khảo [video hướng dẫn](https://www.bilibili.com/video/BV17bbvzHExd/). Lưu ý script hiện chủ yếu hỗ trợ Ubuntu.

Chạy bằng SSH với quyền root:

```bash
sudo bash -c "$(wget -qO- https://ghfast.top/https://raw.githubusercontent.com/xinnan-tech/xiaozhi-esp32-server/main/docker-setup.sh)"
```

Script sẽ tự:

1. Cài Docker
2. Cấu hình mirror
3. Tải image
4. Tải model ASR
5. Hướng dẫn cấu hình server

Sau khi hoàn tất, làm tiếp theo các bước [4. Chạy chương trình](#4-chay-chuong-trinh) và [5. Khởi động lại xiaozhi-esp32-server](#5-khoi-dong-lai-xiaozhi-esp32-server).

### 1.2 Triển khai thủ công

#### 1.2.1 Tạo thư mục

Tạo thư mục `xiaozhi-server`, rồi tạo tiếp `data`, `models/SenseVoiceSmall`.

```
xiaozhi-server
  ├─ data
  ├─ models
     ├─ SenseVoiceSmall
```

#### 1.2.2 Tải model nhận dạng giọng nói

Tải `SenseVoiceSmall` và đặt `model.pt` vào `models/SenseVoiceSmall`.

- ModelScope: [SenseVoiceSmall](https://modelscope.cn/models/iic/SenseVoiceSmall/resolve/master/model.pt)
- Baidu Netdisk: [SenseVoiceSmall](https://pan.baidu.com/share/init?surl=QlgM58FHhYv1tFnUT_A8Sg&pwd=qvna), mã `qvna`

#### 1.2.3 Tải file cấu hình

Cần 2 file: `docker-compose_all.yaml` và `config_from_api.yaml`.

##### 1.2.3.1 Tải `docker-compose_all.yaml`

Mở [link này](../main/xiaozhi-server/docker-compose_all.yml), tải file rồi đặt vào `xiaozhi-server`.

Hoặc dùng:

```bash
wget https://raw.githubusercontent.com/xinnan-tech/xiaozhi-esp32-server/refs/heads/main/main/xiaozhi-server/docker-compose_all.yml
```

##### 1.2.3.2 Tải `config_from_api.yaml`

Mở [link này](../main/xiaozhi-server/config_from_api.yaml), tải file rồi đổi tên thành `.config.yaml` và đặt trong `data`.

Hoặc:

```bash
wget https://raw.githubusercontent.com/xinnan-tech/xiaozhi-esp32-server/refs/heads/main/main/xiaozhi-server/config_from_api.yaml
```

Cấu trúc file mong đợi:

```
xiaozhi-server
  ├─ docker-compose_all.yml
  ├─ data
    ├─ .config.yaml
  ├─ models
     ├─ SenseVoiceSmall
       ├─ model.pt
```

## 2. Sao lưu dữ liệu

Nếu trước đây bạn đã chạy xong hệ thống và có key cấu hình quan trọng, hãy sao lưu chúng trước vì quá trình nâng cấp có thể ghi đè dữ liệu cũ.

## 3. Xóa image và container cũ

Chạy:

```bash
docker compose -f docker-compose_all.yml down

docker stop xiaozhi-esp32-server
docker rm xiaozhi-esp32-server

docker stop xiaozhi-esp32-server-web
docker rm xiaozhi-esp32-server-web

docker stop xiaozhi-esp32-server-db
docker rm xiaozhi-esp32-server-db

docker stop xiaozhi-esp32-server-redis
docker rm xiaozhi-esp32-server-redis

docker rmi ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:server_latest
docker rmi ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:web_latest
```

## 4. Chạy chương trình

```bash
docker compose -f docker-compose_all.yml up -d
docker logs -f xiaozhi-esp32-server-web
```

Khi log hiện như sau, nghĩa là `智控台` đã chạy thành công:

```text
2025-xx-xx 22:11:12.445 [main] INFO  c.a.d.s.b.a.DruidDataSourceAutoConfigure - Init DruidDataSource
2025-xx-xx 21:28:53.873 [main] INFO  xiaozhi.AdminApplication - Started AdminApplication in 16.057 seconds (process running for 17.941)
http://localhost:8002/xiaozhi/doc.html
```

Lúc này chỉ `智控台` chạy được. Nếu service 8000 của `xiaozhi-esp32-server` chưa ổn thì tạm chưa cần xử lý.

Mở trình duyệt tại `http://127.0.0.1:8002`, đăng ký người dùng đầu tiên. Người đầu tiên là siêu quản trị viên, các user sau là user thường.

Cần làm 3 việc quan trọng:

### Việc quan trọng 1

Đăng nhập bằng siêu quản trị viên, vào `参数管理`, tìm `server.secret`, copy giá trị đó vào `.config.yaml`:

```yaml
manager-api:
  url:  http://127.0.0.1:8002/xiaozhi
  secret: giá_trị_server.secret_của_bạn
```

Vì chạy Docker nên `url` phải đổi thành:

```yaml
manager-api:
  url: http://xiaozhi-esp32-server-web:8002/xiaozhi
  secret: 12345678-xxxx-xxxx-xxxx-123456789000
```

### Việc quan trọng 2

Đăng nhập `智控台` bằng siêu quản trị viên, vào `模型配置` > `大语言模型`, chọn dòng `智谱AI`, bấm `修改`, rồi nhập `API密钥`.

## 5. Khởi động lại xiaozhi-esp32-server

Chạy:

```bash
docker restart xiaozhi-esp32-server
docker logs -f xiaozhi-esp32-server
```

Nếu thấy log như sau thì Server đã chạy:

```text
25-02-23 12:01:09[core.websocket_server] - INFO - Websocket地址是      ws://xxx.xx.xx.xx:8000/xiaozhi/v1/
25-02-23 12:01:09[core.websocket_server] - INFO - =======上面的地址是websocket协议地址，请勿用浏览器访问=======
25-02-23 12:01:09[core.websocket_server] - INFO - 如想测试websocket请用谷歌浏览器打开test目录下的test_page.html
25-02-23 12:01:09[core.websocket_server] - INFO - =======================================================
```

Vì đây là triển khai full module nên có 2 địa chỉ quan trọng cần ghi vào ESP32:

- OTA: `http://ip-lan-cua-may-chu:8002/xiaozhi/ota/`
- Websocket: `ws://ip-lan-cua-may-chu:8000/xiaozhi/v1/`

### Việc quan trọng 3

Trong `参数管理`, nhập:

- `server.websocket` = Websocket ở trên
- `server.ota` = OTA ở trên

Sau đó bạn có thể tiếp tục:

1. [Biên dịch firmware ESP32 của riêng bạn](firmware-build.md)
2. [Cấu hình firmware do Xiaoge build sẵn để dùng server tùy chỉnh](firmware-setting.md)

# Cách 2: Chạy full module từ mã nguồn local

## 1. Cài MySQL

Nếu đã có MySQL, tạo database `xiaozhi_esp32_server`:

```sql
CREATE DATABASE xiaozhi_esp32_server CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Nếu chưa có, có thể dùng Docker:

```bash
docker run --name xiaozhi-esp32-server-db -e MYSQL_ROOT_PASSWORD=123456 -p 3306:3306 -e MYSQL_DATABASE=xiaozhi_esp32_server -e MYSQL_INITDB_ARGS="--character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci" -e TZ=Asia/Shanghai -d mysql:latest
```

## 2. Cài Redis

```bash
docker run --name xiaozhi-esp32-server-redis -d -p 6379:6379 redis
```

## 3. Chạy manager-api

1. Cài JDK 21 và Maven.
2. Mở project `manager-api` bằng VS Code.
3. Cấu hình `src/main/resources/application-dev.yml`:

```yaml
spring:
  datasource:
    username: root
    password: 123456
```

Redis:

```yaml
spring:
  data:
    redis:
      host: localhost
      port: 6379
      password:
      database: 0
```

4. Chạy `src/main/java/xiaozhi/AdminApplication.java`.

## 4. Chạy manager-web

1. Cài Node.js.
2. Mở `manager-web` bằng VS Code.
3. Chạy:

```bash
npm install
npm run serve
```

Nếu API không ở `http://localhost:8002`, hãy sửa `main/manager-web/.env.development`.

Sau khi chạy thành công, mở `http://127.0.0.1:8001` để đăng ký user đầu tiên và cấu hình model `智谱AI`.

## 5. Cài Python

Làm giống phần cài môi trường ở trên bằng `conda`, `libopus`, `ffmpeg`.

## 6. Cài dependency dự án

```bash
conda activate xiaozhi-esp32-server
cd main/xiaozhi-server
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
pip install -r requirements.txt
```

## 7. Tải model ASR

Tải `SenseVoiceSmall` và đặt vào `models/SenseVoiceSmall/model.pt`.

## 8. Cấu hình dự án

Lấy `server.secret` trong `智控台`, sau đó tạo `data/.config.yaml`:

```yaml
manager-api:
  url: http://127.0.0.1:8002/xiaozhi
  secret: 12345678-xxxx-xxxx-xxxx-123456789000
```

## 9. Chạy dự án

```bash
conda activate xiaozhi-esp32-server
python app.py
```

Khi log hiện `Websocket地址` thì Server đã chạy.

## 10. Địa chỉ OTA và Websocket

- OTA: `http://ip-lan-cua-may-tinh:8002/xiaozhi/ota/`
- Websocket: `ws://ip-lan-cua-may-tinh:8000/xiaozhi/v1/`

Ghi 2 địa chỉ này vào `智控台`:

- `server.websocket`
- `server.ota`

## Câu hỏi thường gặp

1. [Vì sao tôi nói tiếng Trung/Anh/Nhật bị nhận sai?](./FAQ.md)
2. [Vì sao TTS lỗi file không tồn tại?](./FAQ.md)
3. [TTS hay lỗi hoặc timeout](./FAQ.md)
4. [Wi-Fi kết nối được nhưng 4G thì không](./FAQ.md)
5. [Làm sao tăng tốc phản hồi?](./FAQ.md)
6. [Tôi nói chậm, Xiaozhi hay cướp lời](./FAQ.md)
7. [Làm sao điều khiển đèn, điều hòa, bật/tắt từ xa?](./FAQ.md)
