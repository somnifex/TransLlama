# 快速入门

TransLlama 使用本地 GGUF 模型在 38 种语言之间进行翻译。你可以通过 REST API 或内置 Web 界面使用它。

## 环境要求

- Python 3.12 或更高版本
- [uv](https://github.com/astral-sh/uv)（推荐）或 pip
- 约 1.1 GB 磁盘空间（默认 Q4_K_M 模型）
- 运行时约 2-4 GB 内存

## 安装

```bash
git clone <repository-url>
cd TransLlama
uv pip install -e .
```

## 下载模型

```bash
huggingface-cli download tencent/HY-MT1.5-1.8B-GGUF \
  HY-MT1.5-1.8B-Q4_K_M.gguf \
  --local-dir storage/models
```

也可以用 Python 脚本下载：

```python
from huggingface_hub import hf_hub_download
hf_hub_download(
    repo_id="tencent/HY-MT1.5-1.8B-GGUF",
    filename="HY-MT1.5-1.8B-Q4_K_M.gguf",
    local_dir="storage/models"
)
```

## 配置

```bash
cp .env.example .env
```

编辑 `.env` 设置 API Key。默认的 Key（`test_key_1`、`test_key_2`、`test_key_3`）可用于本地测试。

## 启动

```bash
python main.py
```

## 验证

```bash
curl http://localhost:8000/health
```

预期响应：

```json
{"status": "healthy", "models_loaded": 0, "uptime_seconds": 5.2}
```

模型在首次翻译请求时延迟加载，因此 `models_loaded` 初始为 0。

## 第一次翻译

```bash
curl -X POST http://localhost:8000/v1/translate \
  -H "Authorization: Bearer test_key_1" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "source_lang": "en", "target_lang": "zh"}'
```

首次请求因模型加载会较慢，后续请求速度正常。

---

[返回首页](README.zh-CN.md) | [安装部署](installation.zh-CN.md) | [配置说明](configuration.zh-CN.md) | [English](getting-started.md)
