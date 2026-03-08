import subprocess
import time
import os
import sys
import glob
from datetime import datetime, timedelta, timezone

# 2026 HYPER-GROWTH CONFIGURATION
TOTAL_UPLOADS = 70  # 10 per day for 7 days
UPLOADS_PER_DAY = 10

# "VIRAL WAVE" SLOTS (IST) - Optimized for 24/7 Global & US Traffic
# Targeted to hit US 8:00 AM to Midnight EST perfectly.
IST_SLOTS = [
    "18:30", "20:30", "22:30", "00:30", "02:30", 
    "04:30", "06:30", "08:30", "10:30", "12:30"
]

def get_path(rel_path):
    root = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(root, rel_path.replace("/", os.sep))

def get_next_n_schedule_times(n=70):
    now_ist = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    schedule_times = []
    
    # Check next 10 days to be safe
    for day_offset in range(10):
        target_date = now_ist.date() + timedelta(days=day_offset)
        for slot in IST_SLOTS:
            h, m = map(int, slot.split(":"))
            slot_time = datetime(target_date.year, target_date.month, target_date.day, h, m, 
                                 tzinfo=timezone(timedelta(hours=5, minutes=30)))
            
            # 30-minute buffer for processing
            if slot_time > now_ist + timedelta(minutes=30):
                utc_time = slot_time.astimezone(timezone.utc)
                schedule_times.append(utc_time.strftime("%Y-%m-%dT%H:%M:%S.0Z"))
                
            if len(schedule_times) == n:
                return schedule_times
                
    return schedule_times

def run_single_cycle(run_number, total_runs, schedule_time):
    print(f"\n" + "="*60)
    print(f"🚀 [MEGA-BATCH] PROCESSING VIDEO {run_number}/{total_runs}")
    print(f"📅 TARGET PUBLISH: {schedule_time}")
    print("="*60 + "\n")
    
    try:
        # Pass schedule to run_all.py
        cmd = [sys.executable, "scripts/run_all.py", f"--schedule={schedule_time}"]
        subprocess.run(cmd, check=True)
        
        # Aggressive Cleanup to save space
        print("🧹 [Cleanup] Wiping large intermediate data...")
        cleanup_items = [
            "temp/*", "outputs/*.mp4", "outputs/*.mp3", "outputs/*.avi", 
            "outputs/*.txt", "outputs/visual_bumps/*", 
            "advanced_pipeline/intermediate/*", "captions.ass"
        ]
        for pattern in cleanup_items:
            for f in glob.glob(get_path(pattern)):
                try:
                    if os.path.isfile(f): os.remove(f)
                except: pass
                
        print(f"\n✅ CYCLE {run_number} COMPLETE. Video is in YouTube's queue.")
        return True
    except Exception as e:
        print(f"\n❌ CYCLE {run_number} FAILED: {e}")
        # Wait a bit before retrying next one in case of network glitch
        time.sleep(10)
        return False

def main():
    print("💎 [Advanced Verifier Mode] Initializing 10-A-Day Weekly Scheduler...")
    print(f"Target: {TOTAL_UPLOADS} high-retention shorts.")
    
    # Pre-flight checks
    import requests
    try:
        requests.get("https://google.com", timeout=5)
    except:
        print("❌ CRITICAL: No Internet. Cannot communicate with YouTube API.")
        return

    # Map out the week
    slots = get_next_n_schedule_times(TOTAL_UPLOADS)
    print(f"📋 Generated {len(slots)} scheduling slots starting from tonight.")
    
    # Summary of first few
    print("\nFirst 3 slots (IST):")
    for i in range(min(3, len(slots))):
        print(f"  - Slot {i+1}: {slots[i]}")

    print("\n⚠️ WARNING: This will take a long time to finish.")
    print("Ensure laptop is plugged into power.")
    
    # Starting the loop
    start_time = time.time()
    success_count = 0
    
    for i, slot_time in enumerate(slots):
        if run_single_cycle(i + 1, TOTAL_UPLOADS, slot_time):
            success_count += 1
        
        # Summary every 10 videos
        if (i + 1) % 10 == 0:
            print(f"\n📊 PROGRESS: {success_count}/{i+1} videos successfully scheduled.")

    total_duration = (time.time() - start_time) / 3600
    print(f"\n" + "="*60)
    print(f"🎉 MISSION ACCOMPLISHED!")
    print(f"✅ Total Videos Scheduled: {success_count}")
    print(f"⏱️ Total Execution Time: {total_duration:.1f} hours")
    print(f"📈 Your channel is now set for a full week of growth.")
    print("="*60)

if __name__ == "__main__":
    main()
