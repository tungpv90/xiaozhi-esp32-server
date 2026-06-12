# Hướng dẫn bật nhận diện giọng nói

Tài liệu gồm 3 phần:

- Cách triển khai dịch vụ nhận diện giọng nói
- Cách cấu hình khi chạy full module
- Cách cấu hình khi chạy tối giản

## 1. Triển khai dịch vụ

### Bước 1: Tải mã nguồn

Mở:
https://github.com/xinnan-tech/voiceprint-api

Tải ZIP rồi đổi tên thành `voiceprint-api`.

### Bước 2: Tạo database

`voiceprint` cần MySQL. Nếu đã có `智控台`, có thể dùng chung.

Kiểm tra:

```bash
telnet 127.0.0.1 3306
```

Nếu `mysql` chạy bằng Docker, hãy đổi `expose` thành `ports` trong `docker-compose_all.yml`.

Tạo DB và bảng:

```sql
CREATE DATABASE voiceprint_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE voiceprint_db;

CREATE TABLE voiceprints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    speaker_id VARCHAR(255) NOT NULL UNIQUE,
    feature_vector LONGBLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_speaker_id (speaker_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Bước 3: Cấu hình DB

Copy `voiceprint.yaml` vào `data/.voiceprint.yaml`.

```yaml
mysql:
  host: "127.0.0.1"
  port: 3306
  user: "root"
  password: "your_password"
  database: "voiceprint_db"
```

Nếu chạy Docker, `host` phải là IP LAN của máy chạy MySQL.

### Bước 4: Chạy

```bash
cd voiceprint-api
docker compose -f docker-compose.yml down
docker stop voiceprint-api
docker rm voiceprint-api
docker rmi ghcr.nju.edu.cn/xinnan-tech/voiceprint-api:latest
docker compose -f docker-compose.yml up -d
docker logs -f voiceprint-api
```

Khi log có dạng:

```text
声纹接口地址: http://127.0.0.1:8005/voiceprint/health?key=abcd
```

hãy đổi sang IP LAN thật của máy bạn.

## 2. Full module

### Bước 1: Bật tính năng

Trong `智控台`, vào `参数字典` -> `系统功能配置`, bật `声纹识别`.

### Bước 2: Cấu hình endpoint

Trong `参数管理`, tìm `server.voice_print` rồi dán địa chỉ voiceprint.

### Bước 3: Chọn memory mode

Trong agent, đặt memory thành `本地短期记忆` và bật `上报文字+语音`.

### Bước 4: Thêm voiceprint

Vào `智能体管理`, bấm nút `声纹识别`, rồi thêm voiceprint cho người dùng.

## 3. Triển khai tối giản

Trong `xiaozhi-server/data/.config.yaml`, thêm:

```yaml
voiceprint:
  url: your_voiceprint_url
  speakers:
    - "test1,张三,张三是一个程序员"
    - "test2,李四,李四是一个产品经理"
    - "test3,王五,王五是一个设计师"
```

### Đăng ký voiceprint

API register:

```text
POST http://localhost:8005/voiceprint/register
```

Header cần Bearer token từ `?key=...`.

Ví dụ:

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "speaker_id=your_speaker_id_here" \
  -F "file=@/path/to/your/file" \
  http://localhost:8005/voiceprint/register
```

`speaker_id` phải khớp với cấu hình trong `.config.yaml`.
