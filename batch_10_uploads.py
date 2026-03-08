import subprocess
import time
import os
import sys
import glob
from datetime import datetime, timedelta, timezone

# CONFIGURATION
TOTAL_UPLOADS = 10  # 5 per day for 2 days
UPLOADS_PER_DAY = 5

# "GOLDEN HOURS" in IST (24h format) 
IST_SLOTS = ["18:30", "22:30", "02:30", "05:30", "08:30"]

def get_path(rel_path):
    root = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(root, rel_path.replace("/", os.sep))

def get_next_n_schedule_times(n=10):
    now_ist = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    schedule_times = []
    
    for day_offset in range(5):
        target_date = now_ist.date() + timedelta(days=day_offset)
        for slot in IST_SLOTS:
            h, m = map(int, slot.split(":"))
            slot_time = datetime(target_date.year, target_date.month, target_date.day, h, m, 
                                 tzinfo=timezone(timedelta(hours=5, minutes=30)))
            
            if slot_time > now_ist + timedelta(minutes=30):
                utc_time = slot_time.astimezone(timezone.utc)
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
        cmd = [sys.executable, "scripts/run_all.py", f"--schedule={schedule_time}"]
        subprocess.run(cmd, check=True)
        
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
    print("🤖 [Batch Driver] Starting 2-Day Batch (10 Videos)...")
    
    slots = get_next_n_schedule_times(TOTAL_UPLOADS)
    print(f"📋 Found {len(slots)} slots.")
    
    for i, slot in enumerate(slots):
        day = (i // UPLOADS_PER_DAY) + 1
        print(f"   Slot {i+1:02}: {slot} (Day {day})")

    # Start Batch
    start_time = time.time()
    for i, slot_time in enumerate(slots):
        success = run_single_cycle(i + 1, TOTAL_UPLOADS, slot_time)
        if not success:
            print(f"⚠️ Warning: Cycle {i+1} failed.")
        
    print(f"\n🎉 2-DAY BATCH COMPLETE!")

if __name__ == "__main__":
    main()
