#!/bin/bash

# TransLlama API Test Examples
# Make sure to replace 'test_key_1' with your actual API key

API_URL="http://localhost:8000"
API_KEY="test_key_1"

echo "=== TransLlama API Test Examples ==="
echo ""

# 1. Health Check
echo "1. Health Check"
curl -s "$API_URL/health" | jq .
echo -e "\n"

# 2. List Models
echo "2. List Models"
curl -s "$API_URL/v1/models" \
  -H "Authorization: Bearer $API_KEY" | jq .
echo -e "\n"

# 3. Simple Translation
echo "3. Simple Translation (English to Chinese)"
curl -s -X POST "$API_URL/v1/translate" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world",
    "source_lang": "en",
    "target_lang": "zh"
  }' | jq .
echo -e "\n"

# 4. Translation with Terminology
echo "4. Translation with Terminology"
curl -s -X POST "$API_URL/v1/translate" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The API interface is working perfectly",
    "source_lang": "en",
    "target_lang": "zh",
    "terminology": {
      "API": "API",
      "interface": "接口"
    }
  }' | jq .
echo -e "\n"

# 5. Translation with Context
echo "5. Translation with Context"
curl -s -X POST "$API_URL/v1/translate" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Click the Submit button",
    "source_lang": "en",
    "target_lang": "zh",
    "context": "UI button label in a web form"
  }' | jq .
echo -e "\n"

# 6. Streaming Translation
echo "6. Streaming Translation"
curl -N -X POST "$API_URL/v1/translate" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is a longer text that will be translated in streaming mode.",
    "source_lang": "en",
    "target_lang": "zh",
    "stream": true
  }'
echo -e "\n"

# 7. Chat Completions (OpenAI-compatible)
echo "7. Chat Completions"
curl -s -X POST "$API_URL/v1/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "hy-mt-general",
    "messages": [
      {"role": "user", "content": "Translate to Chinese: Good morning"}
    ]
  }' | jq .
echo -e "\n"

# 8. Streaming Chat Completions
echo "8. Streaming Chat Completions"
curl -N -X POST "$API_URL/v1/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "hy-mt-general",
    "messages": [
      {"role": "user", "content": "Translate to French: Hello, how are you?"}
    ],
    "stream": true
  }'
echo -e "\n"

# 9. Translation with Format Preservation
echo "9. Translation with Format Preservation"
curl -s -X POST "$API_URL/v1/translate" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Click the **Submit** button to continue.",
    "source_lang": "en",
    "target_lang": "zh",
    "preserve_format": true
  }' | jq .
echo -e "\n"

echo "=== All tests completed ==="
