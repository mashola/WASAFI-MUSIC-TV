import os
import subprocess
import time

# --- CONFIGURATION ---
AUDIO_URL = "https://huggingface.co/datasets/MASHOLA/YOUTUBE/resolve/main/MUSIC/WASAFI%20MUSIC%20RADIO.wav?download=true"
IMAGE_URL = "https://huggingface.co/datasets/MASHOLA/YOUTUBE/resolve/main/IMAGES/WASAFI%20MUSIC%20RADIO.png?download=true"
STREAM_KEY = "3zy9-9xek-e8vu-ef3z-c77u"
STREAM_URL = "rtmp://a.rtmp.youtube.com/live2"

DESTINATION = f"{STREAM_URL}/{STREAM_KEY}"

def start_stream():
    # FFmpeg Command Breakdown:
    # 1. -loop 1 -i IMAGE: Loops the static image
    # 2. -i AUDIO: The live audio source
    # 3. showwavespic: Creates the spectrum visualizer
    # 4. filter_complex: Merges image and visualizer with 10% transparency (alpha 0.1)
    
    cmd = [
        'ffmpeg',
        '-re',
        '-loop', '1', '-i', IMAGE_URL,
        '-i', AUDIO_URL,
        '-filter_complex', 
        "[1:a]showwaves=s=1280x200:mode=line:colors=white@0.1[v_spec];" +  # 10% transparency (@0.1)
        "[0:v][v_spec]overlay=0:H-h:format=auto,format=yuv420p[outv]",
        '-map', '[outv]',
        '-map', '1:a',
        '-c:v', 'libx264', '-preset', 'veryfast', '-b:v', '2500k',
        '-c:a', 'aac', '-b:a', '128k',
        '-f', 'flv', DESTINATION
    ]

    while True:
        print(f"Starting Stream: {time.ctime()}")
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Stream interrupted: {e}. Restarting in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    start_stream()
