# Getting Started

TransLlama translates text between 38 languages using a local GGUF model. You interact with it through a REST API or a built-in web interface.

## Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- ~1.1 GB disk space for the default Q4_K_M model
- ~2-4 GB RAM at runtime

## Install

```bash
git clone <repository-url>
cd TransLlama
uv pip install -e .
```

## Download the Model

```bash
huggingface-cli download tencent/HY-MT1.5-1.8B-GGUF \
  HY-MT1.5-1.8B-Q4_K_M.gguf \
  --local-dir storage/models
```

Alternatively, use Python:

```python
from huggingface_hub import hf_hub_download
hf_hub_download(
    repo_id="tencent/HY-MT1.5-1.8B-GGUF",
    filename="HY-MT1.5-1.8B-Q4_K_M.gguf",
    local_dir="storage/models"
)
```

## Configure

```bash
cp .env.example .env
```

Edit `.env` to set your API keys. The default keys (`test_key_1`, `test_key_2`, `test_key_3`) work for local testing.

## Run

```bash
python main.py
```

## Verify

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status": "healthy", "models_loaded": 0, "uptime_seconds": 5.2}
```

The model loads on first translation request (lazy loading), so `models_loaded` starts at 0.

## First Translation

```bash
curl -X POST http://localhost:8000/v1/translate \
  -H "Authorization: Bearer test_key_1" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "source_lang": "en", "target_lang": "zh"}'
```

The first request takes longer as the model loads into memory. Subsequent requests are fast.

---

[Back to README](README.md) | [Installation details](installation.md) | [Configuration](configuration.md) | [简体中文](getting-started.zh-CN.md)
