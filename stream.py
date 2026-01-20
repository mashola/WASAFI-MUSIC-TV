import os
import subprocess
import time

# --- CONFIGURATION ---
# Replace with your token or make the repo Public
HF_TOKEN = "YOUR_HF_TOKEN" 

AUDIO_URL = f"https://huggingface.co/datasets/MASHOLA/YOUTUBE/resolve/main/MUSIC/WASAFI%20MUSIC%20RADIO.wav?download=true&token={HF_TOKEN}"
IMAGE_URL = f"https://huggingface.co/datasets/MASHOLA/YOUTUBE/resolve/main/IMAGES/WASAFI%20MUSIC%20RADIO.png?download=true&token={HF_TOKEN}"

STREAM_KEY = "3zy9-9xek-e8vu-ef3z-c77u"
STREAM_URL = "rtmp://a.rtmp.youtube.com/live2"
DESTINATION = f"{STREAM_URL}/{STREAM_KEY}"

def start_stream():
    # Streamlined command for lower CPU usage
    cmd = [
        'ffmpeg',
        '-re',                         # Read input at native frame rate
        '-loop', '1',                  # Loop the static image
        '-i', IMAGE_URL,
        '-i', AUDIO_URL,
        '-c:v', 'libx264',             # Video codec
        '-preset', 'ultrafast',        # Use 'ultrafast' to save GitHub CPU
        '-tune', 'stillimage',         # Optimization for static images
        '-pix_fmt', 'yuv420p',         # Required for YouTube compatibility
        '-c:a', 'aac',                 # Audio codec
        '-b:a', '128k',                # Audio bitrate
        '-shortest',                   # End stream if audio stops (though we loop)
        '-f', 'flv', 
        DESTINATION
    ]

    while True:
        print(f"Starting Lite Stream: {time.ctime()}")
        try:
            # We use 'stream_loop -1' logic inside the loop or let the script restart
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Stream paused. Restarting in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    start_stream()
