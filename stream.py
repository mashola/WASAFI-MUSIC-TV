import os
import subprocess
import time

# --- CONFIGURATION ---
# These filenames must match the ones downloaded in the YAML file
IMAGE_FILE = "video_bg.png"
AUDIO_FILE = "audio_track.wav"

STREAM_KEY = "3zy9-9xek-e8vu-ef3z-c77u"
STREAM_URL = "rtmps://a.rtmp.youtube.com:443/live2"
DESTINATION = f"{STREAM_URL}/{STREAM_KEY}"

def start_stream():
    # We use -stream_loop -1 to make the local audio file play forever
    cmd = [
        'ffmpeg',
        '-re',
        '-loop', '1', '-i', IMAGE_FILE,
        '-stream_loop', '-1', '-i', AUDIO_FILE,
        '-map', '0:v:0',
        '-map', '1:a:0',
        '-c:v', 'libx264', '-preset', 'ultrafast', '-tune', 'stillimage',
        '-pix_fmt', 'yuv420p', '-s', '1280x720',
        '-c:a', 'aac', '-b:a', '128k', '-ar', '44100',
        '-g', '60', 
        '-f', 'flv', 
        '-flvflags', 'no_duration_filesize',
        DESTINATION
    ]

    while True:
        print(f"Starting local file stream at: {time.ctime()}")
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError:
            print("Stream process ended. Restarting...")
            time.sleep(5)

if __name__ == "__main__":
    start_stream()
