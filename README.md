# TransLlama

<p align="center">
  <strong>🦙 基于本地 GGUF 模型的自托管翻译 API 与 Web 界面</strong>
</p>

<p align="center">
  <a href="README_EN.md">English Documentation</a>
</p>

TransLlama 是一个基于 FastAPI 和 llama-cpp-python 的自托管翻译 API 后端。它使用本地 GGUF 模型提供 OpenAI 兼容接口和翻译专用接口，并内置 Web 翻译界面，支持 38 种语言的互译。

---

## 功能特性

- **OpenAI 兼容接口** — `/v1/chat/completions`，可直接对接 OpenAI SDK / 任何兼容客户端
- **翻译专用接口** — `/v1/translate`，支持术语表注入、上下文翻译、格式保持
- **Web 翻译界面** — 内置类 Google Translate 风格网页界面，访问 `/` 即用
- **多模型管理** — 通过 `models.yaml` 配置多个模型，支持默认模型与 fallback 自动切换
- **流式输出** — 两个接口及 Web 界面均支持 SSE 流式响应
- **API Key 鉴权** — Bearer Token 认证，支持多 Key 配置
- **基础限流** — 基于内存的 Per-Key 请求频率限制
- **38 种语言** — 基于腾讯混元 Hy-MT1.5 翻译模型，支持中、英、日、韩、法、德、俄等 38 种语言互译
- **Docker 部署** — 提供 Dockerfile 和 docker-compose.yml，开箱即用

---

## 支持的语言

| 语言 | 代码 | 语言 | 代码 | 语言 | 代码 |
|------|------|------|------|------|------|
| 简体中文 | `zh` | 英语 | `en` | 法语 | `fr` |
| 葡萄牙语 | `pt` | 西班牙语 | `es` | 日语 | `ja` |
| 土耳其语 | `tr` | 俄语 | `ru` | 阿拉伯语 | `ar` |
| 韩语 | `ko` | 泰语 | `th` | 意大利语 | `it` |
| 德语 | `de` | 越南语 | `vi` | 马来语 | `ms` |
| 印尼语 | `id` | 菲律宾语 | `tl` | 印地语 | `hi` |
| 繁体中文 | `zh-Hant` | 波兰语 | `pl` | 捷克语 | `cs` |
| 荷兰语 | `nl` | 高棉语 | `km` | 缅甸语 | `my` |
| 波斯语 | `fa` | 古吉拉特语 | `gu` | 乌尔都语 | `ur` |
| 泰卢固语 | `te` | 马拉地语 | `mr` | 希伯来语 | `he` |
| 孟加拉语 | `bn` | 泰米尔语 | `ta` | 乌克兰语 | `uk` |
| 藏语 | `bo` | 哈萨克语 | `kk` | 蒙古语 | `mn` |
| 维吾尔语 | `ug` | 粤语 | `yue` | | |

---

## 快速开始

### 环境要求

- Python 3.12+
- pip 或 [uv](https://github.com/astral-sh/uv)

### 安装

```bash
git clone <repository-url>
cd TransLlama

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# 安装基础依赖
pip install -r requirements.txt

# 或安装开发依赖（含测试工具）
pip install -r requirements-dev.txt
```

> **如需 GPU 加速**，请先按下方 [硬件加速](#硬件加速) 章节安装对应后端的 `llama-cpp-python`，再安装其他依赖。

### 下载模型

推荐使用腾讯官方 GGUF 量化版本：

```bash
# 方式一：huggingface-cli
huggingface-cli download tencent/HY-MT1.5-1.8B-GGUF \
  HY-MT1.5-1.8B-Q4_K_M.gguf \
  --local-dir storage/models

# 方式二：Python 脚本
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

### 配置

```bash
cp .env.example .env
# 编辑 .env，设置你的 API Key
# API_KEYS=your_secret_key_1,your_secret_key_2
```

`models.yaml` 默认指向 `./storage/models/HY-MT1.5-1.8B-Q4_K_M.gguf`，如果下载了其他版本需修改 `path` 字段。

### 启动服务

```bash
# 直接启动
python main.py

# 开发模式（热重载）
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

启动后可访问：
- **Web 翻译界面**：http://localhost:8000/
- **API 文档 (Swagger)**：http://localhost:8000/docs
- **健康检查**：http://localhost:8000/health

### 快速测试

```bash
# 健康检查（无需认证）
curl http://localhost:8000/health

# 中译英
curl -X POST http://localhost:8000/v1/translate \
  -H "Authorization: Bearer test_key_1" \
  -H "Content-Type: application/json" \
  -d '{"text": "人工智能正在改变世界", "source_lang": "zh", "target_lang": "en"}'

# 英译中
curl -X POST http://localhost:8000/v1/translate \
  -H "Authorization: Bearer test_key_1" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "source_lang": "en", "target_lang": "zh"}'
```

---

## Web 翻译界面

TransLlama 内置了一个类似 Google 翻译的 Web 界面，访问根路径 `/` 即可使用。

**功能：**
- 左右双栏源文与译文
- 38 种语言选择 + 交换按钮
- 输入后自动翻译（600ms 防抖）
- 流式逐字显示
- 自定义术语表编辑器
- 复制、清除、字符计数
- Ctrl+Enter 手动触发翻译
- 移动端自适应布局

无需额外构建工具 — 由 FastAPI 直接提供的单文件 HTML。

---

## API 接口文档

### 认证方式

除 `/health` 外，所有接口均需通过 API Key 认证：

```
Authorization: Bearer YOUR_API_KEY
```

API Key 在 `.env` 文件的 `API_KEYS` 中配置，多个 Key 用逗号分隔。

---

### GET /health

健康检查，无需认证。

**响应：**
```json
{
  "status": "healthy",
  "models_loaded": 1,
  "uptime_seconds": 3600.5
}
```

---

### GET /v1/models

列出所有可用模型。

**响应：**
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

翻译专用接口，支持术语表、上下文、格式保持等高级功能。

**请求参数：**

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `text` | string | 是 | — | 待翻译文本 |
| `source_lang` | string | 是 | — | 源语言代码，如 `en`、`zh`、`ja` |
| `target_lang` | string | 是 | — | 目标语言代码 |
| `model` | string | 否 | 默认模型 | 指定使用的模型名称 |
| `terminology` | object | 否 | `null` | 术语表映射，如 `{"API": "接口"}` |
| `context` | string | 否 | `null` | 上下文信息，帮助提高翻译质量 |
| `preserve_format` | bool | 否 | `false` | 是否保持原文格式标记 |
| `stream` | bool | 否 | `false` | 是否启用 SSE 流式输出 |

**请求示例：**
```json
{
  "text": "Hello world",
  "source_lang": "en",
  "target_lang": "zh",
  "terminology": {"world": "世界"},
  "context": "技术文档标题"
}
```

**响应：**
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

**流式响应（`stream: true`）：**
```
data: {"text": "你好"}

data: {"text": "世界"}

data: [DONE]
```

---

### POST /v1/chat/completions

OpenAI 兼容聊天补全接口，可直接用 OpenAI SDK 或任何兼容客户端调用。

**请求参数：**

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `model` | string | 否 | 默认模型 | 模型名称 |
| `messages` | array | 是 | — | 消息列表，格式 `[{"role": "user", "content": "..."}]` |
| `temperature` | float | 否 | 0.7 | 采样温度 (0.0-2.0) |
| `top_p` | float | 否 | 0.6 | 核采样概率 (0.0-1.0) |
| `top_k` | int | 否 | 20 | Top-K 采样 |
| `max_tokens` | int | 否 | 2048 | 最大生成 token 数 |
| `stream` | bool | 否 | `false` | 是否启用 SSE 流式输出 |

**请求示例：**
```json
{
  "model": "hy-mt-general",
  "messages": [
    {"role": "user", "content": "将以下文本翻译为英语，注意只需要输出翻译后的结果，不要额外解释：\n你好世界"}
  ]
}
```

**响应：**
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

**流式响应（`stream: true`）：**
```
data: {"id":"chatcmpl-a1b2c3d4","object":"chat.completion.chunk","created":1715100000,"model":"hy-mt-general","choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}

data: {"id":"chatcmpl-a1b2c3d4","object":"chat.completion.chunk","created":1715100000,"model":"hy-mt-general","choices":[{"index":0,"delta":{"content":" World"},"finish_reason":null}]}

data: {"id":"chatcmpl-a1b2c3d4","object":"chat.completion.chunk","created":1715100000,"model":"hy-mt-general","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

---

## 高级用法

### 术语表注入

指定术语翻译方式，确保专业术语一致性：

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

### 上下文翻译

提供上下文信息，帮助模型理解语境产生更准确的翻译：

```bash
curl -X POST http://localhost:8000/v1/translate \
  -H "Authorization: Bearer test_key_1" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Submit",
    "source_lang": "en",
    "target_lang": "zh",
    "context": "网页表单中的按钮标签"
  }'
```

### 格式保持翻译

保留原文中的 Markdown 标记、HTML 标签等格式元素：

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

### 流式翻译

适用于长文本翻译，逐步返回翻译结果：

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

### 使用 OpenAI Python SDK

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="test_key_1",
)

# 同步调用
response = client.chat.completions.create(
    model="hy-mt-general",
    messages=[
        {"role": "user", "content": "将以下文本翻译为英语，注意只需要输出翻译后的结果，不要额外解释：\n你好世界"}
    ],
)
print(response.choices[0].message.content)

# 流式调用
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

### 使用 requests 库

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

## 配置说明

### 环境变量 (.env)

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `API_KEYS` | `test_key_1,test_key_2,test_key_3` | API Key 列表，逗号分隔 |
| `DEFAULT_MODEL` | `hy-mt-general` | 默认使用的模型名称 |
| `FALLBACK_MODEL` | `hy-mt-general` | 默认模型不可用时的备选模型 |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | `60` | 每个 API Key 每分钟最大请求数 |
| `MODEL_STORAGE_PATH` | `./storage/models` | 模型文件存储目录 |
| `MODELS_CONFIG_PATH` | `./models.yaml` | 模型配置文件路径 |
| `HOST` | `0.0.0.0` | 服务监听地址 |
| `PORT` | `8000` | 服务监听端口 |
| `WORKERS` | `1` | Uvicorn worker 数量 |
| `LOG_LEVEL` | `INFO` | 日志级别 |

### 模型配置 (models.yaml)

```yaml
default_model: "hy-mt-general"       # 默认模型
fallback_model: "hy-mt-general"      # 备选模型

models:
  - name: "hy-mt-general"            # API 中的模型标识
    path: "./storage/models/HY-MT1.5-1.8B-Q4_K_M.gguf"
    description: "General purpose translation model (Hy-MT1.5-1.8B)"
    parameters:
      n_ctx: 4096                    # 上下文窗口（不低于 2048）
      n_gpu_layers: 0                # GPU 层：0=CPU，-1=全部 GPU
      temperature: 0.7               # 采样温度
      top_p: 0.6                     # 核采样
      top_k: 20                      # Top-K
      repeat_penalty: 1.05           # 重复惩罚
      max_tokens: 2048               # 最大输出 token
    supported_languages:             # 支持的语言列表
      - zh
      - en
      - ja
      # ... 完整列表见 models.yaml
```

**多模型配置示例：**

```yaml
default_model: "hy-mt-q4"
fallback_model: "hy-mt-q8"

models:
  - name: "hy-mt-q4"
    path: "./storage/models/HY-MT1.5-1.8B-Q4_K_M.gguf"
    description: "快速翻译 (Q4 量化)"
    parameters: { n_ctx: 4096, n_gpu_layers: 0, temperature: 0.7, top_p: 0.6, top_k: 20, repeat_penalty: 1.05, max_tokens: 2048 }
    supported_languages: [zh, en, ja, ko, fr, de]

  - name: "hy-mt-q8"
    path: "./storage/models/HY-MT1.5-1.8B-Q8_0.gguf"
    description: "高质量翻译 (Q8 量化)"
    parameters: { n_ctx: 4096, n_gpu_layers: -1, temperature: 0.7, top_p: 0.6, top_k: 20, repeat_penalty: 1.05, max_tokens: 2048 }
    supported_languages: [zh, en, ja, ko, fr, de]
```

请求时通过 `model` 字段指定：
```json
{"text": "Hello", "source_lang": "en", "target_lang": "zh", "model": "hy-mt-q8"}
```

---

## Docker 部署

### docker-compose（推荐）

```bash
# 确保模型已下载到 storage/models/ 且 .env 已配置

docker-compose up --build        # 构建并启动
docker-compose up -d             # 后台运行
docker-compose logs -f transllama  # 查看日志
docker-compose down              # 停止
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

---

## 硬件加速

安装 `llama-cpp-python` 时通过 `CMAKE_ARGS` 环境变量选择后端。安装完成后在 `models.yaml` 中设置 `n_gpu_layers` 来控制 GPU 卸载层数（`-1` = 全部，`0` = 纯 CPU）。

### CUDA（NVIDIA）

```bash
# 从源码编译
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
```

也可直接使用预编译 wheel（支持 CUDA 12.1–12.5、Python 3.10–3.12）：

```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
# 可选 cu122 / cu123 / cu124 / cu125
```

### Metal（Apple Silicon / macOS）

```bash
CMAKE_ARGS="-DGGML_METAL=on" pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
```

预编译 wheel（macOS 11.0+、Python 3.10–3.12）：

```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/metal
```

> 如果 M 系列芯片编译报错，使用：
> `CMAKE_ARGS="-DCMAKE_OSX_ARCHITECTURES=arm64 -DCMAKE_APPLE_SILICON_PROCESSOR=arm64 -DGGML_METAL=on"`

### ROCm / hipBLAS（AMD）

```bash
CMAKE_ARGS="-DGGML_HIPBLAS=on" pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
```

### Vulkan（跨平台，支持 NVIDIA / AMD / Intel）

```bash
CMAKE_ARGS="-DGGML_VULKAN=on" pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
```

### SYCL（Intel GPU / oneAPI）

```bash
# 需先加载 oneAPI 环境
source /opt/intel/oneapi/setvars.sh

CMAKE_ARGS="-DGGML_SYCL=on -DCMAKE_C_COMPILER=icx -DCMAKE_CXX_COMPILER=icpx" \
  pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
```

### OpenBLAS（CPU 加速）

```bash
CMAKE_ARGS="-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS" \
  pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
```

### RPC（分布式推理）

```bash
CMAKE_ARGS="-DGGML_RPC=on" pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
```

### 纯 CPU 预编译 wheel

```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

### Windows 注意事项

如果 CMake 找不到编译器，需额外设置：

```powershell
$env:CMAKE_GENERATOR = "MinGW Makefiles"
```

### 安装后配置

在 `models.yaml` 中调整 GPU 卸载层数：

```yaml
parameters:
  n_gpu_layers: -1    # 全部卸载到 GPU
  n_gpu_layers: 20    # 部分卸载（显存不足时）
  n_gpu_layers: 0     # 纯 CPU（默认）
```

---

## 推荐模型

| 模型 | 大小 | 量化 | 说明 | 链接 |
|------|------|------|------|------|
| HY-MT1.5-1.8B-Q4_K_M | 1.1 GB | Q4_K_M | 速度与质量最佳平衡 | [tencent/HY-MT1.5-1.8B-GGUF](https://huggingface.co/tencent/HY-MT1.5-1.8B-GGUF) |
| HY-MT1.5-1.8B-Q6_K | 1.4 GB | Q6_K | 更高质量 | [tencent/HY-MT1.5-1.8B-GGUF](https://huggingface.co/tencent/HY-MT1.5-1.8B-GGUF) |
| HY-MT1.5-1.8B-Q8_0 | 1.8 GB | Q8_0 | 接近全精度 | [tencent/HY-MT1.5-1.8B-GGUF](https://huggingface.co/tencent/HY-MT1.5-1.8B-GGUF) |

> **注意：** [AngelSlim](https://huggingface.co/AngelSlim) 提供的 1.25-bit/2-bit 超压缩版本使用了自定义量化内核 (SEQ/STQ)，标准 llama-cpp-python 尚不支持。

---

## 项目结构

```
TransLlama/
├── api/                           # API 层
│   ├── routes/                    # 路由
│   │   ├── chat.py                #   /v1/chat/completions
│   │   ├── translate.py           #   /v1/translate
│   │   ├── models.py              #   /v1/models
│   │   └── health.py              #   /health
│   └── dependencies.py            # 认证 + 限流依赖注入
├── services/                      # 服务层
│   ├── model_manager.py           # 模型加载、缓存、路由、fallback
│   ├── translation_service.py     # 翻译编排、ChatML 模板、流式输出
│   └── prompt_builder.py          # Hy-MT1.5 提示词工程
├── models/                        # 数据模型
│   ├── requests.py                # 请求 Schema
│   ├── responses.py               # 响应 Schema
│   └── config.py                  # 配置 Schema
├── core/                          # 基础设施
│   ├── config.py                  # pydantic-settings 配置管理
│   ├── auth.py                    # API Key 认证
│   ├── rate_limit.py              # 内存限流
│   ├── middleware.py              # CORS、日志、错误处理中间件
│   └── exceptions.py              # 自定义异常
├── static/                        # Web 界面
│   └── index.html                 # 翻译网页
├── storage/models/                # GGUF 模型文件（已 gitignore）
├── main.py                        # 应用入口
├── models.yaml                    # 模型配置
├── pyproject.toml                 # 项目元数据
├── requirements.txt               # 运行依赖
├── requirements-dev.txt           # 开发依赖
├── .env.example                   # 环境变量模板
├── Dockerfile                     # 容器镜像
├── docker-compose.yml             # 容器编排
└── curl_examples.sh               # API 测试脚本
```

---

## 错误处理

所有错误返回统一 JSON 格式：

| HTTP 状态码 | 类型 | 说明 |
|-------------|------|------|
| 400 | `InvalidLanguageException` | 不支持的语言代码 |
| 401 | `Unauthorized` | API Key 无效或缺失 |
| 404 | `ModelNotFoundException` | 请求的模型不存在 |
| 429 | `Too Many Requests` | 请求频率超限 |
| 500 | `ModelLoadException` | 模型加载失败 |
| 500 | `TranslationException` | 翻译过程出错 |

**示例：**
```json
{
  "error": "Invalid language",
  "detail": "Source language 'xx' is not supported. Supported languages: zh, en, fr, ..."
}
```

---

## 开发

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest tests/

# 开发模式（热重载）
uvicorn main:app --reload
```

---

## 性能建议

1. **选择合适的量化版本** — Q4_K_M 是速度与质量的最佳平衡点
2. **启用 GPU 卸载** — 设置 `n_gpu_layers: -1` 可显著提升推理速度
3. **调整上下文窗口** — 短文本翻译可将 `n_ctx` 降到 2048 以节省内存
4. **使用流式输出** — 长文本翻译时启用 `stream: true` 改善用户体验
5. **模型懒加载** — 首次请求时才加载模型，避免启动时间过长

---

## 许可证

MIT License — 详见 [LICENSE](LICENSE)。

## 致谢

- [FastAPI](https://fastapi.tiangolo.com/) — 高性能 Python Web 框架
- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) — llama.cpp 的 Python 绑定
- [Hy-MT1.5](https://huggingface.co/tencent/HY-MT1.5-1.8B) — 腾讯混元翻译模型
- [AngelSlim](https://github.com/Tencent/AngelSlim) — 腾讯模型压缩工具
