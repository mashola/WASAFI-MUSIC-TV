import subprocess
import time
import os
import requests

# --- CONFIGURATION ---
# Add your Hugging Face video links here
VIDEO_LINKS = [
    "https://huggingface.co/datasets/MASHOLA/YOUTUBE/resolve/main/VIDEOS/WASAFI%20MUSIC%20TV.mp4?download=true",
    " "
]

STREAM_URL = "rtmp://a.rtmp.youtube.com/live2/"
STREAM_KEY = os.getenv("STREAM_KEY") 
STATE_FILE = "state.txt"

def download_file(url, local_filename):
    if not os.path.exists(local_filename):
        print(f"Downloading: {local_filename}...")
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print("Download complete.")

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
    while True:
        current_index = get_last_index()
        
        for i in range(current_index, len(VIDEO_LINKS)):
            save_index(i)
            local_video = f"video_{i}.mp4"
            
            # Download the video locally to prevent buffering
            try:
                download_file(VIDEO_LINKS[i], local_video)
            except Exception as e:
                print(f"Error downloading video {i}: {e}")
                continue

            print(f"Now Streaming: {local_video}")

            # FFmpeg Command for Video Streaming
            # -stream_loop -1 is NOT used here so that Python can manage the list
            cmd = [
                'ffmpeg',
                '-re',                          # Read at native frame rate
                '-i', local_video,              # Input local file
                '-c:v', 'libx264',              # Re-encode to ensure stability
                '-preset', 'veryfast', 
                '-b:v', '3500k',                # High quality bitrate
                '-maxrate', '3500k', 
                '-bufsize', '7000k',
                '-pix_fmt', 'yuv420p',
                '-g', '60',                     # Keyframe every 2 seconds for YouTube
                '-c:a', 'aac', 
                '-b:a', '128k', 
                '-ar', '44100',
                '-f', 'flv', f"{STREAM_URL}{STREAM_KEY}"
            ]

            process = subprocess.Popen(cmd)
            process.wait() 
            
            # Reset to first video if we finished the list
            if i == len(VIDEO_LINKS) - 1:
                save_index(0)

        time.sleep(2)

if __name__ == "__main__":
    start_streaming()
