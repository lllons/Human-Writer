💧 Drip Writer

A Python script that types your text at your cursor — slowly, then fast, then chaotically — mimicking real human typing patterns.

Paste in your full document, position your cursor, and watch it go. Includes realistic typos with self-correction, word and sentence rethinks (delete a few chars and retype), randomised speed phases, and scheduled breaks. All behaviour is tunable via constants at the top of the file.

Features
• Slow → fast → random speed phases
• QWERTY-aware typos that get noticed and fixed
• Word and sentence rethinks with configurable backspace depth
• Automatic breaks every N sentences or characters
• PyAutoGUI failsafe (move mouse to top-left to abort)

Requirements
pip install pyautogui

Note: requires X11 on Linux (not Wayland). Run python3 drip_writer.py, paste your text, press Enter twice, then click into your target window before the countdown ends.
