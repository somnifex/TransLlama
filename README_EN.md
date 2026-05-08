# TransLlama

<p align="center">
  <strong>🦙 Self-hosted Translation API & WebUI powered by local GGUF models</strong>
</p>

<p align="center">
  <a href="README.md">中文文档</a>
</p>

TransLlama is a self-hosted translation API backend built with FastAPI and llama-cpp-python. It serves local GGUF models through OpenAI-compatible and translation-specific endpoints, with a built-in web translation interface, supporting mutual translation across 38 languages.

---

## Features

- **OpenAI-Compatible API** — `/v1/chat/completions`, works with OpenAI SDK and any compatible client
- **Translation Endpoint** — `/v1/translate`, with terminology injection, context-aware, and format preservation
- **Web Translation UI** — Built-in Google-Translate-style web interface at `/`
- **Multi-Model Routing** — Configure multiple models in `models.yaml` with default + fallback switching
- **Streaming** — SSE (Server-Sent Events) for both API endpoints and WebUI
- **Auth & Rate Limiting** — Bearer token auth with per-key rate limits
- **38 Languages** — Powered by Tencent Hunyuan Hy-MT1.5, all pairs supported
- **Docker Ready** — Dockerfile + docker-compose for one-command deployment

---

## Supported Languages

| Language              | Code      | Language   | Code  | Language  | Code |
| --------------------- | --------- | ---------- | ----- | --------- | ---- |
| Chinese (Simplified)  | `zh`      | English    | `en`  | French    | `fr` |
| Portuguese            | `pt`      | Spanish    | `es`  | Japanese  | `ja` |
| Turkish               | `tr`      | Russian    | `ru`  | Arabic    | `ar` |
| Korean                | `ko`      | Thai       | `th`  | Italian   | `it` |
| German                | `de`      | Vietnamese | `vi`  | Malay     | `ms` |
| Indonesian            | `id`      | Filipino   | `tl`  | Hindi     | `hi` |
| Chinese (Traditional) | `zh-Hant` | Polish     | `pl`  | Czech     | `cs` |
| Dutch                 | `nl`      | Khmer      | `km`  | Burmese   | `my` |
| Persian               | `fa`      | Gujarati   | `gu`  | Urdu      | `ur` |
| Telugu                | `te`      | Marathi    | `mr`  | Hebrew    | `he` |
| Bengali               | `bn`      | Tamil      | `ta`  | Ukrainian | `uk` |
| Tibetan               | `bo`      | Kazakh     | `kk`  | Mongolian | `mn` |
| Uyghur                | `ug`      | Cantonese  | `yue` |           |      |

---

## Quick Start

### Prerequisites

- Python 3.12+
- pip or [uv](https://github.com/astral-sh/uv)

### Install

```bash
git clone <repository-url>
cd TransLlama

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or install with dev dependencies (includes testing tools)
pip install -r requirements-dev.txt
```

> **For GPU acceleration**, install the appropriate `llama-cpp-python` backend first — see [Hardware Acceleration](#hardware-acceleration) below.

### Download Model

Recommended: Tencent official GGUF quantized models.

```bash
# Option 1: huggingface-cli
huggingface-cli download tencent/HY-MT1.5-1.8B-GGUF \
  HY-MT1.5-1.8B-Q4_K_M.gguf \
  --local-dir storage/models

# Option 2: Python script
python -c "
from huggingface_hub import hf_hub_download
hf_hub_download(
    repo_id='tencent/HY-MT1.5-1.8B-GGUF',
    filename='HY-MT1.5-1.8B-Q4_K_M.gguf',
    local_dir='storage/models'
)
print('Done')
"
```

### Configure

```bash
cp .env.example .env
# Edit .env — set your API keys
```

`models.yaml` points to `./storage/models/HY-MT1.5-1.8B-Q4_K_M.gguf` by default. Modify the `path` field if you downloaded a different version.

### Run

```bash
# Direct
python main.py

# Dev mode with hot-reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

After startup:
- **Web Translation UI**: http://localhost:8000/
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Quick Test

```bash
# Health check (no auth required)
curl http://localhost:8000/health

# Chinese → English
curl -X POST http://localhost:8000/v1/translate \
  -H "Authorization: Bearer test_key_1" \
  -H "Content-Type: application/json" \
  -d '{"text": "人工智能正在改变世界", "source_lang": "zh", "target_lang": "en"}'

# English → Chinese
curl -X POST http://localhost:8000/v1/translate \
  -H "Authorization: Bearer test_key_1" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "source_lang": "en", "target_lang": "zh"}'
```

---

## Web Translation UI

TransLlama includes a built-in web translation interface at the root path `/`, styled similar to Google Translate.

**Features:**
- Side-by-side source/target panels
- 38 language selector with swap button
- Auto-translate with debounce (600ms)
- Streaming token-by-token display
- Custom terminology editor
- Copy result / clear input / character count
- Ctrl+Enter manual trigger
- Mobile-responsive layout

No extra build tools needed — it's a single HTML file served by FastAPI.

---

## API Reference

### Authentication

All endpoints except `/health` require a Bearer token:

```
Authorization: Bearer YOUR_API_KEY
```

API keys are configured in `.env` (`API_KEYS`), comma-separated.

---

### GET /health

Health check, no auth required.

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": 1,
  "uptime_seconds": 3600.5
}
```

---

### GET /v1/models

List all available models.

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "hy-mt-general",
      "object": "model",
      "created": 1715100000,
      "owned_by": "transllama",
      "description": "General purpose translation model (Hy-MT1.5-1.8B)",
      "supported_languages": ["zh", "en", "fr", "ja", "ko", "..."]
    }
  ]
}
```

---

### POST /v1/translate

Translation endpoint with advanced features.

**Request Parameters:**

| Field             | Type   | Required | Default       | Description                                   |
| ----------------- | ------ | -------- | ------------- | --------------------------------------------- |
| `text`            | string | Yes      | —             | Text to translate                             |
| `source_lang`     | string | Yes      | —             | Source language code (e.g., `en`, `zh`, `ja`) |
| `target_lang`     | string | Yes      | —             | Target language code                          |
| `model`           | string | No       | default model | Model name to use                             |
| `terminology`     | object | No       | `null`        | Term mapping, e.g. `{"API": "接口"}`            |
| `context`         | string | No       | `null`        | Context info to improve quality               |
| `preserve_format` | bool   | No       | `false`       | Preserve formatting markers                   |
| `stream`          | bool   | No       | `false`       | Enable SSE streaming                          |

**Request Example:**
```json
{
  "text": "Hello world",
  "source_lang": "en",
  "target_lang": "zh",
  "terminology": {"world": "世界"},
  "context": "Technical document title"
}
```

**Response:**
```json
{
  "translation": "你好世界",
  "source_lang": "en",
  "target_lang": "zh",
  "model": "hy-mt-general",
  "usage": {
    "characters": 11,
    "prompt_tokens": 42,
    "completion_tokens": 5
  }
}
```

**Streaming Response (`stream: true`):**
```
data: {"text": "你好"}

data: {"text": "世界"}

data: [DONE]
```

---

### POST /v1/chat/completions

OpenAI-compatible chat completions endpoint. Works with OpenAI SDK.

**Request Parameters:**

| Field         | Type   | Required | Default       | Description                                         |
| ------------- | ------ | -------- | ------------- | --------------------------------------------------- |
| `model`       | string | No       | default model | Model name                                          |
| `messages`    | array  | Yes      | —             | Message list `[{"role": "user", "content": "..."}]` |
| `temperature` | float  | No       | 0.7           | Sampling temperature (0.0-2.0)                      |
| `top_p`       | float  | No       | 0.6           | Nucleus sampling (0.0-1.0)                          |
| `top_k`       | int    | No       | 20            | Top-K sampling                                      |
| `max_tokens`  | int    | No       | 2048          | Max output tokens                                   |
| `stream`      | bool   | No       | `false`       | Enable SSE streaming                                |

**Request Example:**
```json
{
  "model": "hy-mt-general",
  "messages": [
    {"role": "user", "content": "将以下文本翻译为英语，注意只需要输出翻译后的结果，不要额外解释：\n你好世界"}
  ]
}
```

**Response:**
```json
{
  "id": "chatcmpl-a1b2c3d4",
  "object": "chat.completion",
  "created": 1715100000,
  "model": "hy-mt-general",
  "choices": [
    {
      "index": 0,
      "message": {"role": "assistant", "content": "Hello World"},
      "finish_reason": "stop"
    }
  ],
  "usage": {"prompt_tokens": 35, "completion_tokens": 3, "total_tokens": 38}
}
```

**Streaming Response (`stream: true`):**
```
data: {"id":"chatcmpl-a1b2c3d4","object":"chat.completion.chunk","created":1715100000,"model":"hy-mt-general","choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}

data: {"id":"chatcmpl-a1b2c3d4","object":"chat.completion.chunk","created":1715100000,"model":"hy-mt-general","choices":[{"index":0,"delta":{"content":" World"},"finish_reason":null}]}

data: {"id":"chatcmpl-a1b2c3d4","object":"chat.completion.chunk","created":1715100000,"model":"hy-mt-general","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

---

## Advanced Usage

### Terminology Injection

Ensure consistent translation of domain-specific terms:

```bash
curl -X POST http://localhost:8000/v1/translate \
  -H "Authorization: Bearer test_key_1" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The API interface returns a response",
    "source_lang": "en",
    "target_lang": "zh",
    "terminology": {
      "API": "API",
      "interface": "接口",
      "response": "响应"
    }
  }'
```

### Context-Aware Translation

Provide context to produce more accurate translations:

```bash
curl -X POST http://localhost:8000/v1/translate \
  -H "Authorization: Bearer test_key_1" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Submit",
    "source_lang": "en",
    "target_lang": "zh",
    "context": "Button label in a web form"
  }'
```

### Format Preservation

Preserve Markdown, HTML tags, and other formatting markers:

```bash
curl -X POST http://localhost:8000/v1/translate \
  -H "Authorization: Bearer test_key_1" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Click the **Submit** button to continue.",
    "source_lang": "en",
    "target_lang": "zh",
    "preserve_format": true
  }'
```

### Streaming

Stream results progressively for long texts:

```bash
curl -N -X POST http://localhost:8000/v1/translate \
  -H "Authorization: Bearer test_key_1" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Artificial intelligence is transforming the world in unprecedented ways.",
    "source_lang": "en",
    "target_lang": "zh",
    "stream": true
  }'
```

### Using OpenAI Python SDK

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="test_key_1",
)

# Sync call
response = client.chat.completions.create(
    model="hy-mt-general",
    messages=[
        {"role": "user", "content": "将以下文本翻译为英语，注意只需要输出翻译后的结果，不要额外解释：\n你好世界"}
    ],
)
print(response.choices[0].message.content)

# Streaming
stream = client.chat.completions.create(
    model="hy-mt-general",
    messages=[
        {"role": "user", "content": "将以下文本翻译为英语，注意只需要输出翻译后的结果，不要额外解释：\n你好世界"}
    ],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### Using requests

```python
import requests

resp = requests.post(
    "http://localhost:8000/v1/translate",
    headers={"Authorization": "Bearer test_key_1"},
    json={
        "text": "Hello world",
        "source_lang": "en",
        "target_lang": "zh",
    },
)
print(resp.json()["translation"])
```

---

## Configuration

### Environment Variables (.env)

| Variable                         | Default                            | Description                          |
| -------------------------------- | ---------------------------------- | ------------------------------------ |
| `API_KEYS`                       | `test_key_1,test_key_2,test_key_3` | Comma-separated API keys             |
| `DEFAULT_MODEL`                  | `hy-mt-general`                    | Default model name                   |
| `FALLBACK_MODEL`                 | `hy-mt-general`                    | Fallback when default fails          |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | `60`                               | Per-key rate limit                   |
| `MODEL_STORAGE_PATH`             | `./storage/models`                 | Model files directory                |
| `MODELS_CONFIG_PATH`             | `./models.yaml`                    | Model config file path               |
| `HOST`                           | `0.0.0.0`                          | Server bind address                  |
| `PORT`                           | `8000`                             | Server port                          |
| `WORKERS`                        | `1`                                | Uvicorn worker count                 |
| `LOG_LEVEL`                      | `INFO`                             | Log level (DEBUG/INFO/WARNING/ERROR) |

### Model Configuration (models.yaml)

```yaml
default_model: "hy-mt-general"       # Default model
fallback_model: "hy-mt-general"      # Fallback model

models:
  - name: "hy-mt-general"            # Model ID used in API
    path: "./storage/models/HY-MT1.5-1.8B-Q4_K_M.gguf"
    description: "General purpose translation model (Hy-MT1.5-1.8B)"
    parameters:
      n_ctx: 4096                    # Context window (min 2048)
      n_gpu_layers: 0                # GPU layers: 0=CPU, -1=all GPU
      temperature: 0.7               # Sampling temperature
      top_p: 0.6                     # Nucleus sampling
      top_k: 20                      # Top-K sampling
      repeat_penalty: 1.05           # Repetition penalty
      max_tokens: 2048               # Max output tokens
    supported_languages:             # Supported language codes
      - zh
      - en
      - ja
      # ... (38 total, see models.yaml)
```

**Multi-model example:**

```yaml
default_model: "hy-mt-q4"
fallback_model: "hy-mt-q8"

models:
  - name: "hy-mt-q4"
    path: "./storage/models/HY-MT1.5-1.8B-Q4_K_M.gguf"
    description: "Fast translation (Q4 quantization)"
    parameters: { n_ctx: 4096, n_gpu_layers: 0, temperature: 0.7, top_p: 0.6, top_k: 20, repeat_penalty: 1.05, max_tokens: 2048 }
    supported_languages: [zh, en, ja, ko, fr, de]

  - name: "hy-mt-q8"
    path: "./storage/models/HY-MT1.5-1.8B-Q8_0.gguf"
    description: "High quality translation (Q8 quantization)"
    parameters: { n_ctx: 4096, n_gpu_layers: -1, temperature: 0.7, top_p: 0.6, top_k: 20, repeat_penalty: 1.05, max_tokens: 2048 }
    supported_languages: [zh, en, ja, ko, fr, de]
```

Specify model per request:
```json
{"text": "Hello", "source_lang": "en", "target_lang": "zh", "model": "hy-mt-q8"}
```

---

## Docker Deployment

### docker-compose (Recommended)

```bash
# Ensure model files are in storage/models/ and .env is configured

docker-compose up --build        # Build and start
docker-compose up -d             # Run in background
docker-compose logs -f transllama  # View logs
docker-compose down              # Stop
```

### Docker Standalone

```bash
docker build -t transllama .

docker run -d \
  --name transllama \
  -p 8000:8000 \
  -v $(pwd)/storage/models:/app/storage/models \
  -v $(pwd)/models.yaml:/app/models.yaml \
  -v $(pwd)/.env:/app/.env \
  transllama
```

---

## Hardware Acceleration

When installing `llama-cpp-python`, set the `CMAKE_ARGS` environment variable to select the backend. After installation, configure `n_gpu_layers` in `models.yaml` to control GPU layer offloading (`-1` = all, `0` = CPU only).

### CUDA (NVIDIA)

```bash
# Build from source
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
```

Pre-built wheels (CUDA 12.1–12.5, Python 3.10–3.12):

```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
# Also available: cu122 / cu123 / cu124 / cu125
```

### Metal (Apple Silicon / macOS)

```bash
CMAKE_ARGS="-DGGML_METAL=on" pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
```

Pre-built wheels (macOS 11.0+, Python 3.10–3.12):

```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/metal
```

> For M-series build errors, use:
> `CMAKE_ARGS="-DCMAKE_OSX_ARCHITECTURES=arm64 -DCMAKE_APPLE_SILICON_PROCESSOR=arm64 -DGGML_METAL=on"`

### ROCm / hipBLAS (AMD)

```bash
CMAKE_ARGS="-DGGML_HIPBLAS=on" pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
```

### Vulkan (Cross-platform: NVIDIA / AMD / Intel)

```bash
CMAKE_ARGS="-DGGML_VULKAN=on" pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
```

### SYCL (Intel GPU / oneAPI)

```bash
# Source oneAPI environment first
source /opt/intel/oneapi/setvars.sh

CMAKE_ARGS="-DGGML_SYCL=on -DCMAKE_C_COMPILER=icx -DCMAKE_CXX_COMPILER=icpx" \
  pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
```

### OpenBLAS (CPU acceleration)

```bash
CMAKE_ARGS="-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS" \
  pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
```

### RPC (Distributed inference)

```bash
CMAKE_ARGS="-DGGML_RPC=on" pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
```

### CPU-only Pre-built Wheel

```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

### Windows Notes

If CMake cannot find compilers, set:

```powershell
$env:CMAKE_GENERATOR = "MinGW Makefiles"
```

### Post-installation Configuration

Adjust GPU offload layers in `models.yaml`:

```yaml
parameters:
  n_gpu_layers: -1    # Offload all layers to GPU
  n_gpu_layers: 20    # Partial offload (limited VRAM)
  n_gpu_layers: 0     # CPU only (default)
```

---

## Recommended Models

| Model                | Size   | Quantization | Notes                      | Link                                                                            |
| -------------------- | ------ | ------------ | -------------------------- | ------------------------------------------------------------------------------- |
| HY-MT1.5-1.8B-Q4_K_M | 1.1 GB | Q4_K_M       | Best speed/quality balance | [tencent/HY-MT1.5-1.8B-GGUF](https://huggingface.co/tencent/HY-MT1.5-1.8B-GGUF) |
| HY-MT1.5-1.8B-Q6_K   | 1.4 GB | Q6_K         | Higher quality             | [tencent/HY-MT1.5-1.8B-GGUF](https://huggingface.co/tencent/HY-MT1.5-1.8B-GGUF) |
| HY-MT1.5-1.8B-Q8_0   | 1.8 GB | Q8_0         | Near full precision        | [tencent/HY-MT1.5-1.8B-GGUF](https://huggingface.co/tencent/HY-MT1.5-1.8B-GGUF) |

> **Note:** The [AngelSlim](https://huggingface.co/AngelSlim) 1.25-bit/2-bit ultra-compressed variants use custom quantization kernels (SEQ/STQ) not yet supported by standard llama-cpp-python.

---

## Project Structure

```
TransLlama/
├── api/                           # API layer
│   ├── routes/                    # Route handlers
│   │   ├── chat.py                #   /v1/chat/completions
│   │   ├── translate.py           #   /v1/translate
│   │   ├── models.py              #   /v1/models
│   │   └── health.py              #   /health
│   └── dependencies.py            # Auth + rate limit DI
├── services/                      # Business logic
│   ├── model_manager.py           # Model loading, cache, routing, fallback
│   ├── translation_service.py     # Translation orchestration, ChatML, streaming
│   └── prompt_builder.py          # Hy-MT1.5 prompt engineering
├── models/                        # Pydantic schemas
│   ├── requests.py                # Request schemas
│   ├── responses.py               # Response schemas
│   └── config.py                  # Config schemas
├── core/                          # Infrastructure
│   ├── config.py                  # pydantic-settings config
│   ├── auth.py                    # API key auth
│   ├── rate_limit.py              # In-memory rate limiter
│   ├── middleware.py              # CORS, logging, error handling
│   └── exceptions.py              # Custom exceptions
├── static/                        # Web UI
│   └── index.html                 # Translation web interface
├── storage/models/                # GGUF model files (gitignored)
├── main.py                        # App entrypoint
├── models.yaml                    # Model configuration
├── pyproject.toml                 # Project metadata
├── requirements.txt               # Runtime dependencies
├── requirements-dev.txt           # Dev dependencies
├── .env.example                   # Environment template
├── Dockerfile                     # Container image
├── docker-compose.yml             # Container orchestration
└── curl_examples.sh               # API test script
```

---

## Error Handling

All errors return a unified JSON format:

| HTTP Status | Type                       | Description                |
| ----------- | -------------------------- | -------------------------- |
| 400         | `InvalidLanguageException` | Unsupported language code  |
| 401         | `Unauthorized`             | Invalid or missing API key |
| 404         | `ModelNotFoundException`   | Model not found            |
| 429         | `Too Many Requests`        | Rate limit exceeded        |
| 500         | `ModelLoadException`       | Model failed to load       |
| 500         | `TranslationException`     | Translation error          |

**Example:**
```json
{
  "error": "Invalid language",
  "detail": "Source language 'xx' is not supported. Supported languages: zh, en, fr, ..."
}
```

---

## Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Dev mode with hot-reload
uvicorn main:app --reload
```

---

## Performance Tips

1. **Choose Q4_K_M quantization** — Best speed/quality tradeoff
2. **Enable GPU offloading** — Set `n_gpu_layers: -1` for significant speedup
3. **Reduce context window** — Set `n_ctx: 2048` for short texts to save memory
4. **Use streaming** — Enable `stream: true` for better UX on long texts
5. **Lazy model loading** — Models load on first request, not at startup

---

## License

MIT License — see [LICENSE](LICENSE).

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) — High-performance Python web framework
- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) — Python bindings for llama.cpp
- [Hy-MT1.5](https://huggingface.co/tencent/HY-MT1.5-1.8B) — Tencent Hunyuan translation model
- [AngelSlim](https://github.com/Tencent/AngelSlim) — Tencent model compression toolkit