# Hướng dẫn tích hợp Fish-Speech

1. Đăng nhập AutoDL và chọn image:

```text
PyTorch / 2.1.0 / 3.10(ubuntu22.04) / cuda 12.1
```

2. Sau khi máy khởi động, bật tăng tốc học thuật:

```bash
source /etc/network_turbo
```

3. Vào thư mục làm việc:

```bash
cd autodl-tmp/
```

4. Clone dự án:

```bash
git clone https://gitclone.com/github.com/fishaudio/fish-speech.git ; cd fish-speech
```

5. Cài dependency:

```bash
pip install -e.
```

Nếu lỗi, cài `portaudio`:

```bash
apt-get install portaudio19-dev -y
```

Sau đó cài lại torch:

```bash
pip install torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cu121
```

6. Tải model:

```bash
cd tools
python download_models.py
```

7. Chạy API:

```bash
python -m tools.api_server --listen 0.0.0.0:6006
```

8. Mở trang AutoDL và bật port forwarding:

https://autodl.com/console/instance/list

Nhấn `Custom service` để bật chuyển tiếp cổng như hình:

![Custom service](images/fishspeech/autodl-01.png)

Sau khi cấu hình xong, mở `http://localhost:6006/` trên máy local là có thể dùng API Fish-Speech.

![Service preview](images/fishspeech/autodl-02.png)

Nếu bạn dùng triển khai đơn module, cấu hình cơ bản:

```yaml
selected_module:
  TTS: FishSpeech
TTS:
  FishSpeech:
    reference_audio: ["config/assets/wakeup_words.wav",]
    reference_text: ["哈啰啊，我是小智啦，声音好听的台湾女孩一枚，超开心认识你耶，最近在忙啥，别忘了给我来点有趣的料哦，我超爱听八卦的啦",]
    api_key: "123"
    api_url: "http://127.0.0.1:6006/v1/tts"
```

Sau đó khởi động lại dịch vụ.
