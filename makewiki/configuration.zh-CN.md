# 配置说明

TransLlama 通过两个配置源进行设置：环境变量（`.env`）和模型配置文件（`models.yaml`）。

## 环境变量（.env）

复制模板并编辑：

```bash
cp .env.example .env
```

| 变量                               | 默认值                                | 说明                                         |
| -------------------------------- | ---------------------------------- | ------------------------------------------ |
| `API_KEYS`                       | `test_key_1,test_key_2,test_key_3` | API Key 列表，逗号分隔，用于 Bearer Token 认证         |
| `DEFAULT_MODEL`                  | `hy-mt-general`                    | 请求未指定模型时使用的默认模型                            |
| `FALLBACK_MODEL`                 | `hy-mt-general`                    | 默认模型加载失败时的备选模型                             |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | `60`                               | 每个 API Key 每分钟最大请求数                        |
| `MODEL_STORAGE_PATH`             | `./storage/models`                 | GGUF 模型文件所在目录                              |
| `MODELS_CONFIG_PATH`             | `./models.yaml`                    | 模型配置文件路径                                   |
| `HOST`                           | `0.0.0.0`                          | 服务监听地址                                     |
| `PORT`                           | `8000`                             | 服务监听端口                                     |
| `WORKERS`                        | `1`                                | Uvicorn Worker 数量（建议保持 1，每个 Worker 独立加载模型） |
| `LOG_LEVEL`                      | `INFO`                             | 日志级别：DEBUG、INFO、WARNING、ERROR              |

## 模型配置（models.yaml）

定义可用模型及推理参数：

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
      # ...（共 38 种）
```

### 模型参数说明

| 参数               | 默认值    | 说明                            |
| ---------------- | ------ | ----------------------------- |
| `n_ctx`          | `4096` | 上下文窗口大小，最小 2048，越大占用内存越多      |
| `n_gpu_layers`   | `0`    | GPU 层卸载。0 = 纯 CPU，-1 = 全部 GPU |
| `temperature`    | `0.7`  | 采样温度，越低越确定性                   |
| `top_p`          | `0.6`  | 核采样阈值                         |
| `top_k`          | `20`   | Top-K 采样                      |
| `repeat_penalty` | `1.05` | 重复惩罚系数                        |
| `max_tokens`     | `2048` | 每次请求最大输出 token 数              |

### 多模型配置

可以配置多个模型用于不同场景：

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

在请求中通过 `model` 字段指定模型：

```json
{"text": "Hello", "source_lang": "en", "target_lang": "zh", "model": "hy-mt-q8"}
```

---

[返回首页](README.zh-CN.md) | [使用指南](usage/basic-usage.zh-CN.md) | [English](configuration.md)
