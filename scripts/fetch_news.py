import requests
import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

def get_path(rel_path):
    return os.path.join(ROOT_DIR, rel_path.replace("/", os.sep))

from bs4 import BeautifulSoup

# BEST FREE MODELS ON OPENROUTER (Verified High-Performance - 2026)
FREE_MODELS = [
    "google/gemma-3-27b-it:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "google/gemma-3-12b-it:free",
    "google/gemma-3-4b-it:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "liquid/lfm-2.5-1.2b-instruct:free",
    "liquid/lfm-2.5-1.2b-thinking:free",
    "arcee-ai/trinity-mini:free",
    "qwen/qwen3-coder:free",
    "upstage/solar-pro-3:free"
]




# SECURITY: API Keys are now loaded from Environment Variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()

# FALLBACK CONTENT (If API is overloaded/fails)
FAIL_SAFE_CONTENT = {
    "source_title": "Safety News: AI Breakthroughs",
    "title": "The AI Revolution is Here! 🚀",
    "script": "POV: You're living in 2026 and AI just changed everything. [POP] From autonomous agents to real-time translation, the world is moving faster than ever. [WHOOSH] Did you know that the most successful creators are now using AI to automate 90% of their work? It's not just a trend, it's the new reality. Watch until the end to see the secret tool everyone is talking about. [WHOOSH] Tag a friend who needs to see this hack!",
    "description": "The future of AI is closer than you think. #AI #Tech #Future",
    "marketing_comment": "Which AI tool are you using the most right now? Let us know below! 👇",
    "host": "Daniel",
    "vibe": "Energetic",
    "b_roll_query": "AI technology futuristic matrix",
    "visual_bumps": ["Logo for OpenAI", "AI brain glowing"]
}

if not OPENROUTER_API_KEY:
    print("⚠️ Warning: OPENROUTER_API_KEY not found in environment.")
else:
    print(f"🔐 API Key detected and stripped: {OPENROUTER_API_KEY[:8]}...")

def get_live_news():
    print("🌐 [Research Agent] Scouring TechCrunch & The Verge...")
    urls = ["https://feeds.feedburner.com/TechCrunch/", "https://www.theverge.com/rss/index.xml"]
    research_summary = []
    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.content, 'xml')
            for item in soup.find_all('item')[:5]:
                title = item.title.text
                desc = item.description.text if item.description else ""
                desc = re.sub('<[^<]+?>', '', desc)[:200]
                research_summary.append(f"- {title}: {desc}")
        except Exception as e: print(f"⚠️ Research failed for {url}: {e}")
    return "\n".join(research_summary)

def fetch_content_and_vibe():
    last_host_path = get_path("temp/last_host.txt")
    current_host = "Daniel"
    if os.path.exists(last_host_path):
        with open(last_host_path, "r") as f:
            last_host = f.read().strip()
            current_host = "Sarah" if last_host == "Daniel" else "Daniel"
    with open(last_host_path, "w") as f: f.write(current_host)

    research_data = get_live_news()
    if not research_data: research_data = "Trending AI news and future technology."
    
    # Prompt for Viral Content
    prompt = f"Write a viral 55-second AI news script about: {research_data[:1000]}. Return ONLY JSON with keys: title, script, description, source_title, marketing_comment, b_roll_query, visual_bumps."
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost",
        "X-Title": "AI View Machine"
    }

    if not OPENROUTER_API_KEY:
        print("❌ No API Key. Using Fail-Safe Content.")
        FAIL_SAFE_CONTENT["host"] = current_host
        return FAIL_SAFE_CONTENT

    for model in FREE_MODELS:
        try:
            print(f"🚀 Prompting {model}...")
            data = {"model": model, "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
            
            if response.status_code == 200:
                parsed = response.json()
                raw_text = parsed['choices'][0]['message']['content'].strip()
                return json.loads(re.sub(r'```json|```', '', raw_text).strip())
            else:
                print(f"⚠️ Model {model} failed ({response.status_code}). Response: {response.text[:100]}")
                continue
        except Exception as e:
            print(f"❌ Error with {model}: {e}")
            continue

    print("🚨 ALL MODELS FAILED. Using Fail-Safe Content to keep the pipeline moving...")
    FAIL_SAFE_CONTENT["host"] = current_host
    return FAIL_SAFE_CONTENT

if __name__ == "__main__":
    try:
        data = fetch_content_and_vibe()
        out_dir = get_path("outputs")
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"✅ Content Ready. Host: {data.get('host')}")
    except Exception as e:
        print(f"❌ Critical Error: {e}")

if __name__ == "__main__":
    try:
        data = fetch_content_and_vibe()
        # Save results...
        out_dir = get_path("outputs")
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        with open(os.path.join(out_dir, "quote.txt"), "w", encoding="utf-8") as f:
            f.write(data.get('script', 'No script generated.'))
            
        print(f"✅ Content fetched using Free AI Models. Host: {data.get('host', 'Unknown')}.")
        
        # Track the news item used to avoid duplicates
        used_news_path = get_path("temp/used_news.txt")
        source_title = data.get("source_title")
        if source_title:
            with open(used_news_path, "a", encoding="utf-8") as f:
                f.write(source_title + "\n")
            print(f"📖 Marked as used: {source_title}")
    except Exception as e:
        print(f"❌ Error: {e}")


