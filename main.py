import subprocess
import time
import os
import requests

# --- CONFIGURATION ---
# Replace these with your actual MP4 video links from Hugging Face
VIDEO_LINKS = [
    "https://huggingface.co/datasets/MASHOLA/YOUTUBE/resolve/main/VIDEOS/WASAFI%20MUSIC%20TV.mp4?download=true",
    " "
]

STREAM_URL = "rtmp://a.rtmp.youtube.com/live2/"
# This reads the secret you set in GitHub
STREAM_KEY = os.getenv("STREAM_KEY") 
STATE_FILE = "state.txt"

def download_file(url, local_filename):
    if not os.path.exists(local_filename):
        print(f"Downloading {local_filename} from Hugging Face...")
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Download of {local_filename} complete.")

def get_last_index():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return int(f.read().strip())
        except: return 0
    return 0

def save_index(index):
    with open(STATE_FILE, "w") as f:
        f.write(str(index))

def start_streaming():
    if not STREAM_KEY:
        print("Error: STREAM_KEY not found in Environment Variables.")
        return

    while True:
        current_index = get_last_index()
        
        for i in range(current_index, len(VIDEO_LINKS)):
            save_index(i)
            local_video = f"video_{i}.mp4"
            
            # Download locally to stop buffering
            try:
                download_file(VIDEO_LINKS[i], local_video)
            except Exception as e:
                print(f"Download error on video {i}: {e}")
                continue

            print(f"Starting Stream: {local_video}")

            # Optimized FFmpeg for YouTube Live Video
            cmd = [
                'ffmpeg',
                '-re',                          # Read at native speed
                '-i', local_video,              # Local input file
                '-c:v', 'libx264',              # Re-encode for stability
                '-preset', 'veryfast', 
                '-b:v', '4000k',                # Bitrate for 1080p
                '-maxrate', '4000k', 
                '-bufsize', '8000k',
                '-pix_fmt', 'yuv420p',
                '-g', '60',                     # Keyframes every 2s
                '-c:a', 'aac', 
                '-b:a', '128k', 
                '-ar', '44100',
                '-f', 'flv', f"{STREAM_URL}{STREAM_KEY}"
            ]

            process = subprocess.Popen(cmd)
            process.wait() 
            
            # Reset index if at the end of the list
            if i == len(VIDEO_LINKS) - 1:
                save_index(0)

        print("Playlist finished. Restarting...")
        time.sleep(2)

if __name__ == "__main__":
    start_streaming()
