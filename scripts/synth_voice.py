import asyncio
import edge_tts
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

def get_path(rel_path):
    return os.path.join(ROOT_DIR, rel_path.replace("/", os.sep))

# Configuration: Premium Neutral Voices for 2026
MALE_VOICE = "en-US-BrianNeural" # More popular, less 'AI' sounding
FEMALE_VOICE = "en-US-EmmaNeural"   # Warmer and more natural female voice
OUTPUT_FILE = get_path("outputs/voice.mp3")

async def generate_voice():
    # 1. Load Metadata
    host = "Daniel"
    text = "Hello, this is a test."
    
    meta_path = get_path("outputs/metadata.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            host = data.get("host", "Daniel")
            text = data.get("script", text)
    
    # Selection based on host
    voice = FEMALE_VOICE if host == "Sarah" else MALE_VOICE
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Process text for Shorts energy
    # remove markings like [POP] for the audio
    clean_text = text.replace("[POP]", "").replace("[WHOOSH]", "").replace("...", " . ")
    
    print(f"🎙️ Synthesizing Voice for {host}: {voice}")
    # Rate +5% is the sweet spot for retention vs naturalness
    communicate = edge_tts.Communicate(clean_text, voice, rate="+5%", pitch="-2Hz") 
    await communicate.save(OUTPUT_FILE)
    print(f"✅ Voice generated at {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(generate_voice())
