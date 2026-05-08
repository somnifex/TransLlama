# TransLlama

TransLlama is a self-hosted translation API that runs local GGUF models. It provides an OpenAI-compatible chat endpoint, a dedicated translation endpoint with terminology injection and context awareness, and a built-in web translation interface. It supports 38 languages using the Tencent Hunyuan Hy-MT1.5 model.

## Quick Start

```bash
git clone <repository-url>
cd TransLlama
uv pip install -e .

# Download the model
huggingface-cli download tencent/HY-MT1.5-1.8B-GGUF \
  HY-MT1.5-1.8B-Q4_K_M.gguf \
  --local-dir storage/models

# Configure
cp .env.example .env

# Run
python main.py
```

After startup:
- Web UI: http://localhost:8000/
- API Docs (Swagger): http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Documentation

| Page                                  | Description                                         |
| ------------------------------------- | --------------------------------------------------- |
| [Getting Started](getting-started.md) | Prerequisites, installation, first run              |
| [Installation](installation.md)       | Detailed install instructions and Docker deployment |
| [Configuration](configuration.md)     | Environment variables and model configuration       |
| [Basic Usage](usage/basic-usage.md)   | API endpoints, Web UI, and code examples            |
| [FAQ](faq.md)                         | Common questions                                    |
| [Troubleshooting](troubleshooting.md) | Error messages and fixes                            |

**其他语言 / Other Languages:** [简体中文](README.zh-CN.md)
