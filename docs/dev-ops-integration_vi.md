# Cách tự động cập nhật khi triển khai full module từ mã nguồn local

Tài liệu này dành cho những ai triển khai full module từ mã nguồn và muốn tự động kéo code, tự build, tự khởi động các cổng một cách định kỳ.

Môi trường test `https://2662r3426b.vicp.fun` đã dùng cách này từ đầu và hoạt động ổn định.

Có thể tham khảo video của Bilibili user `毕乐labs`: [《开源小智服务器xiaozhi-server自动更新以及最新版本MCP接入点配置保姆教程》](https://www.bilibili.com/video/BV15H37zHE7Q)

## Điều kiện ban đầu

- Máy chủ / máy bạn dùng Linux
- Bạn đã chạy thông suốt toàn bộ quy trình
- Bạn muốn theo kịp tính năng mới nhưng ngại deploy thủ công mỗi lần

## Kết quả đạt được

- Kéo được source mới ở môi trường trong nước
- Tự build frontend
- Tự build Java, dừng 8002 và khởi động lại 8002
- Tự kéo Python code, dừng 8000 và khởi động lại 8000

## Bước 1: Chọn thư mục dự án

Ví dụ:

```bash
/home/system/xiaozhi
```

## Bước 2: Clone dự án

```bash
cd /home/system/xiaozhi
git clone https://ghproxy.net/https://github.com/xinnan-tech/xiaozhi-esp32-server.git
```

Sau đó bạn sẽ có thư mục `xiaozhi-esp32-server`.

## Bước 3: Copy các file nền tảng

Nếu đã chạy qua toàn bộ quy trình trước đó, bạn sẽ quen với file `model.pt` và `.config.yaml`.

```bash
mkdir -p /home/system/xiaozhi/xiaozhi-esp32-server/main/xiaozhi-server/data/

cp đường_dẫn_.config.yaml_cũ /home/system/xiaozhi/xiaozhi-esp32-server/main/xiaozhi-server/data/.config.yaml
cp đường_dẫn_model.pt_cũ /home/system/xiaozhi/xiaozhi-esp32-server/main/xiaozhi-server/models/SenseVoiceSmall/model.pt
```

## Bước 4: Tạo 3 file tự động build

### 4.1 Tự build `manager-web`

Tạo file `update_8001.sh` ở `/home/system/xiaozhi/`:

```bash
cd /home/system/xiaozhi/xiaozhi-esp32-server
git fetch --all
git reset --hard
git pull origin main

cd /home/system/xiaozhi/xiaozhi-esp32-server/main/manager-web
npm install
npm run build
rm -rf /home/system/xiaozhi/manager-web
mv /home/system/xiaozhi/xiaozhi-esp32-server/main/manager-web/dist /home/system/xiaozhi/manager-web
```

Gán quyền:

```bash
chmod 777 update_8001.sh
```

### 4.2 Tự build và chạy `manager-api`

Tạo `update_8002.sh`:

```bash
cd /home/system/xiaozhi/xiaozhi-esp32-server
git pull origin main

cd /home/system/xiaozhi/xiaozhi-esp32-server/main/manager-api
rm -rf target
mvn clean package -Dmaven.test.skip=true
cd /home/system/xiaozhi/

PID=$(sudo netstat -tulnp | grep 8002 | awk '{print $7}' | cut -d'/' -f1)

rm -rf /home/system/xiaozhi/xiaozhi-esp32-api.jar
mv /home/system/xiaozhi/xiaozhi-esp32-server/main/manager-api/target/xiaozhi-esp32-api.jar /home/system/xiaozhi/xiaozhi-esp32-api.jar

if [ -z "$PID" ]; then
  echo "Không tìm thấy tiến trình chiếm cổng 8002"
else
  echo "Tìm thấy tiến trình chiếm cổng 8002, PID: $PID"
  kill -9 $PID
  kill -9 $PID
  echo "Đã kill tiến trình $PID"
fi

nohup java -jar xiaozhi-esp32-api.jar --spring.profiles.active=dev &
tail tail -f nohup.out
```

Gán quyền:

```bash
chmod 777 update_8002.sh
```

### 4.3 Tự build và chạy Python project

Tạo `update_8000.sh`:

```bash
cd /home/system/xiaozhi/xiaozhi-esp32-server
git pull origin main

PID=$(sudo netstat -tulnp | grep 8000 | awk '{print $7}' | cut -d'/' -f1)

if [ -z "$PID" ]; then
  echo "Không tìm thấy tiến trình chiếm cổng 8000"
else
  echo "Tìm thấy tiến trình chiếm cổng 8000, PID: $PID"
  kill -9 $PID
  kill -9 $PID
  echo "Đã kill tiến trình $PID"
fi
cd main/xiaozhi-server
source ~/.bashrc
conda activate xiaozhi-esp32-server
pip install -r requirements.txt
nohup python app.py >/dev/null &
tail -f /home/system/xiaozhi/xiaozhi-esp32-server/main/xiaozhi-server/tmp/server.log
```

Gán quyền:

```bash
chmod 777 update_8000.sh
```

## Cập nhật hằng ngày

Chạy lần lượt:

```bash
cd /home/system/xiaozhi
./update_8001.sh
./update_8002.sh
./update_8000.sh

tail -f nohup.out
tail -f /home/system/xiaozhi/xiaozhi-esp32-server/main/xiaozhi-server/tmp/server.log
```

## Lưu ý

Test platform `https://2662r3426b.vicp.fun` dùng Nginx làm reverse proxy. Cấu hình chi tiết có thể xem [ở đây](https://github.com/xinnan-tech/xiaozhi-esp32-server/issues/791).

### Câu hỏi thường gặp

1. Vì sao không thấy cổng 8001?
   - 8001 là cổng dev cho frontend. Nếu deploy server, không nên dùng `npm run serve`; nên build ra file tĩnh rồi để Nginx phục vụ.
2. Có cần cập nhật SQL thủ công mỗi lần không?
   - Không, vì dự án dùng **Liquibase** để quản lý version database và sẽ tự chạy script mới.
