import requests
import json
import os

# TEST CONFIGURATION
TEST_API_KEY = "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"

FREE_MODELS = [
    "google/gemma-3-27b-it:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "google/gemma-3-12b-it:free",
    "google/gemma-3-4b-it:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "liquid/lfm-2.5-1.2b-instruct:free",
    "qwen/qwen3-coder:free",
    "upstage/solar-pro-3:free"
]

def test_key_and_models():
    print(f"🔑 Testing API Key: {TEST_API_KEY[:10]}...")
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {TEST_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost",
        "X-Title": "AI View Machine Test"
    }

    results = []

    for model in FREE_MODELS:
        print(f"📡 Testing model: {model}...", end=" ", flush=True)
        try:
            data = {
                "model": model,
                "messages": [{"role": "user", "content": "Say 'OK' if you are working."}],
                "max_tokens": 10
            }
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=15)
            
            if response.status_code == 200:
                print("✅ PASSED")
                results.append((model, "Success"))
            else:
                print(f"❌ FAILED ({response.status_code})")
                results.append((model, f"Error {response.status_code}"))
        except Exception as e:
            print(f"⚠️ ERROR ({str(e)})")
            results.append((model, "Exception"))

    print("\n" + "="*40)
    print("📊 FINAL TEST RESULTS:")
    print("="*40)
    for model, status in results:
        print(f"{model:<50} | {status}")
    print("="*40)

if __name__ == "__main__":
    test_key_and_models()
