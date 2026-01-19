import os, time, subprocess
from huggingface_hub import HfFileSystem

# --- CONFIG ---
REPO_ID = "MASHOLA/YOUTUBE"
EXTENSIONS = (".mp4", ".mkv", ".mov", ".ts")
IGNORE_LIST = ["GOSPEL", "Loops"]

# Get secrets
STREAM_URL = os.getenv("STREAM_URL", "")
STREAM_KEY = os.getenv("STREAM_KEY", "")
# Ensure there is a slash between URL and Key
DESTINATION = f"{STREAM_URL.rstrip('/')}/{STREAM_KEY.lstrip('/')}"

fs = HfFileSystem()

def get_playlist():
    print(f"Checking for videos in {REPO_ID}...")
    try:
        all_files = fs.ls(f"datasets/{REPO_ID}", recursive=True, detail=False)
        valid_urls = []
        for f in sorted(all_files):
            if not f.lower().endswith(EXTENSIONS): continue
            if any(word.upper() in f.upper() for word in IGNORE_LIST): continue
            
            clean_path = f.replace(f"datasets/{REPO_ID}/", "")
            url = f"https://huggingface.co/datasets/{REPO_ID}/resolve/main/{clean_path}"
            valid_urls.append(url)
        return valid_urls
    except Exception as e:
        print(f"!!! Error scanning HF: {e}")
        return []

while True:
    playlist = get_playlist()
    if not playlist:
        print("No videos found. Waiting 60s...")
        time.sleep(60)
        continue

    print(f"Found {len(playlist)} videos. Starting stream...")

    for url in playlist:
        print(f"Playing: {url}")
        # Added -nostdin to prevent GitHub Action hang
        # Added -loglevel info to see what's happening
        cmd = [
            'ffmpeg', '-re', '-nostdin', '-i', url,
            '-c', 'copy', '-f', 'flv', '-loglevel', 'info', DESTINATION
        ]
        
        process = subprocess.run(cmd)
        if process.returncode != 0:
            print(f"FFmpeg stopped with error code {process.returncode}")
            time.sleep(5) # Brief pause before next video
