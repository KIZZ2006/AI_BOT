import requests
import json
import os
import time

# OPENROUTER SETTINGS
OPENROUTER_KEYS = [
    "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",
    "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",
    "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"
]

FREE_MODELS = [
    "google/gemini-2.0-flash-exp:free",
    "deepseek/deepseek-r1:free",
    "mistralai/mistral-7b-instruct:free",
    "google/gemini-flash-1.5:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "microsoft/phi-3-mini-128k-instruct:free",
    "openchat/openchat-7b:free",
    "qwen/qwen-2-7b-instruct:free"
]

TEST_PROMPT = """
You are a Senior NLP Content Engineer and Viral Growth Strategist.
Generate a JSON object for a 45-second YouTube Shorts script about: 'The Future of AI in 2026'.
The script must use a 'Negative Hook' (e.g., 'Stop doing X') and include 'Power Words' in [BRACKETS].

Return ONLY JSON like this:
{
    "title": "Shocking AI Reveal 🛑",
    "script": "STOP ignoring what's coming. [REVEAL]...",
    "hook_score": 95,
    "pacing": "Fast"
}
"""

def benchmark_models():
    results = {}
    print("🚀 Starting OpenRouter Free Model Benchmark...")
    print(f"📡 Testing {len(FREE_MODELS)} models...\n")

    for model in FREE_MODELS:
        print(f"🤖 Testing Model: {model}")
        success = False
        
        # Try keys until one works (rate limiting)
        for key in OPENROUTER_KEYS:
            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://localhost",
                "X-Title": "AI Benchmark Tool"
            }
            
            try:
                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    data=json.dumps({
                        "model": model,
                        "messages": [{"role": "user", "content": TEST_PROMPT}],
                        "response_format": { "type": "json_object" }
                    }),
                    timeout=20
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data['choices'][0]['message']['content']
                    try:
                        parsed = json.loads(content)
                        results[model] = {
                            "status": "✅ SUCCESS",
                            "hook": parsed.get("title", "No Title"),
                            "length": len(parsed.get("script", "")),
                            "pacing": parsed.get("pacing", "Unknown")
                        }
                    except:
                        results[model] = {"status": "⚠️ INVALID JSON", "raw": content[:50]}
                    success = True
                    break
                elif response.status_code == 429:
                    continue # Try next key
                else:
                    print(f"   ❌ Failed with code: {response.status_code}")
                    results[model] = {"status": f"❌ ERROR {response.status_code}"}
                    break
            except Exception as e:
                print(f"   ❌ Exception: {str(e)[:50]}")
                results[model] = {"status": "❌ TIMEOUT/CRASH"}
                break
        
        if not success:
            print(f"   🛑 All keys failed for {model}")
            results[model] = {"status": "🛑 ALL KEYS RATE LIMITED"}
        
        time.sleep(1) # Tiny delay for stability

    print("\n" + "="*50)
    print("📊 BENCHMARK RESULTS SUMMARY")
    print("="*50)
    for model, data in results.items():
        print(f"Model: {model}")
        print(f"Status: {data['status']}")
        if "hook" in data:
            print(f"Result: {data['hook']} | Length: {data['length']} chars")
        print("-" * 30)

    # Save to file
    with open("outputs/model_benchmark.json", "w") as f:
        json.dump(results, f, indent=4)
    print(f"\n✅ Full report saved to outputs/model_benchmark.json")

if __name__ == "__main__":
    benchmark_models()
