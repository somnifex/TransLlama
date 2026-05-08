# 安装部署

## 标准安装

```bash
git clone <repository-url>
cd TransLlama
uv pip install -e .
```

如果没有 `uv`，可用 pip：

```bash
pip install -e .
```

## 下载模型

将 GGUF 模型文件下载到 `storage/models/` 目录：

```bash
huggingface-cli download tencent/HY-MT1.5-1.8B-GGUF \
  HY-MT1.5-1.8B-Q4_K_M.gguf \
  --local-dir storage/models
```

可选量化版本：

| 模型                   | 大小     | 质量        |
| -------------------- | ------ | --------- |
| HY-MT1.5-1.8B-Q4_K_M | 1.1 GB | 速度与质量最佳平衡 |
| HY-MT1.5-1.8B-Q6_K   | 1.4 GB | 更高质量      |
| HY-MT1.5-1.8B-Q8_0   | 1.8 GB | 接近全精度     |

## Docker 部署

### docker-compose（推荐）

确保模型已下载且 `.env` 已配置：

```bash
docker-compose up --build
```

后台运行：

```bash
docker-compose up -d
```

查看日志：

```bash
docker-compose logs -f transllama
```

### 独立 Docker

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

容器暴露 8000 端口，已配置健康检查。

## GPU 加速

默认使用 CPU 运行。启用 GPU 方法：

### NVIDIA CUDA

```bash
CMAKE_ARGS="-DGGML_CUDA=on" FORCE_CMAKE=1 \
  pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
```

然后在 `models.yaml` 中设置 `n_gpu_layers: -1`（全部 GPU）或指定层数（部分卸载）。

### Vulkan（跨平台）

```bash
CMAKE_ARGS="-DGGML_VULKAN=on" FORCE_CMAKE=1 \
  pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
```

## 开发模式

```bash
uv pip install -e ".[dev]"
uvicorn main:app --reload
```

---

[返回首页](README.zh-CN.md) | [配置说明](configuration.zh-CN.md) | [English](installation.md)
