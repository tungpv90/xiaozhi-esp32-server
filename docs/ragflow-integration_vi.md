# Hướng dẫn tích hợp ragflow

Tài liệu gồm 2 phần:

- Cách triển khai ragflow
- Cách cấu hình ragflow trong `智控台`

Nếu bạn đã quen với ragflow và đã triển khai rồi, có thể nhảy thẳng sang phần 2.

## Phần 1: Triển khai ragflow

### Bước 1: Kiểm tra MySQL và Redis

ragflow cần `mysql`. Nếu bạn đã cài `智控台`, thường sẽ có sẵn `mysql` để dùng chung.

Kiểm tra:

```bash
telnet 127.0.0.1 3306
telnet 127.0.0.1 6379
```

Nếu không mở được, cần chỉnh `docker-compose_all.yml` để đổi `expose` thành `ports` cho MySQL/Redis rồi restart.

### Bước 2: Tạo database và user

```sql
CREATE DATABASE IF NOT EXISTS rag_flow CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'rag_flow'@'%' IDENTIFIED BY 'infini_rag_flow';
GRANT ALL PRIVILEGES ON rag_flow.* TO 'rag_flow'@'%';
FLUSH PRIVILEGES;
```

### Bước 3: Tải ragflow

```bash
git clone https://ghfast.top/https://github.com/infiniflow/ragflow.git
cd ragflow
git checkout v0.22.0
cd docker
```

Sửa `docker-compose.yml` để bỏ `depends_on` của `ragflow-cpu` và `ragflow-gpu`.

Sửa `docker-compose-base.yml` để bỏ cấu hình `mysql` và `redis`.

### Bước 4: Sửa biến môi trường

Trong `.env`, sửa:

- `MYSQL_HOST`
- `MYSQL_PORT`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DBNAME`
- `REDIS_HOST`
- `REDIS_PORT`
- `REDIS_PASSWORD`

Lưu ý: nếu không có `MYSQL_USER`, hãy thêm vào.

Nếu Redis không có password, sửa `service_conf.yaml.template` để password rỗng.

### Bước 5: Chạy ragflow

```bash
docker-compose -f docker-compose.yml up -d
docker logs -n 20 -f docker-ragflow-cpu-1
```

### Bước 6: Đăng ký tài khoản

Mở `http://127.0.0.1:8008`, đăng ký, rồi đăng nhập.

Nếu muốn tắt đăng ký:

```dotenv
REGISTER_ENABLED=0
```

### Bước 7: Cấu hình model cho ragflow

Vào phần cài đặt của ragflow, thêm:

- LLM
- TEXT EMBEDDING

Rồi chọn model mặc định tương ứng.

## Phần 2: Cấu hình ragflow trong `智控台`

### Bước 1: Đăng nhập ragflow

Mở `http://127.0.0.1:8008`, vào `Sign In`.

Ở phần `API`, bấm `API Key` rồi tạo key mới và copy lại.

### Bước 2: Cấu hình vào `智控台`

Đảm bảo `智控台` version từ `0.8.7` trở lên.

1. Bật `知识库` trong `参数字典` -> `系统功能配置`
2. Vào `模型配置` -> `知识库`
3. Tìm `RAG_RAGFlow` và bấm `编辑`
4. Điền:
   - `服务地址`: `http://ip-lan-cua-ragflow:8008`
   - `API密钥`: key vừa copy
5. Lưu lại

### Bước 3: Tạo knowledge base

Vào `知识库` -> `新增`, đặt tên và mô tả, rồi upload tài liệu.

Sau đó:

- bấm `解析`
- xem chunk
- bấm `召回测试`

### Bước 4: Cho agent dùng ragflow

Vào `智能体` -> chọn agent -> `配置角色`.

Bấm `编辑功能`, chọn knowledge base muốn dùng rồi lưu.
