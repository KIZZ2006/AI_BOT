import os
import json
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

def get_path(rel_path):
    return os.path.join(ROOT_DIR, rel_path.replace("/", os.sep))

def fetch_broll():
    metadata_path = get_path("outputs/metadata.json")
    output_broll = get_path("outputs/b_roll.mp4")
    
    # 1. Load Query
    query = "AI technology futuristic"
    if os.path.exists(metadata_path):
        with open(metadata_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            query = data.get("b_roll_query", query)
    
    print(f"🔍 [B-Roll Agent] Searching for relevant visuals: {query}")
    
    # 2. Use YT-DLP to find a short, high-quality video
    # We search for "4k b-roll [query]" to get high quality
    search_query = f"ytsearch1:4k b-roll {query}"
    
    import shutil
    # DYNAMIC FFMPEG LOOKUP (Windows vs Linux)
    FFMPEG_EXE = shutil.which("ffmpeg") or "ffmpeg"
    if os.name == 'nt' and os.path.exists(r"D:\tools\ffmpeg\bin\ffmpeg.exe"):
        FFMPEG_EXE = r"D:\tools\ffmpeg\bin\ffmpeg.exe"
    
    try:
        # Download the best video under 60 seconds
        # Using sys.executable -m yt_dlp is the most robust way to call it on Windows
        cmd = [
            sys.executable, "-m", "yt_dlp",
            "--ffmpeg-location", FFMPEG_EXE,
            "-f", "best[ext=mp4]/best", # Force mp4 for reliability
            "--match-filter", "duration < 60",
            "--no-playlist",
            "--extractor-args", "youtube:player_client=android,web",
            "--max-downloads", "1",
            "-N", "4", # Use 4 threads for faster download
            "--output", output_broll,
            search_query
        ]
        
        print("📥 Downloading cinematic B-roll clip...")
        # yt-dlp returns 101 when --max-downloads is reached, which is success for us
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Cleanup potential waste files left by yt-dlp
        for waste in [output_broll + ".part", output_broll + ".ytdl"]:
            if os.path.exists(waste):
                try: os.remove(waste)
                except: pass

        if result.returncode not in [0, 101]:
            print(f"⚠️ yt-dlp warning (Code {result.returncode}): {result.stderr[:200]}")
        
        if os.path.exists(output_broll) and os.path.getsize(output_broll) > 1000:
            print(f"✅ B-Roll downloaded successfully: {output_broll}")
        else:
            print("⚠️ B-Roll file empty or missing. Using safety background.")

            
    except Exception as e:
        print(f"❌ Error fetching B-Roll: {e}")
        # Fallback is handled by the main assembly script

if __name__ == "__main__":
    fetch_broll()
