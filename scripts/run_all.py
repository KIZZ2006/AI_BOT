import subprocess
import time
import os
import sys
import psutil
from concurrent.futures import ThreadPoolExecutor

def set_high_priority():
    try:
        p = psutil.Process(os.getpid())
        if os.name == 'nt':
            p.nice(psutil.HIGH_PRIORITY_CLASS)
        else:
            p.nice(-10) # High priority on Linux/Mac
        print("🚀 [Turbo] Process priority set to HIGH.")
    except Exception as e:
        print(f"⚠️ Failed to set priority: {e}")


def check_dependencies():
    missing = []
    try: import edge_tts
    except: missing.append("edge-tts")
    try: import mediapipe
    except: missing.append("mediapipe")
    try: import bs4
    except: missing.append("beautifulsoup4")
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("💡 Hint: Run the Colab Setup Cell again with the updated pip command.")
        return False
    return True

def run_step(cmd):
    print(f">>> Starting: {' '.join(cmd)}")
    # CRITICAL: Pass os.environ so sub-scripts see the OPENROUTER_API_KEY
    result = subprocess.run(cmd, env=os.environ.copy())
    if result.returncode != 0:
        raise Exception(f"Step failed: {' '.join(cmd)}")
    return result

def run_pipeline():
    set_high_priority()
    if not check_dependencies():
        return
    print(">>> Starting Optimized AI Media Pipeline (V9 Parallel Edition)...")

    
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    
    start_time = time.time()

    # Step 1: Research (Sequential - everything depends on this)
    run_step([sys.executable, "scripts/fetch_news.py"])
    
    
    # Step 2-4: Parallel Visuals, Audio & Avatar
    # These don't depend on each other, only on metadata from Step 1
    print("\n[SPEED] Fetching B-Roll, synthesizing voice, and humanizing host...")
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(run_step, [sys.executable, "scripts/fetch_broll.py"]),
            executor.submit(run_step, [sys.executable, "scripts/fetch_visuals.py"]),
            executor.submit(run_step, [sys.executable, "scripts/synth_voice.py"]),
            executor.submit(run_step, [sys.executable, "scripts/life_sim.py"])
        ]
        # Wait for all to complete
        for future in futures:
            future.result()

    # NEW STEP: Generate Timestamps for SFX & Captions
    # This must happen before run_wav2lip_wrapper because the audio mixer needs timestamps
    run_step([sys.executable, "scripts/timestamp_engine.py", "outputs/voice.mp3", "outputs/timestamps.json"])

    # Step 5: Assembly (Lip Sync & Overlay)
    run_step([sys.executable, "run_wav2lip_wrapper.py"])
    
    # Step 6: Upload
    upload_cmd = [sys.executable, "scripts/upload_video.py"]
    # Check if a schedule time was passed to run_all.py
    for arg in sys.argv:
        if arg.startswith("--schedule="):
            schedule_time = arg.split("=")[1]
            upload_cmd.append(schedule_time)
            
    run_step(upload_cmd)

    total_time = time.time() - start_time
    print(f"\n🎉 Pipeline Complete in {total_time:.1f}s! Ready in 'outputs/final_with_captions.mp4'.")

if __name__ == "__main__":
    run_pipeline()