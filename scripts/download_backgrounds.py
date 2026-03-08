import subprocess
import os

def download_bg(query, filename):
    output_path = f"backgrounds/{filename}.mp4"
    if os.path.exists(output_path):
        print(f"✅ {filename} already exists. Skipping.")
        return

    print(f"📥 Downloading: {query}...")
    # Search for high-quality, vertically-friendly satisfying videos
    search_query = f"ytsearch1:No copyright {query} 4k satisfying background"
    
    cmd = [
        "yt-dlp",
        "-f", "bestvideo[height<=1080][ext=mp4]/best[ext=mp4]/best",
        "--match-filter", "duration > 60 & duration < 600",
        "--no-playlist",
        "--output", output_path,
        search_query
    ]
    
    try:
        subprocess.run(cmd, check=True)
        # Crop/Scale to 1080x1920 will be handled in assembly, but let's confirm download
        if os.path.exists(output_path):
            print(f"✨ Successfully downloaded {filename}")
    except Exception as e:
        print(f"❌ Failed to download {filename}: {e}")

if __name__ == "__main__":
    os.makedirs("backgrounds", exist_ok=True)
    
    # 1. Minecraft Parkour (The ultimate retention hack)
    download_bg("Minecraft Parkour Gameplay No Copyright", "minecraft_parkour")
    
    # 2. Futuristic Technology (Clean and professional)
    download_bg("Futuristic Blue Technology Grid 4k satisfying", "tech_loop")
    
    # 3. Satisfying Kinetic Sand/Slime (High retention)
    download_bg("Satisfying Hydraulic Press or Kinetic Sand No Copyright", "satisfying_slime")
