import subprocess
import time
import os
import sys
from datetime import datetime, timedelta, timezone

# CONFIGURATION
UPLOADS_PER_DAY = 5

# "GOLDEN HOURS" in IST (24h format)
# 6:30 PM, 10:30 PM, 2:30 AM, 5:30 AM, 8:30 AM
IST_SLOTS = ["18:30", "22:30", "02:30", "05:30", "08:30"]

def get_path(rel_path):
    root = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(root, rel_path.replace("/", os.sep))

def get_next_5_schedule_times():
    now_ist = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    schedule_times = []
    
    # We look through today, tomorrow, and the day after to find the next 5 slots
    for day_offset in range(3):
        target_date = now_ist.date() + timedelta(days=day_offset)
        for slot in IST_SLOTS:
            h, m = map(int, slot.split(":"))
            slot_time = datetime(target_date.year, target_date.month, target_date.day, h, m, 
                                 tzinfo=timezone(timedelta(hours=5, minutes=30)))
            
            # If the slot is at least 30 minutes in the future, it's a candidate
            # (30 mins buffer for rendering and uploading)
            if slot_time > now_ist + timedelta(minutes=30):
                # Convert to UTC ISO format for YouTube
                utc_time = slot_time.astimezone(timezone.utc)
                schedule_times.append(utc_time.strftime("%Y-%m-%dT%H:%M:%S.0Z"))
                
            if len(schedule_times) == UPLOADS_PER_DAY:
                return schedule_times
                
    return schedule_times

def run_single_cycle(run_number, schedule_time):
    print(f"\n{'='*60}")
    print(f"🚀 STARTING UPLOAD CYCLE {run_number}/{UPLOADS_PER_DAY}")
    print(f"📅 SCHEDULED RELEASE TIME: {schedule_time}")
    print(f"{'='*60}\n")
    
    try:
        # Step 1: Run the pipeline with the schedule argument
        cmd = [sys.executable, "scripts/run_all.py", f"--schedule={schedule_time}"]
        subprocess.run(cmd, check=True)
        
        # Step 2: Auto-Cleanup "Waste Data" to prevent disk bloat
        print("🧹 [Cleanup] Clearing intermediate files and test data...")
        cleanup_items = [
            "temp/*", "outputs/*.mp4", "outputs/*.mp3", "outputs/*.avi", 
            "outputs/*.txt", "outputs/visual_bumps/*", 
            "advanced_pipeline/intermediate/*", "captions.ass",
            "test_*.py", "check_versions.py", "*.part", "*.ytdl"
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
    print("🤖 [Batch Driver] Initializing Global Virality Batch Scheduler...")
    
    # Check for internet
    import requests
    try:
        requests.get("https://google.com", timeout=5)
    except:
        print("❌ Error: No internet connection. Scheduling requires YouTube API access.")
        return

    # Calculate 5 slots
    slots = get_next_5_schedule_times()
    print(f"📋 Found next {len(slots)} available slots for US audience.")

    # Start Batch
    start_time = time.time()
    successful_runs = 0
    for i, slot_time in enumerate(slots):
        print(f"\n📊 PROGRESS: {i}/{len(slots)} COMPLETE")
        success = run_single_cycle(i + 1, slot_time)
        if success:
            successful_runs += 1
        else:
            print(f"⚠️ Retrying Cycle {i+1} once...")
            time.sleep(10) # Cooling off
            if run_single_cycle(i + 1, slot_time):
                successful_runs += 1
        
    total_duration = (time.time() - start_time) / 60
    print(f"\n{'='*60}")
    print(f"🎉 BATCH COMPLETE!")
    print(f"✅ Success Rate: {successful_runs}/{len(slots)}")
    print(f"⏱️ Total Render Time: {total_duration:.1f} minutes")
    print(f"📉 Battery Saved: Laptop can now be closed/turned off.")
    print(f"🌍 YouTube will handle the releases automatically.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
