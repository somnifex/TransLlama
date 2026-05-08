# Troubleshooting

## Model file not found

**Error:** `Model file not found: ./storage/models/HY-MT1.5-1.8B-Q4_K_M.gguf`

**Cause:** The GGUF model has not been downloaded.

**Fix:** Download the model:

```bash
huggingface-cli download tencent/HY-MT1.5-1.8B-GGUF \
  HY-MT1.5-1.8B-Q4_K_M.gguf \
  --local-dir storage/models
```

## 401 Unauthorized

**Error:** `{"error": "Unauthorized", "detail": "Invalid or missing API key"}`

**Cause:** The `Authorization` header is missing or the key is not in the `API_KEYS` list.

**Fix:** Include the header `Authorization: Bearer <key>` using a key from your `.env` file's `API_KEYS` value.

## 429 Too Many Requests

**Error:** Rate limit exceeded response.

**Cause:** More than `RATE_LIMIT_REQUESTS_PER_MINUTE` requests from the same key within one minute.

**Fix:** Wait and retry, or increase the limit in `.env`.

## Unsupported language error

**Error:** `Source language 'xx' is not supported. Supported languages: zh, en, fr, ...`

**Cause:** The language code is not in the model's `supported_languages` list.

**Fix:** Use one of the 38 supported language codes. See [Basic Usage](usage/basic-usage.md) for the full list.

## First request is very slow

**Cause:** The model loads into memory on first use (lazy loading). The Q4_K_M model takes a few seconds to load on CPU.

**Fix:** This is expected. Subsequent requests will be fast. If you want to pre-warm the model, send a short translation request after startup.

---

[Back to README](README.md) | [FAQ](faq.md) | [简体中文](troubleshooting.zh-CN.md)
