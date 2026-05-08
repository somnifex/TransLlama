# FAQ

## How much RAM does TransLlama need?

The Q4_K_M model uses approximately 1.5-2 GB of RAM at runtime. The Q8_0 model uses approximately 2.5-3 GB. The container is limited to 4 GB by default in docker-compose.

## Can I run multiple models simultaneously?

Yes. Configure multiple entries in `models.yaml` and specify the model per request. Each loaded model occupies memory independently, so ensure you have enough RAM.

## Does the model load at startup?

No. Models load lazily on the first request that uses them. This means the first translation takes longer (model loading) but startup is fast.

## Can I use this with the OpenAI Python/Node SDK?

Yes. Point the SDK's `base_url` to `http://localhost:8000/v1` and set `api_key` to one of your configured keys. The `/v1/chat/completions` endpoint is compatible.

---

[Back to README](README.md) | [Troubleshooting](troubleshooting.md) | [简体中文](faq.zh-CN.md)
