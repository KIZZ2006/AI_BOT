import subprocess
import time
import os
import sys
from datetime import datetime, timedelta, timezone

# CONFIGURATION
TOTAL_VIDEOS = 30
VIDEOS_PER_DAY = 2

# "GOLDEN HOURS" in IST (24h format) for maximum US/India reach
IST_SLOTS = ["18:30", "22:30"]

def get_path(rel_path):
    root = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(root, rel_path.replace("/", os.sep))

def get_next_30_slots():
    now_ist = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    schedule_times = []
    
    # We look through the next 20 days to find 30 slots
    for day_offset in range(1, 21): # Start from tomorrow
        target_date = now_ist.date() + timedelta(days=day_offset)
        for slot in IST_SLOTS:
            h, m = map(int, slot.split(":"))
            slot_time = datetime(target_date.year, target_date.month, target_date.day, h, m, 
                                 tzinfo=timezone(timedelta(hours=5, minutes=30)))
            
            # Convert to UTC ISO format for YouTube API
            utc_time = slot_time.astimezone(timezone.utc)
            schedule_times.append(utc_time.strftime("%Y-%m-%dT%H:%M:%S.0Z"))
            
            if len(schedule_times) == TOTAL_VIDEOS:
                return schedule_times
                
    return schedule_times

def run_single_cycle(run_number, schedule_time):
    print(f"\n{'='*60}")
    print(f"🚀 STARTING BATCH CYCLE {run_number}/{TOTAL_VIDEOS}")
    print(f"📅 SCHEDULED RELEASE TIME (UTC): {schedule_time}")
    print(f"{'='*60}\n")
    
    try:
        # Step 1: Run the pipeline with the schedule argument
        cmd = [sys.executable, "scripts/run_all.py", f"--schedule={schedule_time}"]
        # CRITICAL: Pass os.environ so sub-scripts see the OPENROUTER_API_KEY
        subprocess.run(cmd, check=True, env=os.environ.copy())
        
        # Step 2: Auto-Cleanup "Waste Data" to prevent Colab disk full
        print("🧹 [Cleanup] Clearing intermediate files...")
        cleanup_items = [
            "temp/*", "outputs/*.mp4", "outputs/*.mp3", "outputs/*.avi", 
            "outputs/*.txt", "outputs/visual_bumps/*", 
            "advanced_pipeline/intermediate/*", "captions.ass"
        ]
        import glob
        for pattern in cleanup_items:
            for f in glob.glob(get_path(pattern)):
                try:
                    if os.path.isfile(f): os.remove(f)
                except: pass
                
        print(f"\n✅ CYCLE {run_number} COMPLETED AND SCHEDULED.")
        return True

    except Exception as e:
        print(f"\n❌ CYCLE {run_number} FAILED: {e}")
        return False

def main():
    print("🤖 [Mega Scheduler] Initializing 30-Video Global Batch Driver...")
    
    # Check for internet (essential for YouTube upload)
    import requests
    try:
        requests.get("https://google.com", timeout=10)
    except:
        print("❌ Error: No internet connection. Scheduling requires YouTube API access.")
        return

    # Calculate 30 slots (2 per day for 15 days)
    slots = get_next_30_slots()
    print(f"📋 Generated {len(slots)} slots for the next 15 days.")

    # Start Mega Batch
    start_time = time.time()
    successful_runs = 0
    
    for i, slot_time in enumerate(slots):
        print(f"\n📊 TOTAL PROGRESS: {i}/{len(slots)} COMPLETE")
        success = run_single_cycle(i + 1, slot_time)
        if success:
            successful_runs += 1
        else:
            print(f"⚠️ Retrying Cycle {i+1} after cooling down...")
            time.sleep(30) 
            if run_single_cycle(i + 1, slot_time):
                successful_runs += 1
        
    total_duration_hours = (time.time() - start_time) / 3600
    print(f"\n{'='*60}")
    print(f"🎉 30-VIDEO MEGA BATCH COMPLETE!")
    print(f"✅ Success Rate: {successful_runs}/{len(slots)}")
    print(f"⏱️ Total Process Time: {total_duration_hours:.2f} hours")
    print(f"📉 Colab can now be disconnected.")
    print(f"🌍 YouTube will release your 2 shorts daily for the next 15 days.")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
