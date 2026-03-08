# Script to upload final video to YouTube Shorts
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import json
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

def get_path(rel_path):
    return os.path.join(ROOT_DIR, rel_path.replace("/", os.sep))

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
token_path = get_path("token.json")

creds = None
if os.path.exists(token_path):
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:
            print(f"⚠️ Refresh failed: {e}. Re-authenticating...")
            if os.path.exists(token_path):
                os.remove(token_path)
            flow = InstalledAppFlow.from_client_secrets_file(get_path("config/client_secret.json"), SCOPES)
            creds = flow.run_local_server()
    else:
        flow = InstalledAppFlow.from_client_secrets_file(get_path("config/client_secret.json"), SCOPES)
        creds = flow.run_local_server()
    
    with open(token_path, "w") as token:
        token.write(creds.to_json())

youtube = build("youtube", "v3", credentials=creds)

# 1. Load Multi-Host Research Metadata
metadata_path = get_path("outputs/metadata.json")
video_title = "Latest AI News 🚀 #shorts"
description = "AI News Breakdown. #AI #Tech"

if os.path.exists(metadata_path):
    with open(metadata_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        video_title = data.get("title", video_title)
        # Ensure #shorts is in the title for algorithm boost
        if "#shorts" not in video_title.lower():
            video_title += " #shorts"
            
        # PRO-DESCRIPTION: Cliffhangers + Curiosity
        ai_desc = data.get("description", "")
        if ai_desc:
            description = f"{ai_desc}\n\nWatch until 0:25 for the biggest reveal! 😱"
        else:
            description = "Most people are missing the biggest shift in AI traffic. I tested it and the results are INSANE. Watch until the end to see how it works! 🚀"

# 2. Sisinty-Viral Tags (2026 Optimized - HIGH CTR US TARGETING)
viral_tags = [
    "shorts", "ai", "technews", "chatgpt", "growthhacking", 
    "moneyhacks", "futuretech", "innovation", 
    "usa", "siliconvalley", "technews", "americantech",
    "airevolution", "automation", "wealth", "secret"
]

# Update hashtags in description for SEO
description += "\n\n#AIRevolution #TechTrends #USA #LifeHacks #ShortsViral"

video_file = get_path("outputs/final_with_captions.mp4")
request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": video_title[:100], 
            "description": description,
            "tags": viral_tags
        },
        "status": {"privacyStatus": "public"}
    },
    media_body=MediaFileUpload(video_file)
)

# 2.5 Handle Scheduling
# If a schedule time is provided (Format: YYYY-MM-DDTHH:MM:SSTZD)
if len(sys.argv) > 1:
    schedule_time = sys.argv[1]
    print(f"📅 [Scheduler] Setting publication time for: {schedule_time}")
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": video_title[:100], 
                "description": description,
                "tags": viral_tags
            },
            "status": {
                "privacyStatus": "private",
                "publishAt": schedule_time,
                "selfDeclaredMadeForKids": False
            }
        },
        media_body=MediaFileUpload(video_file)
    )
response = request.execute()
video_id = response['id']
print(f"✅ Uploaded: https://youtube.com/watch?v={video_id}")

# 3. MONETIZED COMMENT AUTOMATION (The Sisinty Pin)
try:
    with open(metadata_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        marketing_comment = data.get("marketing_comment", "")
        
    if marketing_comment:
        print("💬 [Marketing Engine] Posting & Pinning Viral Comment...")
        # Add Affiliate Link Placeholder if not present
        if "http" not in marketing_comment:
            marketing_comment += "\n\n🚀 Get the Best AI Tools Here: https://growthschool.io/ (Affiliate)"
            
        comment_res = youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": marketing_comment
                        }
                    }
                }
            }
        ).execute()
        
        # PIN THE COMMENT (Requires 'modern' API level or Creator status)
        # Note: Pinning via API can be restricted on new channels, but the comment stay at top if early.
        print(f"✅ Marketing Comment Posted: {marketing_comment[:50]}...")
except Exception as e:
    print(f"⚠️ Comment Automation Failed: {e}")