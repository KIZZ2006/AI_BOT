import os
import sys
import subprocess
import json
import re
import psutil

def set_high_priority():
    try:
        p = psutil.Process(os.getpid())
        if os.name == 'nt':
            p.nice(psutil.HIGH_PRIORITY_CLASS)
        else:
            p.nice(-10)
        print("🚀 [Turbo] Process priority set to HIGH.")
    except Exception as e:
        print(f"⚠️ Failed to set priority: {e}")


# Express Mode: Set to False to lock-in the highest possible quality for US Audiences
EXPRESS_MODE = True # PRO MODE ENABLED (Temporarily set to True to bypass environment-specific GFPGAN crash)

# Handle FFmpeg/FFprobe path dynamically for Cross-Platform (Windows vs Colab/Linux)
FFMPEG_PATH = "ffmpeg"
if os.name == 'nt' and os.path.exists(r"D:\tools\ffmpeg\bin\ffmpeg.exe"):
    FFMPEG_PATH = r"D:\tools\ffmpeg\bin\ffmpeg.exe"

def get_ffprobe_path():
    if FFMPEG_PATH == "ffmpeg":
        return "ffprobe"
    return FFMPEG_PATH.replace("ffmpeg.exe", "ffprobe.exe")


def get_path(rel_path):
    root = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(root, rel_path.replace("/", os.sep))

def has_video_stream(file_path):
    if not os.path.exists(file_path): return False
    try:
        cmd = [get_ffprobe_path(), "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_type", "-of", "csv=p=0", file_path]

        output = subprocess.check_output(cmd, text=True).strip()
        return output == "video"
    except:
        return False

AVATAR_916 = get_path("images/avatar_vertical_916.png")
VOICE_RAW = "outputs/voice.mp3"
MUSIC_RAW = "audio/bg_music.mp3"
PROCESSED_AUDIO = "outputs/pro_audio.mp3"
INPUT_VIDEO = "advanced_pipeline/intermediate/input_face_916.mp4"
INPUT_PROXY = "advanced_pipeline/intermediate/input_proxy_480.mp4"
WAV2LIP_OUT = "outputs/final_test_wav2lip.mp4"
HD_OUT = "outputs/final_test_hd.mp4"
FINAL_OUT = "outputs/final_with_captions.mp4"

os.environ["PATH"] += os.pathsep + os.path.dirname(FFMPEG_PATH)

def run_pipeline():
    set_high_priority()
    # 0.4 Create Turbo Proxy (Downscale to 480p for 5x speed)
    print("🚀 [Turbo] Downscaling for processing speed...")
    subprocess.run([
        FFMPEG_PATH, "-y",
        "-threads", "0",
        "-i", INPUT_VIDEO,
        "-vf", "scale=-1:480:flags=bicubic", # Sharper scaling
        "-c:v", "libx264", "-crf", "18",
        "-preset", "ultrafast",
        INPUT_PROXY
    ], check=True)


    # 0.5 Process Audio (Dynamic Background Beats + Sonic Pulse SFX)
    print("🎧 [Step 0.5] Pro Audio Engineering (Compression + Sonic Pulse SFX)...")
    
    # 1. Selection: Background Music
    MUSIC_DIR = "music"
    SELECTED_MUSIC = get_path("audio/bg_music.mp3") 
    if os.path.exists(MUSIC_DIR) and len(os.listdir(MUSIC_DIR)) > 0:
        import random
        music_files = [os.path.join(MUSIC_DIR, f) for f in os.listdir(MUSIC_DIR) 
                       if f.endswith(".mp3") or f.endswith(".webm") or f.endswith(".m4a")]
        if music_files:
            SELECTED_MUSIC = random.choice(music_files)
            print(f"🎵 [Vibe Boost] Selected Track: {os.path.basename(SELECTED_MUSIC)}")

    # 2. Sonic Pulse: Map SFX to Timestamps
    sfx_filters = ""
    sfx_inputs = []
    
    meta_path = get_path("outputs/metadata.json")
    time_path = get_path("outputs/timestamps.json")
    
    if os.path.exists(meta_path) and os.path.exists(time_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            script_raw = json.load(f).get("script", "")
        with open(time_path, "r", encoding="utf-8") as f:
            timestamps = json.load(f)
            
        # Parse script for markers: [POP], [WHOOSH]
        import re
        tokens = re.split(r'(\[.*?\])', script_raw)
        
        current_word_idx = 0
        sfx_count = 0
        
        # We start from input index 2 (0=Voice, 1=Music)
        input_idx = 2
        
        for i, token in enumerate(tokens):
            if token.startswith("["):
                marker = token.strip("[]").upper()
                # Find the next word's timestamp
                if current_word_idx < len(timestamps):
                    start_time = int(timestamps[current_word_idx]['start'] * 1000) # ms
                    sfx_file = get_path(f"sfx/{marker.lower()}.mp3")
                    if os.path.exists(sfx_file):
                        sfx_inputs.extend(["-i", sfx_file])
                        # Delay the SFX to the word start time
                        sfx_filters += f"[{input_idx}:a]adelay={start_time}|{start_time},volume=0.4[sfx{sfx_count}]; "
                        sfx_count += 1
                        input_idx += 1
            else:
                # Count how many words in this text segment
                words = token.strip().split()
                current_word_idx += len(words)

    # 3. Final Multi-Track Mix with Professional Audio Ducking (Side-Chain Compression)
    # inputs: 0 (Voice), 1 (Music), 2+ (SFX)
    sfx_labels = "".join([f"[sfx{j}]" for j in range(sfx_count)])
    
    # CINEMATIC MIXING LOGIC:
    # 1. Voice gets EQ and Compression for authority.
    # 2. SFX are mixed into a single 'effects' bus.
    # 3. Music is 'ducked' by the Voice+SFX bus using sidechaincompress.
    audio_filter = (
        f"{sfx_filters}" # adelay filters for SFX
        f"[0:a]equalizer=f=200:t=q:w=1:g=4,bass=g=8:f=100,"
        f"compand=attacks=0:points=-80/-80|-24/-24|-12/-8|-6/-3|0/-2,volume=2.2[voice_comp]; "
        f"[1:a]volume=0.15[music_base]; " # Higher base volume, will be ducked
        f"[voice_comp]{sfx_labels}amix=inputs={1 + sfx_count}:duration=first[voice_sfx_bus]; "
        f"[music_base][voice_sfx_bus]sidechaincompress=threshold=0.1:ratio=20:attack=15:release=200[music_ducked]; "
        f"[voice_sfx_bus][music_ducked]amix=inputs=2:duration=first:dropout_transition=2[aout]"
    )
    
    cmd = [FFMPEG_PATH, "-y", "-i", VOICE_RAW, "-i", SELECTED_MUSIC]
    cmd.extend(sfx_inputs)
    cmd.extend(["-filter_complex", audio_filter, "-map", "[aout]", PROCESSED_AUDIO])
    
    subprocess.run(cmd, check=True)

    # 1. Run Wav2Lip (On Turbo Proxy)
    # RYZEN 3 OPTIMIZATION: Lower batch size for 8GB RAM safety
    print("👄 [Step 1] Running Lip-Sync (Generative AI - RYZEN 3 MODE)...")
    subprocess.run([
        sys.executable,
        "Wav2Lip/inference.py",
        "--checkpoint_path", "Wav2Lip/checkpoints/wav2lip_gan.pth",
        "--face", INPUT_PROXY, 
        "--audio", PROCESSED_AUDIO,
        "--outfile", WAV2LIP_OUT,
        "--wav2lip_batch_size", "8", # Aggressive for 8GB RAM
        "--face_det_batch_size", "8",
        "--nosmooth" # Faster on CPU
    ], check=True, env=os.environ) # Pass environment for path lookup



    # 2. Conditional HD Enhancement
    input_for_assembly = WAV2LIP_OUT
    if not EXPRESS_MODE:
        print("✨ [Step 2] Applying HD Face Enhancement (GFPGAN)...")
        subprocess.run([
            sys.executable,
            "enhance_video.py",
            WAV2LIP_OUT,
            HD_OUT
        ], check=True)
        input_for_assembly = HD_OUT
    POLISHED_TEMP = "outputs/polished_temp.mp4"
    BG_DIR = "backgrounds"
    FETCHED_BROLL = get_path("outputs/b_roll.mp4")
    # PRIORITY: 1. Minecraft Parkour (High Retention) -> 2. Relevant News B-Roll -> 3. Satisfying Loops
    SATISFYING_BG = get_path("backgrounds/minecraft_parkour.mp4")
    
    if os.path.exists(SATISFYING_BG):
        print(f"🎮 [Viral Hack] Using Minecraft Parkour Background")
    elif os.path.exists(FETCHED_BROLL):
        print(f"🌍 [Newsroom] Injecting Contextual Background: B-Roll")
        SATISFYING_BG = FETCHED_BROLL
    elif os.path.exists(BG_DIR) and len(os.listdir(BG_DIR)) > 0:
        import random
        bg_files = [os.path.join(BG_DIR, f) for f in os.listdir(BG_DIR) if f.endswith(".mp4")]
        if bg_files: SATISFYING_BG = random.choice(bg_files)
        print(f"🎮 [Viral Hack] Using Catch-all Loop: {os.path.basename(SATISFYING_BG)}")
    else:
        SATISFYING_BG = get_path("images/robot_bg.mp4") # Safety Default
    
    # 3. PRECISION EDITING: Keyword-Locked Visuals
    # We map keywords from timestamps.json to specific time windows
    print("🎯 [Precision Engine] Calculating Keyword-Locked Visual Triggers...")
    
    keyword_triggers = []
    
    # Load Timestamps
    timestamps_path = get_path("outputs/timestamps.json")
    if os.path.exists(timestamps_path):
        with open(timestamps_path, "r", encoding="utf-8") as f:
            ts_data = json.load(f)
            
        # Target Keywords for Visual Bumps
        # We look for broad categories. Ideally fetches should be tagged, but we'll infer.
        # Simple Logic: Trigger visual bumps at 15%, 40%, 65%, 90% of video if no keywords found
        total_duration = ts_data[-1]['end'] if ts_data else 60
        
        # Define 4 "Slots" for potential visuals
        slots = [total_duration * 0.15, total_duration * 0.4, total_duration * 0.65, total_duration * 0.85]
        
        # B-Roll Bumping Logic (Visual Density - Floating Window Mode)
        bump_dir = get_path("outputs/visual_bumps")
        bump_files = []
        if os.path.exists(bump_dir):
            bump_files = [os.path.join(bump_dir, f) for f in os.listdir(bump_dir) if f.endswith(".mp4")]
        
        # Filter valid bumps
        valid_bump_files = [f for f in bump_files if has_video_stream(f)]
        
        bump_inputs = []
        bump_filters = ""
        last_v_label = "scene"
        actual_bump_idx = 0
        
        # Audio-Reactive Camera Logic (Micro-Zooms)
        # We simulate "energy" by slightly zooming in during the middle of the video
        # Zoom from 1.0 to 1.05 and back from t=10 to t=50
        zoom_expr = f"1+0.05*sin(2*PI*(t-10)/40)*between(t,10,50)"

        for i, b_file in enumerate(valid_bump_files[:4]):
            if i >= len(slots): break
            
            b_idx = 4 + actual_bump_idx
            bump_inputs.extend(["-stream_loop", "-1", "-i", b_file])
            
            # Use the calculated "Golden Slot" time
            start_time = slots[i]
            end_time = start_time + 4.5
            
            # Randomize position slightly for "Organic" feel
            import random
            pos_y = 350 if i % 2 == 0 else 450
            
            # Scale smaller and add a subtle white border for "Picture-in-Picture" look
            bump_filters += (
                f"[{b_idx}:v]scale=500:350:force_original_aspect_ratio=increase,crop=500:350,"
                f"pad=504:354:2:2:white,setsar=1,fade=t=in:st={start_time}:d=0.4,fade=t=out:st={end_time-0.4}:d=0.4[card{i}]; "
                f"[{last_v_label}][card{i}]overlay=(W-w)/2:{pos_y}:enable='between(t,{start_time},{end_time})'[v_bump{i}]; "
            )
            last_v_label = f"v_bump{i}"
            actual_bump_idx += 1

    print(f"🎨 [Step 3] Assembling Layout (Split Rendering for Stability)...")
    
    # STEP A: Layout Assembly (Host + BG + UI + Bumps) - Fixed Over-Scale
    # We scale to 1.1x (1188x2112) so we have "room" to zoom in/out with the crop filter later
    FLAT_TEMP = "outputs/flat_layout_temp.mp4"
    
    layout_filter = (
        f"[0:v]scale=1188:2112,colorkey=0xFF00FF:0.32:0.10," 
        f"crop=1188:2112,"
        f"unsharp=3:3:1.2[host_raw]; " 
        f"[1:v]scale=1190:2114:force_original_aspect_ratio=increase,crop=1188:2112,boxblur=3:1[bg_news]; " 
        f"[bg_news][host_raw]overlay=0:385[scene_base]; " 
        f"[2:v]scale=352:-1,colorkey=0x000000:0.2:0.1[live]; "
        f"[3:v]scale=495:-1,colorkey=0x000000:0.2:0.1[ticker]; "
        f"[scene_base][live]overlay=55:132[v1]; "
        f"[v1][ticker]overlay=W-w-55:132[scene]; " 
        f"{bump_filters}"
        f"[{last_v_label}]null[v_out]" 
    )

    
    HOSTS = {
        "Daniel": ["images/daniel_pro.png", "images/daniel_v2.png", "images/main.png"],
        "Sarah": ["images/sarah_pro.png", "images/sarah_v1.png", "images/sarah_v2.png", "images/avatar2.jpeg"]
    }
    
    SELECTED_HOST_AVATAR = None
    meta_path = get_path("outputs/metadata.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
            host_name = metadata.get("host", "Daniel") # Default to Daniel
            
            if host_name in HOSTS:
                for avatar_path in HOSTS[host_name]:
                    full_avatar_path = get_path(avatar_path)
                    if os.path.exists(full_avatar_path):
                        SELECTED_HOST_AVATAR = full_avatar_path
                        print(f"👤 [Host] Selected host avatar: {os.path.basename(SELECTED_HOST_AVATAR)}")
                        break
            
    if SELECTED_HOST_AVATAR:
        AVATAR_916 = SELECTED_HOST_AVATAR
    else:
        print(f"⚠️ Warning: No valid host avatar found for '{host_name}'. Using default: {os.path.basename(AVATAR_916)}")

    cmd_a = [
        FFMPEG_PATH, "-y",
        "-i", input_for_assembly,
        "-stream_loop", "-1", "-i", SATISFYING_BG,
        "-i", get_path("assets/live_badge.png"),
        "-i", get_path("assets/news_ticker.png")
    ]
    
    # Error-free Check: Verify Assets
    for i_path in [input_for_assembly, SATISFYING_BG, get_path("assets/live_badge.png"), get_path("assets/news_ticker.png")]:
        if not os.path.exists(i_path):
            print(f"⚠️ Warning: Missing asset {i_path}. Performance may degrade.")
    
    cmd_a.extend(bump_inputs)
    # Select encoder based on environment
    # Windows/AMD = h264_amf, Colab/Linux = libx264 (safe) or h264_nvenc (fastest)
    v_encoder = "h264_amf" if os.name == "nt" else "libx264"
    
    cmd_a.extend([
        "-filter_complex", layout_filter,
        "-map", "[v_out]",
        "-map", "0:a", 
        "-shortest",
        "-c:v", v_encoder,
        "-b:v", "15M", 
        "-threads", "0",
        FLAT_TEMP
    ])

    subprocess.run(cmd_a, check=True)

    # STEP B: Camera Magic (Fixed-Resolution Crop Zoom)
    print(f"🎥 [Step 3.5] Applying Stable Dynamic Zoom & Colors...")
    
    # Logic: We crop a 1080x1920 window out of the 1188x2112 canvas
    # Zoom In = Smaller crop window area, then scaled back up to 1080p
    # This keeps the buffer size constant = ZERO CRASHES
    zoom_val = f"(1+0.05*sin(2*PI*(t-10)/40)*between(t,10,50))"
    crop_w = f"1188/{zoom_val}"
    crop_h = f"2112/{zoom_val}"
    
    camera_filter = (
        f"crop={crop_w}:{crop_h}:(1188-ow)/2:(2112-oh)/2,scale=1080:1920,"
        f"eq=contrast=1.15:saturation=1.4:brightness=0.02"
    )
    
    cmd_b = [
        FFMPEG_PATH, "-y",
        "-i", FLAT_TEMP,
        "-vf", camera_filter,
        "-c:v", "libx264", 
        "-preset", "ultrafast",
        "-crf", "18",
        "-threads", "0",
        "-c:a", "copy",
        POLISHED_TEMP
    ]
    
    # ONEDRIVE LOCK PROTECTION: Wait for file to be ready
    import time
    max_retries = 10
    for i in range(max_retries):
        try:
            with open(FLAT_TEMP, 'rb') as f: break
        except IOError:
            print(f"🔄 [OneDrive] Waiting for file release (Retry {i+1})...")
            time.sleep(2.5)
            
    subprocess.run(cmd_b, check=True)
    
    # Cleanup intermediate
    try: 
        time.sleep(2)
        if os.path.exists(FLAT_TEMP): os.remove(FLAT_TEMP)
    except: pass







    # 4. Captions
    print("💬 [Step 4] Generating Viral Pop-In Captions...")
    subprocess.run([
        sys.executable,
        "scripts/subtitle_overlay.py",
        POLISHED_TEMP,
        FINAL_OUT
    ], check=True)

    print(f"\n🔥 TURBO SUCCESS! Video Ready: {FINAL_OUT}")

if __name__ == "__main__":
    os.makedirs("advanced_pipeline/intermediate", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    run_pipeline()
