import os
import json
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor

FFMPEG_EXE = r"D:\tools\ffmpeg\bin\ffmpeg.exe"

def get_path(rel_path):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root, rel_path.replace("/", os.sep))

def download_single_bump(args):
    i, query, visuals_dir = args
    output_file = os.path.join(visuals_dir, f"bump_{i}.mp4")
    search_query = f"ytsearch1:{query} high quality"
    
    print(f"   [Core {i}] Downloading: {query}")
    
    try:
        cmd = [
            sys.executable, "-m", "yt_dlp",
            "--ffmpeg-location", FFMPEG_EXE,
            "-f", "best[ext=mp4]/best",
            "--match-filter", "duration < 300",
            "--no-playlist",
            "--extractor-args", "youtube:player_client=android,web",
            "--max-downloads", "1",
            "-N", "2",
            "--output", output_file,
            search_query
        ]
        subprocess.run(cmd, capture_output=True, text=True)
        
        # Cleanup
        for waste in [output_file + ".part", output_file + ".ytdl"]:
            if os.path.exists(waste):
                try: os.remove(waste)
                except: pass

        if os.path.exists(output_file) and os.path.getsize(output_file) > 1000:
            temp_trim = output_file.replace(".mp4", "_trimmed.mp4")
            trim_cmd = [
                FFMPEG_EXE, "-y", "-i", output_file, 
                "-threads", "1", # Use 1 core per trim since we run 4 trims in parallel
                "-ss", "0", "-t", "5", 
                "-c", "copy", temp_trim
            ]
            subprocess.run(trim_cmd, capture_output=True)
            if os.path.exists(temp_trim):
                os.replace(temp_trim, output_file)
            return True
    except Exception as e:
        print(f"   ⚠️ Core {i} failed: {e}")
    return False

def fetch_visuals():
    metadata_path = get_path("outputs/metadata.json")
    visuals_dir = get_path("outputs/visual_bumps")
    
    if os.path.exists(visuals_dir):
        import shutil
        shutil.rmtree(visuals_dir)
    os.makedirs(visuals_dir, exist_ok=True)
    
    if not os.path.exists(metadata_path):
        return

    with open(metadata_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        bumps = data.get("visual_bumps", [])

    print(f"🖼️ [Multiprocessing] Spawning 4 cores for {len(bumps)} visual tasks...")

    tasks = []
    for i, q in enumerate(bumps[:4]):
        tasks.append((i, q, visuals_dir))

    with ProcessPoolExecutor(max_workers=4) as executor:
        list(executor.map(download_single_bump, tasks))

if __name__ == "__main__":
    fetch_visuals()
