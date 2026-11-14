import requests
import json
import sys

API_KEY = "YOUR_CLAUDE_API_KEY"

url = "https://api.anthropic.com/v1/messages"

headers = {
    "x-api-key": API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}

payload = {
    "model": "claude-sonnet-4-0",
    "max_tokens": 50,
    "messages": [
        {
            "role": "user",
            "content": "Reply with only the word: SUCCESS"
        }
    ]
}

try:
    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("✅ API Key is valid!")

        if "content" in data:
            print("Claude Response:")
            for item in data["content"]:
                if item.get("type") == "text":
                    print(item["text"])

    elif response.status_code == 401:
        print("❌ Invalid API Key")

    else:
        print("❌ Request failed")
        print(json.dumps(response.json(), indent=2))

except requests.exceptions.RequestException as e:
    print(f"❌ Connection error: {e}")
    sys.exit(1)