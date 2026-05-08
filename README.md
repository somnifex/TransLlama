# TransLlama

TransLlama is a self-hosted translation API backend built with FastAPI and llama-cpp-python. It provides OpenAI-compatible endpoints for translation services using local GGUF models.

## Features

- **OpenAI-Compatible API**: `/v1/chat/completions` endpoint compatible with OpenAI SDK
- **Translation-Specific Endpoint**: `/v1/translate` with terminology, context, and format preservation
- **Multiple Model Support**: Load and route between multiple translation models with fallback
- **Streaming Output**: Server-Sent Events (SSE) for both endpoints
- **API Key Authentication**: Bearer token authentication
- **Rate Limiting**: Per-key request rate limiting
- **38 Languages**: Via Hy-MT1.5 models (Chinese, English, Japanese, Korean, French, German, etc.)
- **Docker Support**: Ready-to-use Dockerfile and docker-compose

## Quick Start

### Prerequisites

- Python 3.12+
- uv (Python package manager)
- A GGUF translation model

### Installation

```bash
# Install dependencies
uv pip install -e .

# Download a translation model
mkdir -p storage/models
huggingface-cli download tencent/HY-MT1.5-1.8B-GGUF HY-MT1.5-1.8B-Q4_K_M.gguf --local-dir storage/models

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Update models.yaml with the correct model path

# Run the server
python main.py
```

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# Simple translation
curl -X POST http://localhost:8000/v1/translate \
  -H "Authorization: Bearer test_key_1" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "source_lang": "en", "target_lang": "zh"}'

# Chat completions (OpenAI-compatible)
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer test_key_1" \
  -H "Content-Type: application/json" \
  -d '{"model": "hy-mt-general", "messages": [{"role": "user", "content": "Translate to Chinese: Hello world"}]}'
```

## Docker Deployment

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d
```

## API Endpoints

### GET /health

Health check (no authentication required).

```json
{"status": "healthy", "models_loaded": 1, "uptime_seconds": 3600.5}
```

### GET /v1/models

List available models.

### POST /v1/translate

Translation-specific endpoint with advanced features.

| Field | Type | Required | Description |
|---|---|---|---|
| text | string | yes | Text to translate |
| source_lang | string | yes | Source language code (e.g., `en`, `zh`) |
| target_lang | string | yes | Target language code |
| model | string | no | Model name (uses default if omitted) |
| terminology | object | no | Custom terminology mapping `{"source": "target"}` |
| context | string | no | Additional context for translation |
| preserve_format | bool | no | Preserve text formatting (default: false) |
| stream | bool | no | Enable SSE streaming (default: false) |

### POST /v1/chat/completions

OpenAI-compatible chat completions. Works with the OpenAI Python SDK:

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="test_key_1")
response = client.chat.completions.create(
    model="hy-mt-general",
    messages=[{"role": "user", "content": "Translate to Chinese: Hello world"}],
)
print(response.choices[0].message.content)
```

## Configuration

### Environment Variables (.env)

| Variable | Default | Description |
|---|---|---|
| API_KEYS | test_key_1,... | Comma-separated API keys |
| DEFAULT_MODEL | hy-mt-general | Default model name |
| FALLBACK_MODEL | hy-mt-general | Fallback model name |
| RATE_LIMIT_REQUESTS_PER_MINUTE | 60 | Rate limit per API key |
| MODEL_STORAGE_PATH | ./storage/models | Model files directory |
| MODELS_CONFIG_PATH | ./models.yaml | Model configuration file |
| HOST | 0.0.0.0 | Server host |
| PORT | 8000 | Server port |
| LOG_LEVEL | INFO | Logging level |

### Model Configuration (models.yaml)

```yaml
default_model: "hy-mt-general"
fallback_model: "hy-mt-general"

models:
  - name: "hy-mt-general"
    path: "./storage/models/Hy-MT1.5-1.8B-Q4_K_M.gguf"
    description: "General purpose translation model"
    parameters:
      n_ctx: 4096           # Context window size
      n_gpu_layers: 0       # GPU layers (0=CPU, -1=all GPU)
      temperature: 0.7
      top_p: 0.6
      top_k: 20
      repeat_penalty: 1.05
      max_tokens: 2048
    supported_languages: [zh, en, fr, es, ja, ko, de, ru, ar, ...]
```

## Advanced Usage

### Terminology Injection

```bash
curl -X POST http://localhost:8000/v1/translate \
  -H "Authorization: Bearer test_key_1" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The API interface is working",
    "source_lang": "en", "target_lang": "zh",
    "terminology": {"API": "API", "interface": "接口"}
  }'
```

### Context-Aware Translation

```bash
curl -X POST http://localhost:8000/v1/translate \
  -H "Authorization: Bearer test_key_1" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Submit",
    "source_lang": "en", "target_lang": "zh",
    "context": "Button label in a web form"
  }'
```

### Streaming Translation

```bash
curl -N -X POST http://localhost:8000/v1/translate \
  -H "Authorization: Bearer test_key_1" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "source_lang": "en", "target_lang": "zh", "stream": true}'
```

## GPU Acceleration

```bash
# Install llama-cpp-python with CUDA
CMAKE_ARGS="-DGGML_CUDA=on" FORCE_CMAKE=1 pip install llama-cpp-python --force-reinstall --no-cache-dir

# Set n_gpu_layers: -1 in models.yaml
```

## Recommended Models

| Model | Size | Quality | Link |
|---|---|---|---|
| HY-MT1.5-1.8B-Q4_K_M | ~1.1GB | Best balance | [tencent/HY-MT1.5-1.8B-GGUF](https://huggingface.co/tencent/HY-MT1.5-1.8B-GGUF) |
| HY-MT1.5-1.8B-Q8_0 | ~1.9GB | Higher quality | [tencent/HY-MT1.5-1.8B-GGUF](https://huggingface.co/tencent/HY-MT1.5-1.8B-GGUF) |
| Hy-MT1.5-1.8B-2bit | ~574MB | Ultra compact | [AngelSlim/Hy-MT1.5-1.8B-2bit](https://huggingface.co/AngelSlim/Hy-MT1.5-1.8B-2bit) |
| Hy-MT1.5-1.8B-1.25bit | ~440MB | Smallest | [AngelSlim/Hy-MT1.5-1.8B-1.25bit](https://huggingface.co/AngelSlim/Hy-MT1.5-1.8B-1.25bit) |

## Project Structure

```
TransLlama/
├── api/routes/            # API endpoint implementations
├── services/              # Model manager, translation service, prompt builder
├── models/                # Pydantic request/response schemas
├── core/                  # Config, auth, rate limiting, middleware
├── storage/models/        # GGUF model files (gitignored)
├── main.py               # Application entry point
├── models.yaml           # Model configuration
├── Dockerfile            # Container image
└── docker-compose.yml    # Container orchestration
```

## License

MIT
