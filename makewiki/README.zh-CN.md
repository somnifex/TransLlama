# TransLlama

TransLlama 是一个自托管翻译 API 服务，使用本地 GGUF 模型运行。它提供 OpenAI 兼容的聊天接口、支持术语注入和上下文感知的翻译专用接口，以及内置的 Web 翻译界面。基于腾讯混元 Hy-MT1.5 模型，支持 38 种语言互译。

## 快速开始

```bash
git clone <repository-url>
cd TransLlama
uv pip install -e .

# 下载模型
huggingface-cli download tencent/HY-MT1.5-1.8B-GGUF \
  HY-MT1.5-1.8B-Q4_K_M.gguf \
  --local-dir storage/models

# 配置
cp .env.example .env

# 启动
python main.py
```

启动后访问：
- Web 翻译界面：http://localhost:8000/
- API 文档（Swagger）：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## 文档目录

| 页面                                 | 说明                  |
| ---------------------------------- | ------------------- |
| [快速入门](getting-started.zh-CN.md)   | 环境要求、安装、首次运行        |
| [安装部署](installation.zh-CN.md)      | 详细安装说明和 Docker 部署   |
| [配置说明](configuration.zh-CN.md)     | 环境变量和模型配置           |
| [使用指南](usage/basic-usage.zh-CN.md) | API 接口、Web UI 和代码示例 |
| [常见问题](faq.zh-CN.md)               | FAQ                 |
| [故障排除](troubleshooting.zh-CN.md)   | 错误信息和解决方法           |

**Other Languages:** [English](README.md)
