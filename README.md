# Raspberry Pi Radio Watchdog

This script auto-plays a radio stream on your Raspberry Pi and automatically switches to local backup audio files if the internet connection is lost for more than a minute. When the connection is restored, it resumes the stream. It is designed for robust, unattended operation and outputs audio over the 3.5mm headphone jack.

A sample radio stream has been entered for testing purposes and the user 'radio' is used in the scripts, change as appropriate.

## Features
- Auto-plays a specified radio stream on boot
- Monitors internet connection and stream health
- Plays local `.mp3`, `.m4a`, and `.flac` files from a backup folder if the stream is unavailable
- Automatically switches back to the stream when the connection is restored
- Designed for Raspberry Pi OS (Lite or Desktop)
- Outputs audio over the 3.5mm jack (headphone port)

---

## Requirements
- Raspberry Pi running Raspberry Pi OS
- 3.5mm speakers or headphones connected
- Internet connection (for streaming)

### Dependencies
Install these packages:
```sh
sudo apt-get update
sudo apt-get install mpv python3 python3-pip alsa-utils
```

---

## Setup Instructions

### 1. Place the Script
Move `radio_watchdog.py` to your desired location, e.g. `/home/radio/radio_watchdog.py`.

### 2. Create the Backup Folder
Create a folder for backup audio files:
```sh
sudo mkdir -p /home/radio/radio_backup/
sudo chown -R radio:radio /home/radio/
```
Add your `.mp3`, `.m4a`, or `.flac` files to `/home/radio/radio_backup/`.

### 3. Make the Script Executable
```sh
chmod +x /home/radio/radio_watchdog.py
```

### 4. Create the systemd Service
Create `/etc/systemd/system/radio_watchdog.service` with the following content (adjust paths and user as needed):

```
[Unit]
Description=Raspberry Pi Radio Watchdog
After=network.target sound.target

[Service]
ExecStart=/usr/bin/python3 /home/radio/radio_watchdog.py
Restart=always
User=radio

[Install]
WantedBy=multi-user.target
```

### 5. Enable and Start the Service
```sh
sudo systemctl daemon-reload
sudo systemctl enable radio_watchdog
sudo systemctl start radio_watchdog
```

### 6. Test Audio Output
To test audio output through the 3.5mm jack:
```sh
sudo -u radio aplay -D plughw:0,0 /usr/share/sounds/alsa/Front_Center.wav
```
You should hear "Front Center" from your speakers/headphones.

---

## Troubleshooting
- **No audio output:**
  - Ensure your user (`radio` shown in this example) is in the `audio` group:
    ```sh
    sudo usermod -aG audio radio
    sudo reboot
    ```
  - Make sure your speakers/headphones are plugged into the 3.5mm jack.
  - Check that the script uses `--audio-device=alsa/plughw:0,0` in the `mpv` command.
  - Test with `aplay` as above.
- **Audio device errors:**
  - Run `aplay -l` to list available devices. The 3.5mm jack should appear as `card 0`.
- **Stream not playing:**
  - Check your internet connection.
  - Check the stream URL in the script.
- **Backup files not playing:**
  - Ensure there are supported audio files in `/home/radio/radio_backup/`.

---

## Customization
- **Change the stream URL:** Edit the `RADIO_URL` variable in `radio_watchdog.py`.
- **Change the backup folder:** Edit the `BACKUP_FOLDER` variable in `radio_watchdog.py`.
- **Supported formats:** Add more file extensions in the script if needed.

---

## Credits
Created by Ross Turville - [turvilleweb.com](https://turvilleweb.com)

---

## License
This project is open source and licensed under the MIT License. See the LICENSE file for details. 
