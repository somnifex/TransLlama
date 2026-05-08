# 使用指南

## 认证

除 `/health` 外，所有接口均需 Bearer Token 认证：

```
Authorization: Bearer YOUR_API_KEY
```

API Key 通过 `.env` 文件中的 `API_KEYS` 变量配置。

## Web 翻译界面

在浏览器中打开 http://localhost:8000/ ，界面功能包括：

- 左右双栏源文与译文
- 38 种语言选择器，带交换按钮
- 输入后 600ms 自动翻译
- 流式逐字显示翻译结果
- 自定义术语表编辑器
- Ctrl+Enter 手动触发翻译

## 翻译接口

### POST /v1/translate

```bash
curl -X POST http://localhost:8000/v1/translate \
  -H "Authorization: Bearer test_key_1" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "source_lang": "en", "target_lang": "zh"}'
```

响应：

```json
{
  "translation": "你好世界",
  "source_lang": "en",
  "target_lang": "zh",
  "model": "hy-mt-general",
  "usage": {"characters": 11, "prompt_tokens": 42, "completion_tokens": 5}
}
```

### 请求参数

| 字段                | 类型     | 必填 | 默认值   | 说明                  |
| ----------------- | ------ | -- | ----- | ------------------- |
| `text`            | string | 是  | —     | 待翻译文本               |
| `source_lang`     | string | 是  | —     | 源语言代码               |
| `target_lang`     | string | 是  | —     | 目标语言代码              |
| `model`           | string | 否  | 默认模型  | 指定模型                |
| `terminology`     | object | 否  | null  | 术语映射 `{"原文": "译文"}` |
| `context`         | string | 否  | null  | 上下文信息               |
| `preserve_format` | bool   | 否  | false | 保持 Markdown/HTML 格式 |
| `stream`          | bool   | 否  | false | 启用 SSE 流式输出         |

### 术语注入

指定术语的翻译方式，确保专业术语一致：

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

### 上下文翻译

提供上下文帮助消歧：

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

### 流式翻译

```bash
curl -N -X POST http://localhost:8000/v1/translate \
  -H "Authorization: Bearer test_key_1" \
  -H "Content-Type: application/json" \
  -d '{"text": "Long text here...", "source_lang": "en", "target_lang": "zh", "stream": true}'
```

流式响应（SSE）：

```
data: {"text": "长"}
data: {"text": "文本"}
data: [DONE]
```

## OpenAI 兼容聊天接口

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

### 使用 OpenAI Python SDK

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

### 使用 requests 库

```python
import requests

resp = requests.post(
    "http://localhost:8000/v1/translate",
    headers={"Authorization": "Bearer test_key_1"},
    json={"text": "Hello world", "source_lang": "en", "target_lang": "zh"},
)
print(resp.json()["translation"])
```

## 其他接口

### GET /health

无需认证，返回服务状态：

```json
{"status": "healthy", "models_loaded": 1, "uptime_seconds": 3600.5}
```

### GET /v1/models

列出所有已配置的模型：

```json
{
  "object": "list",
  "data": [{"id": "hy-mt-general", "object": "model", "created": 1715100000, "owned_by": "transllama"}]
}
```

## 支持的语言

共支持 38 种语言，`source_lang` 和 `target_lang` 使用以下代码：

`zh`、`en`、`fr`、`pt`、`es`、`ja`、`tr`、`ru`、`ar`、`ko`、`th`、`it`、`de`、`vi`、`ms`、`id`、`tl`、`hi`、`zh-Hant`、`pl`、`cs`、`nl`、`km`、`my`、`fa`、`gu`、`ur`、`te`、`mr`、`he`、`bn`、`ta`、`uk`、`bo`、`kk`、`mn`、`ug`、`yue`

---

[返回首页](README.zh-CN.md) | [配置说明](configuration.zh-CN.md) | [English](usage/basic-usage.md)
