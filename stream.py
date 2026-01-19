import os
import time
import subprocess
from huggingface_hub import HfFileSystem

# --- CONFIGURATION ---
# Your specific Hugging Face Repository
REPO_ID = "MASHOLA/YOUTUBE" 
# Extensions to look for
EXTENSIONS = (".mp4", ".mkv", ".mov", ".ts")

# --- SKIP RULES ---
# The script will skip any folder or file containing these words
IGNORE_LIST = ["GOSPEL", "Loops"]

# Streaming Destination (Linked via GitHub Secrets)
STREAM_URL = os.getenv("STREAM_URL")
STREAM_KEY = os.getenv("STREAM_KEY")
DESTINATION = f"{STREAM_URL}/{STREAM_KEY}"

fs = HfFileSystem()

def get_filtered_playlist():
    """Scans the repo and removes anything matching the ignore list."""
    try:
        # Scan the entire repository recursively
        all_files = fs.ls(f"datasets/{REPO_ID}", recursive=True, detail=False)
        
        valid_urls = []
        for file_path in sorted(all_files):
            # 1. Only grab video files
            if not file_path.lower().endswith(EXTENSIONS):
                continue
            
            # 2. Skip if "GOSPEL" or "Loops" is in the path
            # We use .upper() to make sure it catches "gospel", "Gospel", or "GOSPEL"
            if any(word.upper() in file_path.upper() for word in IGNORE_LIST):
                print(f"Skipping ignored content: {file_path}")
                continue
            
            # 3. Create the direct 'resolve' link
            clean_path = file_path.replace(f"datasets/{REPO_ID}/", "")
            url = f"https://huggingface.co/datasets/{REPO_ID}/resolve/main/{clean_path}"
            valid_urls.append(url)
            
        return valid_urls
    except Exception as e:
        print(f"Error scanning Hugging Face: {e}")
        return []

def run_stream():
    while True:
        print(f"\n--- Refreshing Playlist: {time.ctime()} ---")
        playlist = get_filtered_playlist()
        
        if not playlist:
            print("No videos found (or all were ignored). Retrying in 60s...")
            time.sleep(60)
            continue

        for video_url in playlist:
            print(f"Now playing: {video_url}")
            
            # FFmpeg command: -re (native speed), -c copy (low CPU)
            cmd = [
                'ffmpeg', '-re', '-i', video_url,
                '-c', 'copy', '-f', 'flv', DESTINATION
            ]
            
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError:
                print(f"Error streaming {video_url}. Moving to next video.")

        print("End of playlist reached. Restarting scan...")

if __name__ == "__main__":
    run_stream()
