import os
import sys
import subprocess
import json
from datetime import timedelta


FFMPEG_PATH = r"D:\tools\ffmpeg\bin\ffmpeg.exe"
os.environ["PATH"] += os.pathsep + r"D:\tools\ffmpeg\bin"

def get_word_timestamps(audio_path):
    from faster_whisper import WhisperModel
    print(f"🎙️ [AMD Turbo] Transcribing with Faster-Whisper: {audio_path}")
    # Optimized for AMD CPU (AVX2 support)
    model = WhisperModel("tiny.en", device="cpu", compute_type="int8")

    segments, info = model.transcribe(audio_path, beam_size=5, word_timestamps=True)
    
    # Standardize result format for the rest of the script
    class Word:
        def __init__(self, text, start, end):
            self.word = text
            self.start = start
            self.end = end
            
    class Segment:
        def __init__(self, words):
            self.words = words
            
    class Result:
        def __init__(self, segments):
            self.segments = segments

    all_segments = []
    for s in segments:
        words = [Word(w.word, w.start, w.end) for w in s.words]
        all_segments.append(Segment(words))
        
    return Result(all_segments)

EMOJI_MAP = {
    "AI": "🤖", "ROBOT": "🤖", "MONEY": "💰", "CASH": "💵", "PROFIT": "📈",
    "FUTURE": "⏳", "TECH": "💻", "NEW": "🔥", "HOT": "🧨", "SHOCKING": "😱",
    "SUCCESS": "🏆", "ROCKET": "🚀", "GROWTH": "📊", "STOP": "🛑", "WARNING": "🚨"
}

def generate_ass_file(result, ass_path, width, height):
    print(f"✍️ Generating Sisinty-Style Captions: {ass_path}")
    
    # VAIBHAV 3.0 SCALING: Middle-Center placement
    font_size = int(height * 0.08) # Slightly smaller for more words
    margin_v = int(height * 0.45) # 45% from bottom (Middle-Center)
    
    # ASS Header: Standardized for FFmpeg Compatibility
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,Arial,{font_size},&H00FFFFFF,&H00000000,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,8,0,2,30,30,{margin_v},1
Style: Highlight,Arial,{font_size},&H00000000,&H00000000,&H00CCFF00,&H00CCFF00,-1,0,0,0,100,100,0,0,1,5,0,2,30,30,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Text
"""
    
    events = []
    i = 0
    POWER_WORDS = ["FREE", "MONEY", "AI", "SCAM", "NEW", "STOP", "DANGER", "PROFIT", "SECRET", "HIDDEN", "VIRAL", "WRONG", "HACK", "SHOCKING", "WATCH"]
    
    for segment in result.segments:
        for word in segment.words:
            start = format_timestamp(word.start)
            end = format_timestamp(word.end)
            text = word.word.strip().upper()
            
            clean_word = text.replace(",", "").replace(".", "").replace("!", "").replace("?", "")
            
            is_power = clean_word in POWER_WORDS or clean_word in EMOJI_MAP
            
            if clean_word in EMOJI_MAP:
                text = f"{text} {EMOJI_MAP[clean_word]}"

            # Pulsing Animation Logic: Center Focal Mode
            if is_power:
                # Highlighted style (Black text on Neon Green)
                style = "Highlight"
                # Add a small background box effect via ASS drawing if possible, or just simpler highlight
                animated_text = "{\\fscx115\\fscy115\\t(0,80,\\fscx100\\fscy100)}" + text
            else:
                style = "Main"
                animated_text = "{\\fscx105\\fscy105\\t(0,80,\\fscx100\\fscy100)}" + text
            
            events.append(f"Dialogue: 0,{start},{end},{style},{animated_text}")
            i += 1

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write("\n".join(events))

def format_timestamp(seconds):
    # Strictly H:MM:SS.cc for ASS compatibility
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remaining_seconds = seconds % 60
    centiseconds = int((remaining_seconds - int(remaining_seconds)) * 100)
    return f"{hours}:{minutes:02d}:{int(remaining_seconds):02d}.{centiseconds:02d}"

def burn_subtitles(input_video, ass_path, output_video):
    # CRITICAL: Use full path for ASS file and remove fontsdir to stop file-scanning errors
    abs_ass = os.path.abspath(ass_path).replace("\\", "/") # FFmpeg style paths
    # If the path has a drive letter like C:, we need to escape it for the subtitles filter
    # subtitles=C\\:/path/to/file.ass
    safe_ass = abs_ass.replace(":", "\\:")
    
    print(f"🔥 [AMD AMF] Burning Sisinty-Captions: {output_video}...")
    
    cmd = [
        FFMPEG_PATH, "-y",
        "-i", input_video,
        "-vf", f"subtitles='{safe_ass}'",
        "-c:v", "h264_amf", # AMD HARDWARE ENCODER
        "-quality", "quality",
        "-rc", "vbr_peak",
        "-b:v", "8M",
        "-threads", "6",
        "-aspect", "9:16",
        "-c:a", "copy",
        output_video
    ]
    subprocess.run(cmd, check=True)

def process_captions(video_path, output_path):
    cmd_res = [FFMPEG_PATH.replace("ffmpeg.exe", "ffprobe.exe"), "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "json", video_path]
    meta = json.loads(subprocess.check_output(cmd_res))
    width, height = meta['streams'][0]['width'], meta['streams'][0]['height']
    
    # REUSE TIMESTAMPS: No need to re-run whisper
    time_path = "outputs/timestamps.json"
    if os.path.exists(time_path):
        with open(time_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # Structure it back for generate_ass_file
        class Word:
            def __init__(self, text, start, end):
                self.word = text
                self.start = start
                self.end = end
        
        class Segment:
            def __init__(self, words):
                self.words = words
        
        class Result:
            def __init__(self, segments):
                self.segments = segments
        
        # We just group all words into one segment for simplicity
        words = [Word(w['word'], w['start'], w['end']) for w in data]
        result = Result([Segment(words)])
        
        ass_path = os.path.join(os.getcwd(), "captions.ass")
        generate_ass_file(result, ass_path, width, height)
        burn_subtitles(video_path, ass_path, output_path)
    else:
        print("❌ Error: timestamps.json not found. Run timestamp_engine.py first.")

if __name__ == "__main__":
    process_captions(sys.argv[1], sys.argv[2])