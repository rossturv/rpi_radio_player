import subprocess
import time
import os
import signal
import glob

RADIO_URL = "https://azuracast.turvilleweb.com/listen/rcm_radio/radio.mp3"
BACKUP_FOLDER = "/home/radio/radio_backup/"
CHECK_HOST = "8.8.8.8"  # Google DNS
INTERNET_TIMEOUT = 60  # seconds
CHECK_INTERVAL = 5  # seconds


def set_audio_output():
    """Try several methods to force audio to 3.5mm jack, but don't fail if not possible."""
    methods = [
        ["amixer", "cset", "numid=3", "1"],  # Older Pi
        ["amixer", "-c", "0", "sset", "Headphone", "100%"],  # Newer Pi
        ["raspi-config", "nonint", "do_audio", "1"],  # Pi OS tool
    ]
    for cmd in methods:
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Audio output set using: {' '.join(cmd)}")
            return
        except Exception:
            continue
    print("Warning: Could not set audio output to 3.5mm jack. Audio may not play on the intended device.")

def play_stream():
    # Start mpv as a subprocess for the stream
    return subprocess.Popen(["mpv", "--no-video", "--audio-device=alsa/plughw:0,0", RADIO_URL])

def play_local_files():
    # Play all supported files in BACKUP_FOLDER in a loop
    exts = ("*.mp3", "*.m4a", "*.flac")
    files = []
    for ext in exts:
        files.extend(glob.glob(os.path.join(BACKUP_FOLDER, ext)))
    if not files:
        print("No backup files found!")
        time.sleep(10)
        return None
    # Use mpv to play multiple files in sequence, looping
    return subprocess.Popen(["mpv", "--no-video", "--audio-device=alsa/plughw:0,0", "--loop=inf"] + files)

def check_internet():
    # Returns True if internet is up, False otherwise
    try:
        subprocess.check_call(["ping", "-c", "1", "-W", "2", CHECK_HOST], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    set_audio_output()
    last_online = time.time()
    playing_stream = True
    proc = play_stream()
    while True:
        try:
            online = check_internet()
            now = time.time()
            if online:
                last_online = now
                if not playing_stream:
                    print("Internet restored. Switching to stream.")
                    if proc:
                        proc.terminate()
                        proc.wait()
                    proc = play_stream()
                    playing_stream = True
            else:
                if playing_stream and (now - last_online > INTERNET_TIMEOUT):
                    print("Internet down for over a minute. Switching to backup files.")
                    if proc:
                        proc.terminate()
                        proc.wait()
                    proc = play_local_files()
                    playing_stream = False
            # Check if current player is still running
            if proc and proc.poll() is not None:
                print("Player stopped unexpectedly. Restarting...")
                if playing_stream:
                    proc = play_stream()
                else:
                    proc = play_local_files()
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("Exiting...")
            if proc:
                proc.terminate()
            return

if __name__ == "__main__":
    main() 