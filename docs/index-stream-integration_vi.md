# Hướng dẫn dùng IndexStreamTTS

## Chuẩn bị môi trường

### 1. Clone project

```bash
git clone https://github.com/Ksuriuri/index-tts-vllm.git
cd index-tts-vllm
git checkout 224e8d5e5c8f66801845c66b30fa765328fd0be3
```

### 2. Tạo và kích hoạt môi trường conda

```bash
conda create -n index-tts-vllm python=3.12
conda activate index-tts-vllm
```

### 3. Cài PyTorch 2.8.0

Kiểm tra driver/CUDA:

```bash
nvidia-smi
nvcc --version
```

Sau đó cài torch:

```bash
pip install torch torchvision
```

### 4. Cài dependency

```bash
pip install -r requirements.txt
```

### 5. Tải model weight

Có thể tải bản official từ HuggingFace hoặc ModelScope rồi convert sang định dạng phù hợp với vLLM.

### 6. Chỉnh API cho phù hợp dự án

Sửa `api_server.py` để endpoint `/tts` trả thẳng dữ liệu âm thanh:

```python
@app.post("/tts", responses={
    200: {"content": {"application/octet-stream": {}}},
    500: {"content": {"application/json": {}}}
})
async def tts_api(request: Request):
    try:
        data = await request.json()
        text = data["text"]
        character = data["character"]

        global tts
        sr, wav = await tts.infer_with_ref_audio_embed(character, text)

        return Response(content=wav.tobytes(), media_type="application/octet-stream")
    except Exception as ex:
        tb_str = ''.join(traceback.format_exception(type(ex), ex, ex.__traceback__))
        print(tb_str)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(tb_str)}
        )
```

### 7. Viết script khởi động

```bash
conda activate index-tts-vllm
nohup python api_server.py --model_dir /path/to/IndexTTS-1.5 --port 11996 > tmp/server.log 2>&1 &
```

Xem log bằng:

```bash
tail -f tmp/server.log
```

### 8. Cấu hình giọng

Trong `assets/speaker.json`, khai báo speaker:

```json
{
  "说话人名称1": [
    "audio1.wav",
    "audio2.wav"
  ],
  "说话人名称2": [
    "audio3.wav"
  ]
}
```

Sau đó restart service để đăng ký giọng.

## Cấu hình Xiaozhi

Trong `data/.config.yaml`:

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

Khởi động `python app.py`, mở `test_page.html` để kiểm tra log bên TTS.
