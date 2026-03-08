import os
import json
import sys

def generate_timestamps(audio_path, output_json):
    from faster_whisper import WhisperModel
    print(f">>> [TIMESTAMP ENGINE] Analyzing audio for SFX mapping: {audio_path}")
    
    # Optimized for AMD CPU (AVX2 support)
    model = WhisperModel("tiny.en", device="cpu", compute_type="int8")

    segments, info = model.transcribe(audio_path, beam_size=5, word_timestamps=True)
    
    word_data = []
    for segment in segments:
        for word in segment.words:
            word_data.append({
                "word": word.word.strip().upper(),
                "start": word.start,
                "end": word.end
            })
            
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(word_data, f, indent=4)
    print(f"✅ Timestamps saved to {output_json}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python timestamp_engine.py <audio_path> <output_json>")
    else:
        generate_timestamps(sys.argv[1], sys.argv[2])
