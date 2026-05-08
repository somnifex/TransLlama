#!/bin/bash
# =============================================================================
# TransLlama API 测试脚本
# =============================================================================
#
# 用法：
#   chmod +x curl_examples.sh
#   ./curl_examples.sh
#
# 确保服务已启动：python main.py
# 默认地址：http://localhost:8000
# =============================================================================

API_URL="${TRANSLLAMA_URL:-http://localhost:8000}"
API_KEY="${TRANSLLAMA_KEY:-test_key_1}"
AUTH="Authorization: Bearer $API_KEY"
CT="Content-Type: application/json"

echo "TransLlama API Tests"
echo "Server: $API_URL"
echo "API Key: ${API_KEY:0:8}..."
echo "=========================================="
echo ""

# ---------- 1. 健康检查（无需认证） ----------
echo "1. GET /health"
curl -s "$API_URL/health" | python -m json.tool
echo -e "\n"

# ---------- 2. 模型列表 ----------
echo "2. GET /v1/models"
curl -s "$API_URL/v1/models" \
  -H "$AUTH" | python -m json.tool
echo -e "\n"

# ---------- 3. 基础翻译：英译中 ----------
echo "3. POST /v1/translate — English to Chinese"
curl -s -X POST "$API_URL/v1/translate" \
  -H "$AUTH" -H "$CT" \
  -d '{
    "text": "Artificial intelligence is transforming the world in unprecedented ways.",
    "source_lang": "en",
    "target_lang": "zh"
  }' | python -m json.tool
echo -e "\n"

# ---------- 4. 基础翻译：中译英 ----------
echo "4. POST /v1/translate — Chinese to English"
curl -s -X POST "$API_URL/v1/translate" \
  -H "$AUTH" -H "$CT" \
  -d '{
    "text": "人工智能正在以前所未有的方式改变世界。",
    "source_lang": "zh",
    "target_lang": "en"
  }' | python -m json.tool
echo -e "\n"

# ---------- 5. 术语表注入 ----------
echo "5. POST /v1/translate — With terminology"
curl -s -X POST "$API_URL/v1/translate" \
  -H "$AUTH" -H "$CT" \
  -d '{
    "text": "The API interface returns a response",
    "source_lang": "en",
    "target_lang": "zh",
    "terminology": {
      "API": "API",
      "interface": "接口",
      "response": "响应"
    }
  }' | python -m json.tool
echo -e "\n"

# ---------- 6. 上下文翻译 ----------
echo "6. POST /v1/translate — With context"
curl -s -X POST "$API_URL/v1/translate" \
  -H "$AUTH" -H "$CT" \
  -d '{
    "text": "Submit",
    "source_lang": "en",
    "target_lang": "zh",
    "context": "网页表单中的按钮标签"
  }' | python -m json.tool
echo -e "\n"

# ---------- 7. 格式保持翻译 ----------
echo "7. POST /v1/translate — Preserve format"
curl -s -X POST "$API_URL/v1/translate" \
  -H "$AUTH" -H "$CT" \
  -d '{
    "text": "Click the **Submit** button to continue.",
    "source_lang": "en",
    "target_lang": "zh",
    "preserve_format": true
  }' | python -m json.tool
echo -e "\n"

# ---------- 8. 英译日 ----------
echo "8. POST /v1/translate — English to Japanese"
curl -s -X POST "$API_URL/v1/translate" \
  -H "$AUTH" -H "$CT" \
  -d '{
    "text": "Good morning, how are you?",
    "source_lang": "en",
    "target_lang": "ja"
  }' | python -m json.tool
echo -e "\n"

# ---------- 9. 英译法 ----------
echo "9. POST /v1/translate — English to French"
curl -s -X POST "$API_URL/v1/translate" \
  -H "$AUTH" -H "$CT" \
  -d '{
    "text": "Good morning, how are you?",
    "source_lang": "en",
    "target_lang": "fr"
  }' | python -m json.tool
echo -e "\n"

# ---------- 10. 流式翻译 ----------
echo "10. POST /v1/translate — Streaming"
curl -N -X POST "$API_URL/v1/translate" \
  -H "$AUTH" -H "$CT" \
  -d '{
    "text": "Artificial intelligence is transforming the world in unprecedented ways.",
    "source_lang": "en",
    "target_lang": "zh",
    "stream": true
  }'
echo -e "\n\n"

# ---------- 11. Chat Completions（同步） ----------
echo "11. POST /v1/chat/completions — Sync"
curl -s -X POST "$API_URL/v1/chat/completions" \
  -H "$AUTH" -H "$CT" \
  -d '{
    "model": "hy-mt-general",
    "messages": [
      {
        "role": "user",
        "content": "将以下文本翻译为英语，注意只需要输出翻译后的结果，不要额外解释：\n人工智能正在改变世界。"
      }
    ]
  }' | python -m json.tool
echo -e "\n"

# ---------- 12. Chat Completions（流式） ----------
echo "12. POST /v1/chat/completions — Streaming"
curl -N -X POST "$API_URL/v1/chat/completions" \
  -H "$AUTH" -H "$CT" \
  -d '{
    "model": "hy-mt-general",
    "messages": [
      {
        "role": "user",
        "content": "Translate the following segment into French, without additional explanation.\n\nGood morning, how are you?"
      }
    ],
    "stream": true
  }'
echo -e "\n\n"

# ---------- 13. 认证失败测试 ----------
echo "13. Auth failure test (expect 401)"
curl -s -o /dev/null -w "HTTP %{http_code}" \
  "$API_URL/v1/models" \
  -H "Authorization: Bearer wrong_key"
echo -e "\n\n"

# ---------- 14. 无效语言测试 ----------
echo "14. Invalid language test (expect 400/500)"
curl -s -X POST "$API_URL/v1/translate" \
  -H "$AUTH" -H "$CT" \
  -d '{
    "text": "Hello",
    "source_lang": "xx",
    "target_lang": "zh"
  }' | python -m json.tool
echo -e "\n"

echo "=========================================="
echo "All tests completed."
