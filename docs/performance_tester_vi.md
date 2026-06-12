# Hướng dẫn dùng công cụ kiểm thử hiệu năng

1. Tạo thư mục `data` trong `main/xiaozhi-server`
2. Tạo file `.config.yaml` trong `data`
3. Trong `data/.config.yaml`, điền cấu hình ASR, LLM, TTS và VLLM của bạn

Ví dụ:

```yaml
LLM:
  ChatGLMLLM:
    type: openai
    model_name: glm-4-flash
    url: https://open.bigmodel.cn/api/paas/v4/
    api_key: your-chat-glm-web-key

TTS:

VLLM:

ASR:
```

4. Chạy:

```bash
python performance_tester.py
```
