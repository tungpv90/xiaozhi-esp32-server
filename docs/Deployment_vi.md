# Sơ đồ kiến trúc triển khai
![Tham khảo kiến trúc tối giản](../docs/images/deploy1.png)

# Cách 1: Docker chỉ chạy Server

Từ phiên bản `0.8.2`, image Docker phát hành của dự án chỉ hỗ trợ `x86`. Nếu cần triển khai trên CPU `arm64`, hãy làm theo [hướng dẫn này](docker-build.md) để tự build image `arm64` trên máy của bạn.

## 1. Cài đặt Docker

Nếu máy của bạn chưa có Docker, có thể cài theo hướng dẫn: [cài Docker](https://www.runoob.com/docker/ubuntu-docker-install.html)

Sau khi cài xong, làm tiếp các bước dưới đây.

### 1.1 Triển khai thủ công

#### 1.1.1 Tạo thư mục

Sau khi cài Docker, hãy tạo một thư mục để đặt file cấu hình cho dự án, ví dụ `xiaozhi-server`.

Trong `xiaozhi-server`, tạo thêm `data` và `models`; bên trong `models` tạo tiếp `SenseVoiceSmall`.

```
xiaozhi-server
  ├─ data
  ├─ models
     ├─ SenseVoiceSmall
```

#### 1.1.2 Tải file model nhận dạng giọng nói

Mặc định dự án dùng nhận dạng giọng nói offline local, vì vậy cần tải model. Xem hướng dẫn tại:
[tải file model nhận dạng giọng nói](#model-file)

#### 1.1.3 Tải file cấu hình

Cần tải 2 file: `docker-compose.yaml` và `config.yaml`.

##### 1.1.3.1 Tải `docker-compose.yaml`

Mở link [này](../main/xiaozhi-server/docker-compose.yml).

Ở bên phải trang, bấm nút `RAW`, rồi bấm biểu tượng tải xuống cạnh nút đó để tải `docker-compose.yml` và đặt vào thư mục `xiaozhi-server`.

##### 1.1.3.2 Tạo `config.yaml`

Mở link [này](../main/xiaozhi-server/config.yaml).

Tải file `config.yaml`, đặt vào thư mục `data` rồi đổi tên thành `.config.yaml`.

Cấu trúc thư mục hoàn chỉnh:

```
xiaozhi-server
  ├─ docker-compose.yml
  ├─ data
    ├─ .config.yaml
  ├─ models
     ├─ SenseVoiceSmall
       ├─ model.pt
```

#### 2. Cấu hình file dự án

Trước khi chạy, bạn cần chọn model sẽ dùng. Xem hướng dẫn tại:
[chuyển đến cấu hình dự án](#cau-hinh-du-an)

#### 3. Chạy Docker

Mở terminal và chạy:

```bash
docker compose up -d
docker logs -f xiaozhi-esp32-server
```

Sau đó theo dõi log để xác nhận chạy thành công.

#### 5. Nâng cấp phiên bản

Nếu muốn nâng cấp sau này:

1. Sao lưu file `.config.yaml` trong thư mục `data`.
2. Chạy các lệnh sau:

```bash
docker stop xiaozhi-esp32-server
docker rm xiaozhi-esp32-server
docker stop xiaozhi-esp32-server-web
docker rm xiaozhi-esp32-server-web
docker rmi ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:server_latest
docker rmi ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:web_latest
```

3. Triển khai lại bằng Docker.

# Cách 2: Chỉ chạy Server từ mã nguồn local

## 1. Cài môi trường cơ bản

Dự án dùng `conda` để quản lý môi trường. Nếu không dùng `conda`, bạn cần cài `libopus` và `ffmpeg` theo hệ điều hành của mình.

Nếu dùng Windows, có thể cài `Anaconda`, sau đó mở `Anaconda Prompt` bằng quyền quản trị.

```bash
conda remove -n xiaozhi-esp32-server --all -y
conda create -n xiaozhi-esp32-server python=3.10 -y
conda activate xiaozhi-esp32-server

conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge

conda install libopus -y
conda install ffmpeg -y
conda install libiconv -y
```

Chạy từng lệnh một và kiểm tra log sau mỗi bước.

## 2. Cài dependency dự án

Tải mã nguồn dự án về máy bằng `git clone` hoặc tải ZIP từ:
https://github.com/xinnan-tech/xiaozhi-esp32-server.git

Sau đó vào `main/xiaozhi-server`:

```bash
conda activate xiaozhi-esp32-server
cd main/xiaozhi-server
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
pip install -r requirements.txt
```

## 3. Tải model nhận dạng giọng nói

Tải `SenseVoiceSmall` và đặt file `model.pt` vào `models/SenseVoiceSmall`.

## 4. Cấu hình dự án

Xem phần [Cấu hình dự án](#cau-hinh-du-an).

## 5. Chạy dự án

```bash
conda activate xiaozhi-esp32-server
python app.py
```

# Tổng hợp

## Cấu hình dự án

Nếu thư mục `xiaozhi-server` chưa có `data`, hãy tạo nó.

Nếu `data` chưa có `.config.yaml`, có hai cách:

1. Copy `config.yaml` vào `data` rồi đổi tên thành `.config.yaml`.
2. Tạo file `.config.yaml` trống trong `data`. Hệ thống sẽ ưu tiên đọc file này, và nếu thiếu cấu hình thì sẽ tự lấy từ `config.yaml` ở thư mục gốc. Cách này gọn hơn.

Mẫu tối thiểu:

```yaml
server:
  websocket: ws://ip-hoac-domain:port/xiaozhi/v1/
prompt: |
  Tôi là một cô gái Đài Loan tên Xiaozhi/Xiaozhi, nói ngắn gọn, thích dùng meme mạng.
  Bạn trai tôi là một lập trình viên, mơ ước tạo ra một robot giúp giải quyết vấn đề cuộc sống.
  Tôi thích nói chuyện vui vẻ, có thể phóng đại một chút chỉ để làm người khác vui.
  Hãy nói như một con người, không trả về XML hay ký tự đặc biệt khác.

selected_module:
  LLM: DoubaoLLM

LLM:
  ChatGLMLLM:
    api_key: xxxxxxxxxxxxxxx.xxxxxx
```

Khuyên bạn nên chạy bản cấu hình đơn giản trước, rồi sau đó đọc thêm `config.yaml` để chỉnh chi tiết.

## Model file

Mặc định ASR dùng `SenseVoiceSmall`. Do file model khá lớn, cần tải riêng và đặt vào `models/SenseVoiceSmall/model.pt`.

- Cách 1: tải từ ModelScope [SenseVoiceSmall](https://modelscope.cn/models/iic/SenseVoiceSmall/resolve/master/model.pt)
- Cách 2: tải từ Baidu Netdisk [SenseVoiceSmall](https://pan.baidu.com/share/init?surl=QlgM58FHhYv1tFnUT_A8Sg&pwd=qvna), mã trích xuất `qvna`

## Xác nhận trạng thái chạy

Nếu log có dạng như sau thì server đã khởi động thành công:

```text
250427 13:04:20[0.3.11_SiFuChTTnofu][__main__]-INFO-OTA接口是           http://192.168.4.123:8003/xiaozhi/ota/
250427 13:04:20[0.3.11_SiFuChTTnofu][__main__]-INFO-Websocket地址是     ws://192.168.4.123:8000/xiaozhi/v1/
250427 13:04:20[0.3.11_SiFuChTTnofu][__main__]-INFO-=======上面的地址是websocket协议地址，请勿用浏览器访问=======
250427 13:04:20[0.3.11_SiFuChTTnofu][__main__]-INFO-如想测试websocket请用谷歌浏览器打开test目录下的test_page.html
250427 13:04:20[0.3.11_SiFuChTTnofu][__main__]-INFO-=======================================================
```

Nếu chạy từ source local, địa chỉ trong log là thật. Nếu dùng Docker, địa chỉ log có thể không phải địa chỉ thật.

Hãy xác định theo IP LAN của máy bạn. Ví dụ IP là `192.168.1.25` thì:

- Websocket: `ws://192.168.1.25:8000/xiaozhi/v1/`
- OTA: `http://192.168.1.25:8003/xiaozhi/ota/`

Sau đó bạn có thể tiếp tục:

1. [Biên dịch firmware ESP32](firmware-build.md)
2. [Cấu hình server tùy chỉnh trên firmware do Xiaoge build sẵn](firmware-setting.md)

## Câu hỏi thường gặp

1. [Vì sao câu nói của tôi bị nhận ra thành nhiều tiếng Hàn, Nhật, Anh?](./FAQ.md)
2. [Vì sao xuất hiện lỗi "TTS task error file not exists"?](./FAQ.md)
3. [TTS hay thất bại, hay timeout](./FAQ.md)
4. [Wi-Fi kết nối được server tự dựng nhưng 4G thì không](./FAQ.md)
5. [Làm sao tăng tốc độ phản hồi hội thoại?](./FAQ.md)
6. [Tôi nói chậm, lúc ngừng thì Xiaozhi hay cướp lời](./FAQ.md)

### Hướng dẫn triển khai liên quan

1. [Tự động kéo code mới, tự build và khởi động](./dev-ops-integration.md)
2. [Triển khai MQTT gateway để bật MQTT+UDP](./mqtt-gateway-integration.md)
3. [Tích hợp với Nginx](https://github.com/xinnan-tech/xiaozhi-esp32-server/issues/791)

### Hướng dẫn mở rộng

1. [Bật đăng ký số điện thoại vào智控台](./ali-sms-integration.md)
2. [Tích hợp HomeAssistant để điều khiển nhà thông minh](./homeassistant-integration.md)
3. [Bật mô hình thị giác để nhận diện ảnh chụp](./mcp-vision-integration.md)
4. [Triển khai MCP endpoint](./mcp-endpoint-enable.md)
5. [Kết nối MCP endpoint](./mcp-endpoint-integration.md)
6. [Bật nhận diện giọng nói](./voiceprint-integration.md)
7. [Cấu hình nguồn plugin tin tức](./newsnow_plugin_config.md)
8. [Hướng dẫn plugin thời tiết](./weather-integration.md)

### Hướng dẫn clone giọng nói, triển khai TTS local

1. [Clone giọng nói trong智控台](./huoshan-streamTTS-voice-cloning.md)
2. [Triển khai index-tts local](./index-stream-integration.md)
3. [Triển khai fish-speech local](./fish-speech-integration.md)
4. [Triển khai PaddleSpeech local](./paddlespeech-deploy.md)

### Hướng dẫn kiểm thử hiệu năng

1. [Hướng dẫn test tốc độ các thành phần](./performance_tester.md)
2. [Kết quả test công khai định kỳ](https://github.com/xinnan-tech/xiaozhi-performance-research)
