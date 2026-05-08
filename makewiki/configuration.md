# Configuration

TransLlama uses two configuration sources: environment variables (`.env`) and a model configuration file (`models.yaml`).

## Environment Variables (.env)

Copy `.env.example` to `.env` and edit as needed:

```bash
cp .env.example .env
```

| Variable                         | Default                            | Description                                                               |
| -------------------------------- | ---------------------------------- | ------------------------------------------------------------------------- |
| `API_KEYS`                       | `test_key_1,test_key_2,test_key_3` | Comma-separated API keys for Bearer token auth                            |
| `DEFAULT_MODEL`                  | `hy-mt-general`                    | Model used when requests don't specify one                                |
| `FALLBACK_MODEL`                 | `hy-mt-general`                    | Model used when the default fails to load                                 |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | `60`                               | Max requests per API key per minute                                       |
| `MODEL_STORAGE_PATH`             | `./storage/models`                 | Directory containing GGUF model files                                     |
| `MODELS_CONFIG_PATH`             | `./models.yaml`                    | Path to model configuration file                                          |
| `HOST`                           | `0.0.0.0`                          | Server bind address                                                       |
| `PORT`                           | `8000`                             | Server port                                                               |
| `WORKERS`                        | `1`                                | Uvicorn worker count (keep at 1 — each worker loads the model separately) |
| `LOG_LEVEL`                      | `INFO`                             | Log level: DEBUG, INFO, WARNING, ERROR                                    |

## Model Configuration (models.yaml)

Defines which models are available and their inference parameters:

```yaml
default_model: "hy-mt-general"
fallback_model: "hy-mt-general"

models:
  - name: "hy-mt-general"
    path: "./storage/models/HY-MT1.5-1.8B-Q4_K_M.gguf"
    description: "General purpose translation model (Hy-MT1.5-1.8B Q4_K_M)"
    parameters:
      n_ctx: 4096
      n_gpu_layers: 0
      temperature: 0.7
      top_p: 0.6
      top_k: 20
      repeat_penalty: 1.05
      max_tokens: 2048
    supported_languages:
      - zh
      - en
      - ja
      # ... (38 total)
```

### Model Parameters

| Parameter        | Default | Description                                                    |
| ---------------- | ------- | -------------------------------------------------------------- |
| `n_ctx`          | `4096`  | Context window size. Minimum 2048. Larger values use more RAM. |
| `n_gpu_layers`   | `0`     | GPU layer offload. 0 = CPU only, -1 = all layers on GPU.       |
| `temperature`    | `0.7`   | Sampling temperature. Lower = more deterministic.              |
| `top_p`          | `0.6`   | Nucleus sampling threshold.                                    |
| `top_k`          | `20`    | Top-K sampling.                                                |
| `repeat_penalty` | `1.05`  | Penalizes repeated tokens.                                     |
| `max_tokens`     | `2048`  | Maximum output tokens per request.                             |

### Multiple Models

You can configure multiple models for different quality/speed tradeoffs:

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

Specify a model per request by setting the `model` field:

```json
{"text": "Hello", "source_lang": "en", "target_lang": "zh", "model": "hy-mt-q8"}
```

---

[Back to README](README.md) | [Basic Usage](usage/basic-usage.md) | [简体中文](configuration.zh-CN.md)
