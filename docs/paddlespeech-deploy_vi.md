# Tích hợp PaddleSpeech TTS vào dịch vụ Xiaozhi

## Lưu ý chính

- Ưu điểm: chạy local offline, tốc độ tốt
- Nhược điểm: tính đến `2025-09-25`, model mặc định là tiếng Trung, không hỗ trợ đọc tiếng Anh. Nếu có tiếng Anh thì có thể không phát âm ra tiếng đọc.

## 1. Yêu cầu môi trường

- OS: Windows / Linux / WSL2
- Python 3.9+
- Paddle bản mới nhất
- Dùng `conda` hoặc `venv`

## 2. Khởi động dịch vụ PaddleSpeech

### Clone source

```bash
git clone https://github.com/PaddlePaddle/PaddleSpeech.git
cd PaddleSpeech
```

### Tạo môi trường

```bash
conda create -n paddle_env python=3.10 -y
conda activate paddle_env
```

### Cài Paddle

Làm theo trang chính thức:
https://www.paddlepaddle.org.cn/install

### Cài PaddleSpeech

```bash
pip install pytest-runner -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple
pip install paddlespeech -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Tải model

```bash
paddlespeech tts --input "你好，这是一次测试"
```

### Sửa cấu hình

Mở `PaddleSpeech/demos/streaming_tts_server/conf/tts_online_application.yaml` và đặt `protocol` là `websocket`.

### Khởi động

```bash
paddlespeech_server start --config_file ./demos/streaming_tts_server/conf/tts_online_application.yaml
```

## 3. Sửa cấu hình Xiaozhi

Trong `main/xiaozhi-server/data/.config.yaml`:

```yaml
selected_module:
  TTS: PaddleSpeechTTS
TTS:
  PaddleSpeechTTS:
    type: paddle_speech
    protocol: websocket
    url: ws://127.0.0.1:8092/paddlespeech/tts/streaming
    spk_id: 0
    sample_rate: 24000
    speed: 1.0
    volume: 1.0
    save_path:
```

Khởi động `python app.py`, mở `test_page.html` để xem log bên PaddleSpeech.
