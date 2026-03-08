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
# In Colab/Linux, use: os.environ['OPENROUTER_API_KEY']
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

if not OPENROUTER_API_KEY:
    # Fallback to local check for debugging only
    print("⚠️ Warning: OPENROUTER_API_KEY not found in environment.")
else:
    print(f"🔐 API Key detected from Environment: {OPENROUTER_API_KEY[:8]}...****")

def get_live_news():
    print("🌐 [Research Agent] Scouring TechCrunch & The Verge for breakthroughs...")
    urls = [
        "https://feeds.feedburner.com/TechCrunch/",
        "https://www.theverge.com/rss/index.xml"
    ]
    research_summary = []
    
    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.content, 'xml')
            items = soup.find_all('item')[:5] # Get top 5 from each
            for item in items:
                title = item.title.text
                desc = item.description.text if item.description else ""
                # Clean html tags from description
                desc = re.sub('<[^<]+?>', '', desc)[:200]
                research_summary.append(f"- {title}: {desc}")
        except Exception as e:
            print(f"⚠️ Research failed for {url}: {e}")
            
    return "\n".join(research_summary) if research_summary else "No live news found (using general AI knowledge)."

def fetch_content_and_vibe():
    # 0. PERSISTENT HOST TRACKING
    last_host_path = get_path("temp/last_host.txt")
    current_host = "Daniel"
    
    if os.path.exists(last_host_path):
        with open(last_host_path, "r") as f:
            last_host = f.read().strip()
            current_host = "Sarah" if last_host == "Daniel" else "Daniel"
    
    with open(last_host_path, "w") as f:
        f.write(current_host)

    # 1. LIVE DEEP RESEARCH
    research_data_raw = get_live_news()
    
    # 2. FILTER RECENTLY USED
    used_news_path = get_path("temp/used_news.txt")
    used_titles = []
    if os.path.exists(used_news_path):
        with open(used_news_path, "r", encoding="utf-8") as f:
            used_titles = [line.strip() for line in f.readlines()]
            
    filtered_news = []
    for item in research_data_raw.split("- "):
        if not item.strip(): continue
        title = item.split(":")[0].strip()
        if title not in used_titles:
            filtered_news.append(item)
            
    if not filtered_news:
        print("⚠️ All recent news items already used! Clearing cache to reuse oldest.")
        with open(used_news_path, "w") as f: f.write("") # Clear cache
        filtered_news = research_data_raw.split("- ")
        
    research_data = "\n- ".join(filtered_news)
    print(f"📄 Found {len(filtered_news)} new items. Host for this run: {current_host}")

    # SISINTY-STYLE NLP PROMPT: The Viral Gatekeeper + Metadata Engineer (US TARGETING - LONG FORM)
    prompt = f"""
    You are a Senior NLP Content Engineer and US-Market Viral Strategist.
    
    STEP 1: USA AUDIENCE VIRALITY ANALYSIS
    Analyze these news items: {json.dumps(research_data.splitlines())}
    Pick the item with the highest retention potential for a USA/Western audience.
    
    STEP 2: VAIBHAV 3.0 AUTHORITY SCRIPTING
    Write a 55-second script (approx. 150-160 words).
    Structure:
    - [HOOK]: Start with a "POV" or "Massive Claim" (e.g. "Adobe Photoshop just became FREE...").
    - [BODY]: Focus on tool demos and screenshots. Use transition markers [POP] and [WHOOSH].
    - [POWER WORDS]: Use words like SCAM, SECRET, FREE, and HACK to trigger high-impact highlights.
    - [INFINITE LOOP]: Transition seamlessly back to the opening hook.
    
    STEP 3: METADATA ENGINEERING (US-TRENDING)
    Generate "Curiosity Gap" metadata.
    - Title: High-CTR (e.g. "DON'T Use ChatGPT in the US! 🇺🇸"). Must be < 100 chars.
    - Description: Start with a cliffhanger. Include: "Watch until the end to see how this affects you."
    
    Return ONLY JSON:
    {{
        "source_title": "TITLE_OF_THE_NEWS_ITEM_PICKED",
        "title": "Shocking Title 🛑",
        "script": "Full spoken script...",
        "description": "High-retention description...",
        "marketing_comment": "Viral pinned comment with a question + CTA...",
        "host": "{current_host}",
        "vibe": "Energetic",
        "b_roll_query": "General theme",
        "visual_bumps": ["Logo for X", "Screenshot of Y"]
    }}
    """
    
    url = "https://openrouter.ai/api/v1/chat/completions"

    # API Authentication check
    if not OPENROUTER_API_KEY:
        raise Exception("❌ ERROR: OPENROUTER_API_KEY environment variable not set. Add it to Colab Secrets or your System Environment.")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost",
        "X-Title": "AI View Machine"
    }
        
    for model in FREE_MODELS:
        try:
            print(f"🚀 Prompting {model}...")
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "response_format": { "type": "json_object" }
            }
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                raw_text = result['choices'][0]['message']['content'].strip()
                # Clean markdown and common AI noise
                raw_text = re.sub(r'```json|```', '', raw_text).strip()
                parsed = json.loads(raw_text)
                # Safety check
                if 'script' not in parsed:
                    print(f"⚠️ Model {model} gave incomplete JSON. Retrying...")
                    continue
                return parsed
            
            elif response.status_code == 400:
                print(f"⚠️ Model {model} failed (400). Retrying without JSON mode...")
                data.pop("response_format", None)
                response = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    raw_text = result['choices'][0]['message']['content'].strip()
                    raw_text = re.sub(r'```json|```', '', raw_text).strip()
                    json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                    if json_match:
                        parsed = json.loads(json_match.group())
                        return parsed
                    else:
                        print(f"⚠️ Model {model} responded but no JSON found.")
                        continue
                else:
                    print(f"⚠️ Model {model} still failed ({response.status_code}).")
                    continue
            
            elif response.status_code == 429:
                print(f"⚠️ Rate limited. Skipping model...")
                continue
            else:
                print(f"⚠️ Model {model} failed ({response.status_code}).")
                continue

        except Exception as e:
            print(f"❌ Detail Error: {e}")
            continue

    raise Exception("ALL MODELS FAILED. The system is overloaded.")

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


