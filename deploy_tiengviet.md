# Hướng dẫn Deploy xiaozhi-esp32-server lên Ubuntu (Không Docker, CI/CD)

> **Môi trường:** Ubuntu, Nginx đã cài sẵn, account: `minica_deployer`, thư mục: `/home/xiaozhi`

---

## Tổng quan kiến trúc

```
GitHub Push → GitHub Actions
    ├── Build Java JAR   (manager-api)   → xiaozhi-esp32-api.jar
    ├── Build Vue dist   (manager-web)   → dist/
    └── Deploy lên server qua SSH

Server Ubuntu:
    ├── MySQL 8.0          port 3306
    ├── Redis              port 6379
    ├── Nginx              port 80       (static files + reverse proxy)
    ├── xiaozhi-api        port 8002     (Java Spring Boot)
    ├── xiaozhi-server     port 8000     (Python WebSocket)
    └── xiaozhi-server     port 8003     (Python HTTP: OTA + Vision)
```

### Thứ tự khởi động bắt buộc (lần đầu)

```
MySQL + Redis
    ↓
xiaozhi-api (Java)       ← start trước
    ↓
Vào Web UI → đăng ký admin → lấy server.secret
    ↓
Điền secret vào data/.config.yaml
    ↓
xiaozhi-server (Python)  ← start sau
```

> **Tại sao?** Khi `xiaozhi-server` khởi động, nó đọc `data/.config.yaml`. Nếu thấy `manager-api.url` thì ngay lập tức gọi API để lấy cấu hình (LLM, TTS, v.v.). Nếu `secret` sai hoặc `xiaozhi-api` chưa chạy → Python server crash.

---

## PHẦN 1: CHUẨN BỊ SERVER

### Bước 1: Cài các gói hệ thống

```bash
sudo apt update && sudo apt upgrade -y

sudo apt install -y git curl wget unzip build-essential \
  libssl-dev libffi-dev \
  ffmpeg libopus-dev libopus0 \
  libsndfile1 sox
```

> `ffmpeg` và `libopus` là **bắt buộc** — `app.py` kiểm tra `ffmpeg` ngay khi khởi động, thiếu là crash.

Kiểm tra sau khi cài:

```bash
# ffmpeg
ffmpeg -version | head -1
# ffmpeg version 4.x...

# libopus
ldconfig -p | grep opus
# libopus.so.0 => ...
```

### Bước 2: Cài Python 3.10

```bash
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt install -y python3.10 python3.10-venv python3.10-dev python3-pip

python3.10 --version
# Python 3.10.x
```

### Bước 3: Cài Java 21

```bash
wget -O - https://packages.adoptium.net/artifactory/api/gpg/key/public \
  | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/adoptium.gpg

echo "deb https://packages.adoptium.net/artifactory/deb $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/adoptium.list

sudo apt update && sudo apt install -y temurin-21-jdk

java -version
# openjdk 21...
```

### Bước 4: Cài Node.js 20

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

node --version   # v20.x
npm --version
```

### Bước 5: Cài Maven

```bash
sudo apt install -y maven
mvn -version
# Apache Maven 3.x
```

### Bước 6: Cài MySQL 8.0

```bash
sudo apt install -y mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql

sudo mysql_secure_installation
# Validate password component? → No
# Remove anonymous users?      → Yes
# Disallow root login remotely? → Yes
# Remove test database?         → Yes
# Reload privilege tables?      → Yes

# Tạo database và user
sudo mysql -u root -p << 'EOF'
CREATE DATABASE xiaozhi_esp32_server
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER 'xiaozhi'@'localhost' IDENTIFIED BY 'StrongPass123!';
GRANT ALL PRIVILEGES ON xiaozhi_esp32_server.* TO 'xiaozhi'@'localhost';
FLUSH PRIVILEGES;
EOF

# Kiểm tra user đã được tạo chưa
sudo mysql -u root -p -e "SELECT user, host FROM mysql.user WHERE user='xiaozhi';"

# Test kết nối thử — phải trả về 1
mysql -u xiaozhi -p'StrongPass123!' xiaozhi_esp32_server -e "SELECT 1;"
```

> **Quan trọng:** Nếu bước test kết nối báo `Access denied` → xoá và tạo lại user:
> ```bash
> sudo mysql -u root -p -e "DROP USER IF EXISTS 'xiaozhi'@'localhost'; CREATE USER 'xiaozhi'@'localhost' IDENTIFIED BY 'StrongPass123!'; GRANT ALL PRIVILEGES ON xiaozhi_esp32_server.* TO 'xiaozhi'@'localhost'; FLUSH PRIVILEGES;"
> ```

### Bước 7: Cài Redis

```bash
sudo apt install -y redis-server

# Sửa supervised no → supervised systemd
sudo sed -i 's/^supervised no/supervised systemd/' /etc/redis/redis.conf

sudo systemctl restart redis-server
sudo systemctl enable redis-server

redis-cli ping
# PONG
```

---

## PHẦN 2: LẤY CODE VÀ BUILD LẦN ĐẦU

### Bước 8: Clone repository

```bash
cd /home/xiaozhi
git clone https://github.com/<YOUR_USERNAME>/xiaozhi-esp32-server.git app
# Thay <YOUR_USERNAME> bằng username GitHub của bạn (fork từ xinnan-tech)
```

### Bước 9: Cài Python dependencies

```bash
cd /home/xiaozhi/app/main/xiaozhi-server

python3.10 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
# torch (~2GB) mất 10–20 phút tuỳ mạng
```

### Bước 10: Tải model ASR — SenseVoice (~600MB)

```bash
cd /home/xiaozhi/app/main/xiaozhi-server
source venv/bin/activate

mkdir -p models/SenseVoiceSmall

python3 -c "
from modelscope import snapshot_download
snapshot_download('iic/SenseVoiceSmall', local_dir='models/SenseVoiceSmall')
"
```

> Làm **một lần duy nhất**. Thư mục `models/` bị exclude khỏi rsync trong CI/CD, không bao giờ bị ghi đè.

### Bước 11: Cấu hình Python service (chưa điền secret)

Dự án có 2 file config:
- `config.yaml` — config mặc định đầy đủ, **không có** `manager-api:`
- `config_from_api.yaml` — template dành cho chế độ kết nối manager-api, **có** `manager-api:`

Vì ta dùng manager-api, copy từ `config_from_api.yaml`:

```bash
cd /home/xiaozhi/app/main/xiaozhi-server
mkdir -p data tmp

cp config_from_api.yaml data/.config.yaml
nano data/.config.yaml
```

Sửa các dòng sau:

```yaml
server:
  ip: 0.0.0.0
  port: 8000
  http_port: 8003
  # Thay bằng IP thật hoặc domain của server
  vision_explain: http://<IP_SERVER>/mcp/vision/explain

manager-api:
  url: http://127.0.0.1:8002/xiaozhi
  secret: "CHUA_DIEN_LAY_O_BUOC_16"   # ← để tạm, cập nhật sau

prompt_template: agent-base-prompt.txt
```

> **Cơ chế hoạt động:** `app.py` load `data/.config.yaml` trước. Mục nào không có → lấy từ `config.yaml` bù vào. Khi thấy `manager-api.url` → gọi API lấy toàn bộ cấu hình LLM/TTS/ASR từ manager-api thay vì đọc local.

> **Chưa start Python server.** Phải hoàn thành bước 16 trước.

### Bước 12: Tạo config Java (production profile)

```bash
cat > /home/xiaozhi/app/main/manager-api/src/main/resources/application-prod.yml << 'EOF'
spring:
  datasource:
    druid:
      driver-class-name: com.mysql.cj.jdbc.Driver
      url: jdbc:mysql://127.0.0.1:3306/xiaozhi_esp32_server?useUnicode=true&characterEncoding=UTF-8&serverTimezone=Asia/Ho_Chi_Minh&nullCatalogMeansCurrent=true
      username: xiaozhi
      password: StrongPass123!
      initial-size: 10
      max-active: 100
      min-idle: 10
      max-wait: 6000
  data:
    redis:
      host: 127.0.0.1
      port: 6379
      database: 0
      timeout: 10000ms
      lettuce:
        pool:
          max-active: 8
          max-idle: 8
          min-idle: 0

server:
  port: 8002
EOF
```

### Bước 13: Build Java lần đầu

```bash
cd /home/xiaozhi/app/main/manager-api
mvn clean package -DskipTests -q

ls target/
# xiaozhi-esp32-api.jar  ← tên JAR chính xác
```

### Bước 14: Build Web lần đầu

```bash
cd /home/xiaozhi/app/main/manager-web
npm install --legacy-peer-deps
npm run build

ls dist/
# index.html, js/, css/, ...
```

---

## PHẦN 3: SYSTEMD SERVICES

### Bước 15: Tạo service cho Java API

```bash
sudo nano /etc/systemd/system/xiaozhi-api.service
```

```ini
[Unit]
Description=XiaoZhi Manager API (Spring Boot)
After=network.target mysql.service redis-server.service
Wants=mysql.service redis-server.service

[Service]
Type=simple
User=minica_deployer
Group=minica_deployer
WorkingDirectory=/home/xiaozhi/app/main/manager-api
ExecStart=/usr/bin/java \
  -Xms256m -Xmx512m \
  -Dspring.profiles.active=prod \
  -jar /home/xiaozhi/app/main/manager-api/target/xiaozhi-esp32-api.jar
Restart=always
RestartSec=15
StandardOutput=journal
StandardError=journal
SyslogIdentifier=xiaozhi-api
SuccessExitStatus=143

[Install]
WantedBy=multi-user.target
```

### Bước 16: Tạo service cho Python server

```bash
sudo nano /etc/systemd/system/xiaozhi-server.service
```

```ini
[Unit]
Description=XiaoZhi ESP32 Python Server
After=network.target mysql.service redis-server.service xiaozhi-api.service
Wants=mysql.service redis-server.service

[Service]
Type=simple
User=minica_deployer
Group=minica_deployer
WorkingDirectory=/home/xiaozhi/app/main/xiaozhi-server
Environment="PATH=/home/xiaozhi/app/main/xiaozhi-server/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/xiaozhi/app/main/xiaozhi-server/venv/bin/python app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=xiaozhi-server

[Install]
WantedBy=multi-user.target
```

---

## PHẦN 4: CẤU HÌNH NGINX

### Bước 17: Tạo Nginx config

```bash
sudo nano /etc/nginx/sites-available/xiaozhi
```

```nginx
server {
    listen 80;
    server_name _;  # Thay bằng domain nếu có

    # Web Admin UI — Vue.js static files
    location / {
        root /home/xiaozhi/app/main/manager-web/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    # WebSocket — Python AI server
    # Phải đặt TRƯỚC /xiaozhi/ vì Nginx khớp prefix dài nhất
    location /xiaozhi/v1 {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade    $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host       $host;
        proxy_set_header X-Real-IP  $remote_addr;
        proxy_read_timeout  3600s;
        proxy_send_timeout  3600s;
    }

    # REST API — Java Spring Boot
    location /xiaozhi/ {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host             $host;
        proxy_set_header X-Real-IP        $remote_addr;
        proxy_set_header X-Forwarded-For  $proxy_add_x_forwarded_for;
        proxy_connect_timeout 30s;
        proxy_read_timeout    60s;
    }

    # OTA + Vision HTTP API — Python
    location /mcp/ {
        proxy_pass http://127.0.0.1:8003;
        proxy_set_header Host      $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/xiaozhi /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

sudo nginx -t
sudo systemctl reload nginx
```

---

## PHẦN 5: KHỞI ĐỘNG LẦN ĐẦU VÀ LẤY server.secret

### Bước 18: Start xiaozhi-api (Java) trước

```bash
sudo systemctl daemon-reload
sudo systemctl enable xiaozhi-api xiaozhi-server

# Chỉ start Java API — CHƯA start Python
sudo systemctl start xiaozhi-api

# Theo dõi log, đợi xuất hiện "Started XiaozhiApplication"
sudo journalctl -u xiaozhi-api -f
# Ctrl+C để thoát
```

### Bước 19: Đăng ký tài khoản admin và lấy server.secret

**1. Mở trình duyệt** truy cập `http://<IP_SERVER>` (qua Nginx)

**2. Đăng ký tài khoản** — tài khoản đầu tiên đăng ký tự động trở thành **admin**

**3. Vào menu:** `Quản lý hệ thống` → `Quản lý tham số`

**4. Tìm tham số** tên **`server.secret`** → copy toàn bộ giá trị (chuỗi UUID)

**5. Cập nhật `data/.config.yaml`:**

```bash
nano /home/xiaozhi/app/main/xiaozhi-server/data/.config.yaml
```

```yaml
manager-api:
  url: http://127.0.0.1:8002/xiaozhi
  secret: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"  # ← dán UUID vừa copy
```

### Bước 20: Start xiaozhi-server (Python)

```bash
sudo systemctl start xiaozhi-server

# Theo dõi log
sudo journalctl -u xiaozhi-server -f
```

Thành công khi thấy các dòng sau (mất khoảng 20–30 giây để load model ASR):

```
从API读取配置
初始化组件: vad成功 VAD_SileroVAD
ASR模块初始化完成
初始化组件: asr成功 ASR_FunASR
视觉分析接口是   http://x.x.x.x:8003/mcp/vision/explain
Websocket地址是  ws://x.x.x.x:8000/xiaozhi/v1/
```

> **Nếu thấy lỗi `secret配置错误` hoặc `请先配置manager-api的secret`:** Secret chưa đúng hoặc vẫn còn chữ placeholder → kiểm tra lại bước 19.

---

## PHẦN 6: CI/CD VỚI GITHUB ACTIONS

### Bước 21: Tạo SSH deploy key

```bash

# Chạy trên server, bằng account minica_deployer
su - minica_deployer
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/deploy_key -N ""

cat ~/.ssh/deploy_key.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Copy nội dung này để thêm vào GitHub Secrets
cat ~/.ssh/deploy_key
```

### Bước 22: Cấp quyền sudo không cần password

```bash
sudo visudo
```

Thêm vào cuối file:

```
minica_deployer ALL=(ALL) NOPASSWD: \
  /bin/systemctl restart xiaozhi-api, \
  /bin/systemctl restart xiaozhi-server, \
  /bin/systemctl reload nginx, \
  /bin/systemctl is-active xiaozhi-api, \
  /bin/systemctl is-active xiaozhi-server
```

### Bước 23: Thêm GitHub Secrets

Vào GitHub repo → **Settings** → **Secrets and variables** → **Actions**:

| Secret | Giá trị |
|---|---|
| `DEPLOY_HOST` | IP hoặc domain server Ubuntu |
| `DEPLOY_USER` | `minica_deployer` |
| `DEPLOY_SSH_KEY` | Nội dung file `~/.ssh/deploy_key` (private key) |
| `DEPLOY_PATH` | `/home/xiaozhi/app` |

### Bước 24: Tạo workflow file

Tạo file `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Ubuntu

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:

  # ── Job 1: Build Java JAR ─────────────────────────────────────
  build-api:
    name: Build Java API
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'
          cache: maven

      - name: Build JAR
        run: |
          cd main/manager-api
          mvn clean package -DskipTests -q

      - uses: actions/upload-artifact@v4
        with:
          name: api-jar
          path: main/manager-api/target/xiaozhi-esp32-api.jar
          retention-days: 1

  # ── Job 2: Build Vue dist ─────────────────────────────────────
  build-web:
    name: Build Vue Web
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: main/manager-web/package-lock.json

      - name: Build
        run: |
          cd main/manager-web
          npm install --legacy-peer-deps
          npm run build

      - uses: actions/upload-artifact@v4
        with:
          name: web-dist
          path: main/manager-web/dist/
          retention-days: 1

  # ── Job 3: Deploy lên server ──────────────────────────────────
  deploy:
    name: Deploy
    runs-on: ubuntu-latest
    needs: [ build-api, build-web ]
    steps:
      - uses: actions/checkout@v4

      - uses: actions/download-artifact@v4
        with:
          name: api-jar
          path: artifacts/api/

      - uses: actions/download-artifact@v4
        with:
          name: web-dist
          path: artifacts/web/

      - uses: webfactory/ssh-agent@v0.9.0
        with:
          ssh-private-key: ${{ secrets.DEPLOY_SSH_KEY }}

      - name: Add known_hosts
        run: ssh-keyscan -H ${{ secrets.DEPLOY_HOST }} >> ~/.ssh/known_hosts

      - name: Upload JAR
        run: |
          scp artifacts/api/xiaozhi-esp32-api.jar \
            ${{ secrets.DEPLOY_USER }}@${{ secrets.DEPLOY_HOST }}:${{ secrets.DEPLOY_PATH }}/main/manager-api/target/xiaozhi-esp32-api.jar

      - name: Upload web dist
        run: |
          rsync -az --delete artifacts/web/ \
            ${{ secrets.DEPLOY_USER }}@${{ secrets.DEPLOY_HOST }}:${{ secrets.DEPLOY_PATH }}/main/manager-web/dist/

      - name: Sync Python source
        run: |
          rsync -az --delete \
            --exclude='venv/' \
            --exclude='data/' \
            --exclude='models/' \
            --exclude='tmp/' \
            --exclude='__pycache__/' \
            --exclude='*.pyc' \
            main/xiaozhi-server/ \
            ${{ secrets.DEPLOY_USER }}@${{ secrets.DEPLOY_HOST }}:${{ secrets.DEPLOY_PATH }}/main/xiaozhi-server/

      - name: Restart services
        env:
          DEPLOY_PATH: ${{ secrets.DEPLOY_PATH }}
        run: |
          ssh ${{ secrets.DEPLOY_USER }}@${{ secrets.DEPLOY_HOST }} bash << EOF
            set -e

            echo "=== Cập nhật Python deps ==="
            cd "$DEPLOY_PATH/main/xiaozhi-server"
            source venv/bin/activate
            pip install -r requirements.txt -q

            echo "=== Restart xiaozhi-api ==="
            sudo systemctl restart xiaozhi-api
            sleep 10
            sudo systemctl is-active xiaozhi-api || { echo "FAILED: xiaozhi-api"; exit 1; }

            echo "=== Restart xiaozhi-server ==="
            sudo systemctl restart xiaozhi-server
            sleep 5
            sudo systemctl is-active xiaozhi-server || { echo "FAILED: xiaozhi-server"; exit 1; }

            echo "=== Reload nginx ==="
            sudo systemctl reload nginx

            echo "=== Deploy OK ==="
          EOF

      - name: Health check
        run: |
          sleep 10
          CODE=$(curl -s -o /dev/null -w "%{http_code}" \
            http://${{ secrets.DEPLOY_HOST }}/xiaozhi/sys/version)
          echo "HTTP $CODE"
          [ "$CODE" = "200" ] && echo "OK" || echo "WARNING: check logs"
```

---

## PHẦN 7: KIỂM TRA SAU DEPLOY

### Trạng thái services

```bash
sudo systemctl status xiaozhi-api xiaozhi-server nginx mysql redis-server
```

### Ports đang lắng nghe

```bash
ss -tlnp | grep -E '80 |8000|8002|8003|3306|6379'
```

Kết quả mong đợi:

```
0.0.0.0:80      → nginx
0.0.0.0:8000    → xiaozhi-server (WebSocket)
0.0.0.0:8002    → xiaozhi-api (Java)
0.0.0.0:8003    → xiaozhi-server (HTTP: OTA + Vision)
127.0.0.1:3306  → MySQL
127.0.0.1:6379  → Redis
```

### Test nhanh

```bash
# API Java
curl http://localhost/xiaozhi/sys/version

# WebSocket (cần wscat)
npm install -g wscat
wscat -c ws://localhost/xiaozhi/v1/
```

### Xem logs

```bash
sudo journalctl -u xiaozhi-api    -f   # Java
sudo journalctl -u xiaozhi-server -f   # Python
sudo tail -f /var/log/nginx/error.log
```

---

## PHẦN 8: LOGROTATE

```bash
sudo nano /etc/logrotate.d/xiaozhi
```

```
/home/xiaozhi/app/main/xiaozhi-server/tmp/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 minica_deployer minica_deployer
}
```

---

## PHẦN 9: CẬP NHẬT SOURCE CODE QUA CI/CD

### Quy trình chuẩn — chỉ cần push code

Sau khi đã setup CI/CD xong, mọi thay đổi đều deploy tự động:

```bash
# Trên máy local của bạn
git add .
git commit -m "mô tả thay đổi"
git push origin main
```

GitHub Actions tự động chạy, không cần làm gì thêm trên server.

---

### Theo dõi tiến trình deploy

Vào GitHub repo → tab **Actions** → chọn workflow đang chạy để xem log realtime.

Hoặc xem log trên server ngay sau khi push:

```bash
# Xem log Java API sau khi restart
sudo journalctl -u xiaozhi-api -f

# Xem log Python server sau khi restart
sudo journalctl -u xiaozhi-server -f
```

---

### Các trường hợp thay đổi code

#### Chỉ sửa Python (xiaozhi-server)

CI/CD vẫn build cả Java + Vue (mất ~3–5 phút), nhưng chỉ có Python source được rsync và restart `xiaozhi-server`.

Nếu muốn deploy Python nhanh hơn **thủ công** trên server:

```bash
cd /home/xiaozhi/app
git pull origin main

sudo systemctl restart xiaozhi-server
sudo journalctl -u xiaozhi-server -f
```

#### Chỉ sửa Java (manager-api)

CI/CD build lại JAR và restart `xiaozhi-api`. Thủ công trên server:

```bash
cd /home/xiaozhi/app
git pull origin main

cd main/manager-api
mvn clean package -DskipTests -q

sudo systemctl restart xiaozhi-api
sudo journalctl -u xiaozhi-api -f
```

#### Chỉ sửa Vue (manager-web)

CI/CD build lại `dist/` và rsync lên server, reload nginx. Thủ công:

```bash
cd /home/xiaozhi/app
git pull origin main

cd main/manager-web
npm install --legacy-peer-deps
npm run build

sudo systemctl reload nginx
```

---

### Trigger deploy thủ công (không cần push code)

Vào GitHub repo → tab **Actions** → chọn workflow **Deploy to Ubuntu** → nút **Run workflow** → **Run workflow**.

Dùng khi: server bị restart, muốn redeploy lại phiên bản hiện tại mà không thay đổi code.

---

### Kiểm tra deploy thành công

```bash
# Xem thời gian restart gần nhất
sudo systemctl status xiaozhi-api   | grep "Active:"
sudo systemctl status xiaozhi-server | grep "Active:"

# Xem version đang chạy
curl -s http://localhost/xiaozhi/sys/version | python3 -m json.tool
```

---

### Rollback khi deploy lỗi

Nếu deploy mới làm hỏng service, rollback về commit trước:

```bash
cd /home/xiaozhi/app

# Xem danh sách commit
git log --oneline -10

# Quay về commit cụ thể
git checkout <COMMIT_HASH> -- main/xiaozhi-server/
# hoặc reset toàn bộ
git reset --hard <COMMIT_HASH>

# Build lại Java nếu cần
cd main/manager-api
mvn clean package -DskipTests -q

# Restart services
sudo systemctl restart xiaozhi-api
sudo systemctl restart xiaozhi-server
```

---

## TỔNG KẾT

### Lần đầu (thủ công)

```
Bước 1–7   : Cài hệ thống (Python, Java, Node, MySQL, Redis)
Bước 8–11  : Clone code, venv, tải model, cấu hình Python (chưa có secret)
Bước 12–14 : Tạo config Java, build JAR, build Vue
Bước 15–16 : Tạo 2 systemd service files
Bước 17    : Cấu hình Nginx
Bước 18    : Start xiaozhi-api
Bước 19    : Vào Web UI → lấy server.secret → điền vào data/.config.yaml
Bước 20    : Start xiaozhi-server
Bước 21–24 : Setup CI/CD (SSH key, secrets, workflow file)
             → Push → GitHub Actions tự chạy lần đầu
```

### Từ lần 2 (tự động qua CI/CD)

```
git push origin main
    ↓
Job 1 + Job 2 chạy song song (~3–5 phút có cache)
    ├── mvn clean package → xiaozhi-esp32-api.jar
    └── npm run build     → dist/
    ↓
Job 3 deploy lên server:
    ├── scp JAR
    ├── rsync dist/
    ├── rsync Python source (bỏ qua: venv/ data/ models/ tmp/)
    ├── pip install -r requirements.txt
    ├── systemctl restart xiaozhi-api  (đợi 10s)
    ├── systemctl restart xiaozhi-server (đợi 5s)
    ├── systemctl reload nginx
    └── curl health check
```

---

## XỬ LÝ SỰ CỐ

| Lỗi | Nguyên nhân | Cách xử lý |
|---|---|---|
| `xiaozhi-server` crash: `secret配置错误` | Secret chưa điền hoặc sai | Bước 19: lấy lại từ Web UI, cập nhật `data/.config.yaml`, restart |
| `xiaozhi-server` crash: `请先配置...secret` | Secret vẫn là placeholder | Tương tự trên |
| `xiaozhi-server` crash: `ffmpeg not found` | ffmpeg chưa cài | `sudo apt install -y ffmpeg` rồi restart |
| `xiaozhi-server` crash: `Could not find Opus library` | libopus chưa cài | `sudo apt install -y libopus0 libopus-dev` rồi restart |
| `xiaozhi-api` crash: `Access denied for user 'xiaozhi'@'localhost'` | MySQL user sai password hoặc chưa tạo | Tạo lại user: `sudo mysql -u root -p -e "DROP USER IF EXISTS 'xiaozhi'@'localhost'; CREATE USER 'xiaozhi'@'localhost' IDENTIFIED BY 'StrongPass123!'; GRANT ALL PRIVILEGES ON xiaozhi_esp32_server.* TO 'xiaozhi'@'localhost'; FLUSH PRIVILEGES;"` |
| `xiaozhi-api` không start (lỗi khác) | JAR sai tên hoặc config sai | Kiểm tra tên JAR (`xiaozhi-esp32-api.jar`), xem `journalctl -u xiaozhi-api -n 50` |
| Web UI hiện `正在连接服务器` | `xiaozhi-api` chưa chạy | `systemctl status xiaozhi-api` → xem log tìm nguyên nhân |
| Nginx 502 | Service chưa start | `systemctl status xiaozhi-api` / `xiaozhi-server` |
| WebSocket ngắt sau vài giây | Nginx timeout | Kiểm tra `proxy_read_timeout 3600s` trong nginx config |
| Liquibase fail | Credentials MySQL sai | Kiểm tra `application-prod.yml`, test: `mysql -u xiaozhi -p'StrongPass123!' xiaozhi_esp32_server -e "SELECT 1;"` |
| rsync: Permission denied | SSH key chưa đúng | Kiểm tra `~/.ssh/authorized_keys` trên server |
| `pip install` lỗi timeout | Torch quá lớn | Chạy thủ công: `pip install torch==2.2.2 --timeout 300` |

---

## LỆNH QUẢN LÝ HÀNG NGÀY

```bash
# Trạng thái
sudo systemctl status xiaozhi-api xiaozhi-server nginx

# Restart
sudo systemctl restart xiaozhi-api
sudo systemctl restart xiaozhi-server

# Log
sudo journalctl -u xiaozhi-api    -n 100 --no-pager
sudo journalctl -u xiaozhi-server -n 100 --no-pager
sudo journalctl -u xiaozhi-api    --since "1 hour ago"

# Nginx
sudo nginx -t && sudo systemctl reload nginx

# Dung lượng log Python
du -sh /home/xiaozhi/app/main/xiaozhi-server/tmp/
```
