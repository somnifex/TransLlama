# Installation

## Standard Installation

```bash
git clone <repository-url>
cd TransLlama
uv pip install -e .
```

If you don't have `uv`, use pip:

```bash
pip install -e .
```

## Model Download

Download at least one GGUF model file to `storage/models/`:

```bash
huggingface-cli download tencent/HY-MT1.5-1.8B-GGUF \
  HY-MT1.5-1.8B-Q4_K_M.gguf \
  --local-dir storage/models
```

Available quantizations:

| Model                | Size   | Quality                    |
| -------------------- | ------ | -------------------------- |
| HY-MT1.5-1.8B-Q4_K_M | 1.1 GB | Best speed/quality balance |
| HY-MT1.5-1.8B-Q6_K   | 1.4 GB | Higher quality             |
| HY-MT1.5-1.8B-Q8_0   | 1.8 GB | Near full precision        |

## Docker Deployment

### docker-compose (recommended)

Ensure the model is downloaded and `.env` is configured, then:

```bash
docker-compose up --build
```

Run in background:

```bash
docker-compose up -d
```

View logs:

```bash
docker-compose logs -f transllama
```

### Standalone Docker

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

The container exposes port 8000 and has a health check configured.

## GPU Acceleration

By default, TransLlama runs on CPU. To enable GPU:

### NVIDIA CUDA

```bash
CMAKE_ARGS="-DGGML_CUDA=on" FORCE_CMAKE=1 \
  pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
```

Then set `n_gpu_layers: -1` in `models.yaml` for full GPU offload, or a specific number for partial offload.

### Vulkan (cross-platform)

```bash
CMAKE_ARGS="-DGGML_VULKAN=on" FORCE_CMAKE=1 \
  pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
```

## Development Mode

```bash
uv pip install -e ".[dev]"
uvicorn main:app --reload
```

---

[Back to README](README.md) | [Configuration](configuration.md) | [简体中文](installation.zh-CN.md)
