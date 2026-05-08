# 常见问题

## TransLlama 需要多少内存？

Q4_K_M 模型运行时约占 1.5-2 GB 内存，Q8_0 模型约 2.5-3 GB。docker-compose 默认限制容器内存为 4 GB。

## 可以同时运行多个模型吗？

可以。在 `models.yaml` 中配置多个模型条目，请求时通过 `model` 字段指定。每个已加载的模型独立占用内存，请确保有足够的 RAM。

## 模型是启动时加载的吗？

不是。模型在首次使用时延迟加载。首次翻译请求会较慢（需要加载模型），但服务启动速度快。

## 可以用 OpenAI SDK 调用吗？

可以。将 SDK 的 `base_url` 设置为 `http://localhost:8000/v1`，`api_key` 设置为你配置的 Key 即可。`/v1/chat/completions` 接口与 OpenAI 格式兼容。

---

[返回首页](README.zh-CN.md) | [故障排除](troubleshooting.zh-CN.md) | [English](faq.md)
