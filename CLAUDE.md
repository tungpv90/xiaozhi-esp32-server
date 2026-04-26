# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**xiaozhi-esp32-server** is a backend platform for ESP32-based intelligent voice assistant hardware. ESP32 devices connect via WebSocket and the server handles the full voice pipeline: VAD → ASR → LLM → TTS, returning audio back to the device in real time.

## Repository Structure

```
main/
├── xiaozhi-server/   # Core AI engine (Python 3.10, aiohttp, asyncio)
├── manager-api/      # Management REST API (Java 21, Spring Boot 3.4.3)
├── manager-web/      # Web admin panel (Vue.js 2.6, Element UI)
└── manager-mobile/   # Mobile admin panel (uni-app, Vue 3, TypeScript)
docs/                 # Integration guides (MCP, Home Assistant, MQTT, etc.)
```

## Common Commands

### xiaozhi-server (Python)
```bash
cd main/xiaozhi-server
pip install -r requirements.txt
python app.py

# Run the WebSocket test page in browser (after server starts):
# open test/test_page.html

# Performance testing:
python performance_tester.py
```

### Docker (recommended for full stack)
```bash
cd main/xiaozhi-server
docker-compose up -d                                         # Production
docker-compose -f docker-compose.dev.yml up --build         # Dev with hot-reload
```

### manager-api (Java/Maven)
```bash
cd main/manager-api
mvn clean package
mvn spring-boot:run
```

### manager-web (Vue.js)
```bash
cd main/manager-web
npm install
npm run serve     # Dev server
npm run build     # Production build
```

### manager-mobile (uni-app)
```bash
cd main/manager-mobile
pnpm install
pnpm dev          # Dev server
pnpm build        # Production build
pnpm lint         # ESLint
pnpm lint:fix     # Auto-fix
pnpm type-check   # TypeScript validation
```

## Architecture

### Communication Flow
```
ESP32 Device
  │  WebSocket ws://host:8000/xiaozhi/v1/
  ▼
xiaozhi-server (Python, port 8000/8003)
  │  VAD → ASR → LLM → TTS pipeline (all async)
  │  HTTP requests for device config
  ▼
manager-api (Java, port 8002/8003)
  │  MySQL + Redis
  ▼
manager-web / manager-mobile (admin UI)
```

### xiaozhi-server internals (`main/xiaozhi-server/`)

- `app.py` — Entry point; starts WebSocket and HTTP servers
- `core/connection.py` — WebSocket connection lifecycle and device state machine
- `core/websocket_server.py` / `core/http_server.py` — Server initialization
- `core/handle/` — Message handler pipeline (audio receive, ASR, text send, TTS, reporting)
- `core/providers/` — Pluggable AI integrations, one subdirectory per capability:
  - `asr/` — Speech recognition (Sherpa ONNX, ModelScope, Silero VAD)
  - `tts/` — Text-to-speech (Edge TTS, Fish Speech, Huoshan, etc.)
  - `llm/` — Language models (OpenAI, Google, Baidu, local vLLM)
  - `vad/` — Voice activity detection
  - `intent/` — Intent recognition
  - `memory/` — Dialogue context and Mem0 AI long-term memory
  - `tools/` — Unified tool/function-calling dispatcher
- `plugins_func/` — Extensible plugin system (weather, news, Home Assistant, etc.); plugins are auto-imported
- `config.yaml` — Default configuration; user overrides go in `data/.config.yaml` (never edit this directly)
- `agent-base-prompt.txt` — Base system prompt template with placeholder variables

### manager-api internals (`main/manager-api/src/main/java/xiaozhi/modules/`)

Modules: `agent`, `config`, `device`, `knowledge`, `llm`, `security`, `sys`, `timbre`, `voiceclone`

Key technologies: MyBatis Plus ORM, Druid connection pool, Liquibase DB migrations, Apache Shiro auth, Redis cache via Spring Cache.

### Configuration Layering

`config.yaml` (defaults) is overridden by `data/.config.yaml` (user/runtime values). Never commit secrets; put API keys in `data/.config.yaml` or environment variables.

### Provider Pattern

All AI services follow the same pluggable pattern under `core/providers/<capability>/`. To add a new provider, implement the provider interface in the appropriate subdirectory and register it in the config.

### Port Map

| Service | Port | Protocol |
|---------|------|----------|
| xiaozhi-server WebSocket | 8000 | WS |
| xiaozhi-server HTTP (OTA/vision) | 8003 | HTTP |
| manager-api | 8002 | HTTP |
| manager-web | 8001 | HTTP |
| MySQL | 3306 | TCP |
| Redis | 6379 | TCP |

## Key Documentation

Integration guides live in `docs/`:
- `docs/Deployment.md` — Full deployment walkthrough
- `docs/mcp-endpoint-integration.md` — MCP Protocol
- `docs/homeassistant-integration.md` — Home Assistant
- `docs/FAQ.md` — Common issues
- `main/README_en.md` — Technical architecture details in English
