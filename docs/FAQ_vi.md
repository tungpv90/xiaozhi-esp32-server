# Câu hỏi thường gặp

### 1. Vì sao câu tôi nói bị nhận thành nhiều tiếng Hàn, Nhật, Anh?

Hãy kiểm tra `models/SenseVoiceSmall` đã có file `model.pt` chưa. Nếu chưa, hãy tải model tại:
[tải file model nhận dạng giọng nói](Deployment.md#model-file)

### 2. Vì sao xuất hiện lỗi "TTS task error file not exists"?

Hãy kiểm tra bạn đã cài đúng `libopus` và `ffmpeg` bằng `conda` chưa.

Nếu chưa cài, dùng:

```bash
conda install conda-forge::libopus
conda install conda-forge::ffmpeg
```

### 3. TTS hay thất bại, hay timeout

Nếu `EdgeTTS` hay lỗi, hãy kiểm tra xem bạn có đang bật proxy/VPN không. Nếu có, thử tắt rồi chạy lại.

Nếu dùng Doubao TTS của Volcano Engine và hay lỗi, nên dùng bản trả phí vì bản test chỉ hỗ trợ 2 luồng đồng thời.

### 4. Wi-Fi kết nối được server tự dựng nhưng 4G thì không

Nguyên nhân: firmware của Xiaoge yêu cầu kết nối an toàn ở chế độ 4G.

Hướng xử lý:

1. Sửa code theo video: https://www.bilibili.com/video/BV18MfTYoE85
2. Dùng Nginx cấu hình SSL: https://icnt94i5ctj4.feishu.cn/docx/GnYOdMNJOoRCljx1ctecsj9cnRe

### 5. Làm sao tăng tốc phản hồi hội thoại?

Mặc định dự án ưu tiên phương án rẻ. Khuyên người mới cứ dùng model miễn phí trước để đảm bảo "chạy được", rồi tối ưu tốc độ sau.

Từ phiên bản `0.5.2`, dự án hỗ trợ cấu hình stream. So với bản cũ, tốc độ phản hồi tăng khoảng `2.5 giây`.

| Module | Cấu hình miễn phí cho người mới | Cấu hình stream |
|:---:|:---:|:---:|
| ASR | FunASR local | XunfeiStreamASR |
| LLM | glm-4-flash | qwen-flash |
| VLLM | glm-4v-flash | qwen3.5-flash |
| TTS | EdgeTTS | HuoshanDoubleStreamTTS |
| Intent | function_call | function_call |
| Memory | mem_local_short | mem_local_short |

Nếu quan tâm thời gian xử lý từng thành phần, hãy xem [báo cáo benchmark](https://github.com/xinnan-tech/xiaozhi-performance-research).

### 6. Tôi nói chậm, lúc dừng Xiaozhi hay cướp lời

Trong file cấu hình, tìm đoạn sau và tăng `min_silence_duration_ms` lên, ví dụ `1000`:

```yaml
VAD:
  SileroVAD:
    threshold: 0.5
    model_dir: models/snakers4_silero-vad
    min_silence_duration_ms: 700
```

### 7. Hướng dẫn triển khai

1. [Triển khai tối giản](./Deployment.md)
2. [Triển khai full module](./Deployment_all.md)
3. [Triển khai MQTT gateway](./mqtt-gateway-integration.md)
4. [Tự động kéo code mới rồi build và chạy](./dev-ops-integration.md)
5. [Tích hợp Nginx](https://github.com/xinnan-tech/xiaozhi-esp32-server/issues/791)

### 9. Hướng dẫn biên dịch firmware

1. [Tự biên dịch firmware Xiaozhi](./firmware-build.md)
2. [Dùng firmware Xiaoge build sẵn rồi đổi OTA](./firmware-setting.md)
3. [Cấu hình OTA auto upgrade cho triển khai đơn module](./ota-upgrade-guide.md)

### 10. Hướng dẫn mở rộng

1. [Bật đăng ký số điện thoại vào智控台](./ali-sms-integration.md)
2. [Tích hợp HomeAssistant](./homeassistant-integration.md)
3. [Bật vision model để nhận diện ảnh chụp](./mcp-vision-integration.md)
4. [Triển khai MCP endpoint](./mcp-endpoint-enable.md)
5. [Kết nối MCP endpoint](./mcp-endpoint-integration.md)
6. [Lấy thông tin thiết bị bằng MCP](./mcp-get-device-info.md)
7. [Bật nhận diện giọng nói](./voiceprint-integration.md)
8. [Cấu hình nguồn tin tức](./newsnow_plugin_config.md)
9. [Tích hợp ragflow kho kiến thức](./ragflow-integration.md)
10. [Triển khai context source](./context-provider-integration.md)
11. [Tích hợp PowerMem](./powermem-integration.md)
12. [Cấu hình plugin thời tiết](./weather-integration.md)

### 11. Clone giọng nói và TTS local

1. [Clone voice trong智控台](./huoshan-streamTTS-voice-cloning.md)
2. [Tích hợp index-tts local](./index-stream-integration.md)
3. [Tích hợp fish-speech local](./fish-speech-integration.md)
4. [Tích hợp PaddleSpeech local](./paddlespeech-deploy.md)

### 12. Kiểm thử hiệu năng

1. [Hướng dẫn test tốc độ các thành phần](./performance_tester.md)
2. [Kết quả test công khai định kỳ](https://github.com/xinnan-tech/xiaozhi-performance-research)

### 13. Góp ý thêm

Bạn có thể gửi issue tại [đây](https://github.com/xinnan-tech/xiaozhi-esp32-server/issues).
