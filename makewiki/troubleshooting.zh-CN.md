# 故障排除

## 模型文件未找到

**错误：** `Model file not found: ./storage/models/HY-MT1.5-1.8B-Q4_K_M.gguf`

**原因：** GGUF 模型文件未下载。

**解决：** 下载模型：

```bash
huggingface-cli download tencent/HY-MT1.5-1.8B-GGUF \
  HY-MT1.5-1.8B-Q4_K_M.gguf \
  --local-dir storage/models
```

## 401 未授权

**错误：** `{"error": "Unauthorized", "detail": "Invalid or missing API key"}`

**原因：** 请求缺少 `Authorization` 头，或使用的 Key 不在 `API_KEYS` 列表中。

**解决：** 请求头中加入 `Authorization: Bearer <key>`，Key 需为 `.env` 文件 `API_KEYS` 中配置的值。

## 429 请求过多

**错误：** 频率限制超限响应。

**原因：** 同一 Key 在一分钟内请求次数超过 `RATE_LIMIT_REQUESTS_PER_MINUTE` 设定值。

**解决：** 等待后重试，或在 `.env` 中增大限制值。

## 不支持的语言

**错误：** `Source language 'xx' is not supported. Supported languages: zh, en, fr, ...`

**原因：** 使用的语言代码不在模型 `supported_languages` 列表中。

**解决：** 使用 38 种支持的语言代码之一。完整列表见[使用指南](usage/basic-usage.zh-CN.md)。

## 首次请求很慢

**原因：** 模型在首次使用时才加载到内存（延迟加载）。Q4_K_M 模型在 CPU 上加载需要几秒钟。

**解决：** 这是正常现象，后续请求会很快。如需预热模型，启动后发送一个短文本翻译请求即可。

---

[返回首页](README.zh-CN.md) | [常见问题](faq.zh-CN.md) | [English](troubleshooting.md)
