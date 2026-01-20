import os
import subprocess
import time

# --- CONFIGURATION ---
# IMPORTANT: Ensure your HF repo is PUBLIC or add your token to these URLs
AUDIO_URL = "https://huggingface.co/datasets/MASHOLA/YOUTUBE/resolve/main/MUSIC/WASAFI%20MUSIC%20RADIO.wav?download=true"
IMAGE_URL = "https://huggingface.co/datasets/MASHOLA/YOUTUBE/resolve/main/IMAGES/WASAFI%20MUSIC%20RADIO.png?download=true"

STREAM_KEY = "3zy9-9xek-e8vu-ef3z-c77u"
STREAM_URL = "rtmp://a.rtmp.youtube.com/live2"
DESTINATION = f"{STREAM_URL}/{STREAM_KEY}"

def start_stream():
    cmd = [
        'ffmpeg',
        '-re',
        '-loop', '1', '-i', IMAGE_URL,          # Loops image
        '-stream_loop', '-1', '-i', AUDIO_URL,  # LOOPS AUDIO FOREVER (-1)
        '-map', '0:v:0',
        '-map', '1:a:0',
        '-c:v', 'libx264', 
        '-preset', 'ultrafast', 
        '-tune', 'stillimage',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', 
        '-b:a', '128k', 
        '-ar', '44100',
        '-f', 'flv', 
        DESTINATION
    ]

    while True:
        print(f"Stream started/restarted at: {time.ctime()}")
        try:
            # This will run until the GitHub 6-hour limit kills it
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError:
            print("Connection lost. Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    start_stream()
