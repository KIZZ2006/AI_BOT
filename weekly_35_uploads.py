import subprocess
import time
import os
import sys
import glob
from datetime import datetime, timedelta, timezone

# CONFIGURATION
TOTAL_UPLOADS = 35  # 5 per day for 7 days
UPLOADS_PER_DAY = 5

# "GOLDEN HOURS" in IST (24h format) 
# Optimized for US audience peak engagement (Morning/Evening US time)
IST_SLOTS = ["18:30", "22:30", "02:30", "05:30", "08:30"]

def get_path(rel_path):
    root = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(root, rel_path.replace("/", os.sep))

def get_next_n_schedule_times(n=35):
    now_ist = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    schedule_times = []
    
    # We look through the next 10 days to find enough slots
    for day_offset in range(10):
        target_date = now_ist.date() + timedelta(days=day_offset)
        for slot in IST_SLOTS:
            h, m = map(int, slot.split(":"))
            slot_time = datetime(target_date.year, target_date.month, target_date.day, h, m, 
                                 tzinfo=timezone(timedelta(hours=5, minutes=30)))
            
            # If the slot is at least 30 minutes in the future, it's a candidate
            if slot_time > now_ist + timedelta(minutes=30):
                # Convert to UTC ISO format for YouTube
                utc_time = slot_time.astimezone(timezone.utc)
                # YouTube expects YYYY-MM-DDTHH:MM:SSZ
                schedule_times.append(utc_time.strftime("%Y-%m-%dT%H:%M:%S.0Z"))
                
            if len(schedule_times) == n:
                return schedule_times
                
    return schedule_times

def run_single_cycle(run_number, total_runs, schedule_time):
    print(f"\n{'='*60}")
    print(f"🚀 STARTING UPLOAD CYCLE {run_number}/{total_runs}")
    print(f"📅 SCHEDULED RELEASE TIME: {schedule_time}")
    print(f"{'='*60}\n")
    
    try:
        # Step 1: Run the pipeline with the schedule argument
        # We pass the schedule_time directly as the first argument to run_all.py's internal logic
        # Actually run_all.py looks for --schedule=...
        cmd = [sys.executable, "scripts/run_all.py", f"--schedule={schedule_time}"]
        subprocess.run(cmd, check=True)
        
        # Step 2: Auto-Cleanup intermediate files
        print("🧹 [Cleanup] Clearing intermediate files...")
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
                
        print(f"\n✅ CYCLE {run_number} COMPLETED AND SCHEDULED.")
        return True
    except Exception as e:
        print(f"\n❌ CYCLE {run_number} FAILED: {e}")
        return False

def main():
    print("🤖 [Weekly Driver] Initializing Global Virality WEEKLY Batch Scheduler...")
    print(f"Target: {TOTAL_UPLOADS} videos ({UPLOADS_PER_DAY} per day for 7 days)")
    
    # Check for internet
    import requests
    try:
        requests.get("https://google.com", timeout=5)
    except:
        print("❌ Error: No internet connection. Scheduling requires YouTube API access.")
        return

    # Calculate 35 slots
    slots = get_next_n_schedule_times(TOTAL_UPLOADS)
    print(f"📋 Found next {len(slots)} available slots for US audience.")
    
    for i, slot in enumerate(slots):
        day = (i // UPLOADS_PER_DAY) + 1
        print(f"   Slot {i+1:02}: {slot} (Day {day})")

    confirm = input("\nDo you want to start this batch? (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return

    # Start Batch
    start_time = time.time()
    for i, slot_time in enumerate(slots):
        success = run_single_cycle(i + 1, TOTAL_UPLOADS, slot_time)
        if not success:
            print(f"⚠️ Warning: Cycle {i+1} failed. Continuing to next...")
        
    total_duration = (time.time() - start_time) / 60
    print(f"\n{'='*60}")
    print(f"🎉 WEEKLY BATCH COMPLETE!")
    print(f"⏱️ Total Render Time: {total_duration:.1f} minutes")
    print(f"📉 You are now scheduled for the next 7 days.")
    print(f"🌍 YouTube will handle the releases automatically.")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
