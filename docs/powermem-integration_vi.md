# Hướng dẫn tích hợp PowerMem

## Giới thiệu

[PowerMem](https://www.powermem.ai/) là component bộ nhớ cho agent do OceanBase mở nguồn. Nó dùng LLM local để tóm tắt và truy hồi bộ nhớ, giúp quản lý memory hiệu quả hơn.

Chi phí:

- Dùng SQLite + LLM miễn phí = hoàn toàn miễn phí
- Dùng cloud LLM hoặc cloud DB = tính theo dịch vụ

Tài nguyên:

- GitHub: https://github.com/oceanbase/powermem
- Trang chủ: https://www.powermem.ai/
- Ví dụ: https://github.com/oceanbase/powermem/tree/main/examples

## Tính năng

- Tóm tắt local
- User profile
- Quên thông tin cũ theo đường cong quên Ebbinghaus
- Nhiều backend DB: OceanBase, SeekDB, PostgreSQL, SQLite
- Hỗ trợ nhiều LLM: Qwen, Zhipu, OpenAI
- Truy hồi ngữ nghĩa bằng vector search
- Hỗ trợ private deployment
- Xử lý async

## Cài đặt

```bash
pip install powermem
```

## Cấu hình

```yaml
selected_module:
  Memory: powermem

Memory:
  powermem:
    type: powermem
    enable_user_profile: true
    llm:
      provider: openai
      config:
        api_key: your_llm_api_key
        model: qwen-plus
    embedder:
      provider: openai
      config:
        api_key: your_embedding_api_key
        model: text-embedding-v4
        openai_base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
    vector_store:
      provider: sqlite
      config: {}
```

## Chế độ memory

| Mode | Config | Chức năng |
|------|--------|----------|
| Memory thường | `enable_user_profile: false` | Lưu và truy hồi hội thoại |
| User profile | `enable_user_profile: true` | Bộ nhớ + trích xuất hồ sơ người dùng |

## Dùng Qwen

### Cấu hình mẫu

```yaml
Memory:
  powermem:
    type: powermem
    enable_user_profile: true
    llm:
      provider: qwen
      config:
        api_key: sk-xxxxxxxxxxxxxxxx
        model: qwen-plus
    embedder:
      provider: openai
      config:
        api_key: sk-xxxxxxxxxxxxxxxx
        model: text-embedding-v4
        openai_base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
    vector_store:
      provider: sqlite
      config: {}
```

## Dùng Zhipu miễn phí

```yaml
Memory:
  powermem:
    type: powermem
    enable_user_profile: true
    llm:
      provider: openai
      config:
        api_key: xxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxx
        model: glm-4-flash
        openai_base_url: https://open.bigmodel.cn/api/paas/v4/
    embedder:
      provider: openai
      config:
        api_key: xxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxx
        model: embedding-3
        openai_base_url: https://open.bigmodel.cn/api/paas/v4/
    vector_store:
      provider: sqlite
      config: {}
```

## Dùng OceanBase

```yaml
Memory:
  powermem:
    type: powermem
    enable_user_profile: true
    llm:
      provider: qwen
      config:
        api_key: sk-xxxxxxxxxxxxxxxx
        model: qwen-plus
    embedder:
      provider: openai
      config:
        api_key: sk-xxxxxxxxxxxxxxxx
        model: text-embedding-v4
        openai_base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
    vector_store:
      provider: oceanbase
      config:
        host: 127.0.0.1
        port: 2881
        user: root@test
        password: your_password
        db_name: powermem
        collection_name: memories
        embedding_model_dims: 1536
```

## Cô lập bộ nhớ theo thiết bị

PowerMem tự dùng `device_id` làm `user_id`, nên mỗi thiết bị có bộ nhớ riêng.

## UserMemory

`UserMemory` tự trích xuất hồ sơ người dùng từ hội thoại.

## So sánh

| Tính năng | PowerMem | mem0ai | mem_local_short |
|----------|----------|--------|-----------------|
| Cách hoạt động | Tóm tắt local | API cloud | Tóm tắt local |
| Lưu trữ | Local/cloud DB | Cloud | YAML local |
| Chi phí | Tùy LLM/DB | 1000 lần/tháng miễn phí | Miễn phí |
| Truy hồi ngữ nghĩa | Có | Có | Không |
| User profile | Có | Không | Không |
| Quên thông minh | Có | Không | Không |

## Kiểm tra nhanh

```bash
source .venv/bin/activate
python -c "from powermem import AsyncMemory; print('PowerMem import OK')"
python -c "from powermem import UserMemory; print('UserMemory import OK')"
```
