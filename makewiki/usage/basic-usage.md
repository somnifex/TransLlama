# Basic Usage

## Authentication

All endpoints except `/health` require a Bearer token:

```
Authorization: Bearer YOUR_API_KEY
```

API keys are set in `.env` via the `API_KEYS` variable.

## Web UI

Open http://localhost:8000/ in your browser. The interface provides:

- Side-by-side source and target panels
- Language selector for 38 languages with a swap button
- Auto-translate after 600ms of inactivity
- Streaming output (tokens appear as generated)
- Custom terminology editor
- Ctrl+Enter to manually trigger translation

## Translation Endpoint

### POST /v1/translate

```bash
curl -X POST http://localhost:8000/v1/translate \
  -H "Authorization: Bearer test_key_1" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "source_lang": "en", "target_lang": "zh"}'
```

Response:

```json
{
  "translation": "你好世界",
  "source_lang": "en",
  "target_lang": "zh",
  "model": "hy-mt-general",
  "usage": {"characters": 11, "prompt_tokens": 42, "completion_tokens": 5}
}
```

### Request Parameters

| Field             | Type   | Required | Default       | Description                         |
| ----------------- | ------ | -------- | ------------- | ----------------------------------- |
| `text`            | string | Yes      | —             | Text to translate                   |
| `source_lang`     | string | Yes      | —             | Source language code                |
| `target_lang`     | string | Yes      | —             | Target language code                |
| `model`           | string | No       | default model | Model to use                        |
| `terminology`     | object | No       | null          | Term mapping `{"source": "target"}` |
| `context`         | string | No       | null          | Context to improve accuracy         |
| `preserve_format` | bool   | No       | false         | Preserve Markdown/HTML formatting   |
| `stream`          | bool   | No       | false         | Enable SSE streaming                |

### Terminology Injection

Force specific terms to be translated a certain way:

```bash
curl -X POST http://localhost:8000/v1/translate \
  -H "Authorization: Bearer test_key_1" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The API interface returns a response",
    "source_lang": "en",
    "target_lang": "zh",
    "terminology": {"API": "API", "interface": "接口", "response": "响应"}
  }'
```

### Context-Aware Translation

Provide context to disambiguate meaning:

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

### Streaming

```bash
curl -N -X POST http://localhost:8000/v1/translate \
  -H "Authorization: Bearer test_key_1" \
  -H "Content-Type: application/json" \
  -d '{"text": "Long text here...", "source_lang": "en", "target_lang": "zh", "stream": true}'
```

Streaming response (SSE):

```
data: {"text": "长"}
data: {"text": "文本"}
data: [DONE]
```

## OpenAI-Compatible Chat Endpoint

### POST /v1/chat/completions

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer test_key_1" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "hy-mt-general",
    "messages": [{"role": "user", "content": "Translate to English: 你好世界"}]
  }'
```

### Using the OpenAI Python SDK

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="test_key_1",
)

response = client.chat.completions.create(
    model="hy-mt-general",
    messages=[
        {"role": "user", "content": "将以下文本翻译为英语，注意只需要输出翻译后的结果，不要额外解释：\n你好世界"}
    ],
)
print(response.choices[0].message.content)
```

### Using requests

```python
import requests

resp = requests.post(
    "http://localhost:8000/v1/translate",
    headers={"Authorization": "Bearer test_key_1"},
    json={"text": "Hello world", "source_lang": "en", "target_lang": "zh"},
)
print(resp.json()["translation"])
```

## Other Endpoints

### GET /health

No authentication required. Returns server status:

```json
{"status": "healthy", "models_loaded": 1, "uptime_seconds": 3600.5}
```

### GET /v1/models

Lists all configured models:

```json
{
  "object": "list",
  "data": [{"id": "hy-mt-general", "object": "model", "created": 1715100000, "owned_by": "transllama"}]
}
```

## Supported Languages

38 languages are supported. Use these codes for `source_lang` and `target_lang`:

`zh`, `en`, `fr`, `pt`, `es`, `ja`, `tr`, `ru`, `ar`, `ko`, `th`, `it`, `de`, `vi`, `ms`, `id`, `tl`, `hi`, `zh-Hant`, `pl`, `cs`, `nl`, `km`, `my`, `fa`, `gu`, `ur`, `te`, `mr`, `he`, `bn`, `ta`, `uk`, `bo`, `kk`, `mn`, `ug`, `yue`

---

[Back to README](README.md) | [Configuration](configuration.md) | [简体中文](usage/basic-usage.zh-CN.md)
