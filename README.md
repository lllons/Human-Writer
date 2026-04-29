# 💧 Drip Writer — Web App

Types your text into any window at human-like speed.

## Setup

```bash
# Install dependencies
pip install flask pyautogui

# On Fedora, also run:
sudo dnf install python3-tkinter

# If on Wayland, switch to Xorg session at login (recommended)
# or run: export DISPLAY=:0
```

## Run

```bash
cd drip-writer
python app.py
```

Then open **http://localhost:5000** in your browser.

## How to use

1. Paste your text into the box
2. Adjust speed settings if needed
3. Click **▶ start typing**
4. During the countdown — click into the window where you want text typed
5. Watch it type!

## Failsafe

Move your mouse to the **top-left corner** of your screen at any time to instantly abort.

## Cross-platform notes

- **Linux (Fedora/Ubuntu)**: Needs Xorg session. Run `sudo dnf install python3-tkinter`
- **macOS**: Grant Accessibility permissions in System Settings → Privacy & Security → Accessibility
- **Windows**: Works out of the box
