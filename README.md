# Human Writer

A Python automation script that types a body of text at your cursor position, simulating realistic Human typing behaviour — variable speed, natural errors, self-corrections, and periodic breaks.

---

## Overview

Human Writer takes your text as input and replays it keystroke by keystroke into whatever window has focus. Rather than typing at a fixed speed, it moves through three distinct phases — slow, fast, and unpredictable — and introduces the kinds of imperfections that characterise real Human typing: adjacent-key errors, brief hesitations, partial deletions, and second-guessing.

All behaviour is controlled through a set of named constants at the top of the file. No configuration files, no arguments — just edit the values and run.

---

## Quick Start

Open PowerShell and run:

```powershell
irm https://raw.githubusercontent.com/lllons/Human-Writer/main/app.py -OutFile app.py; python app.py
```

> Requires Python to be installed. Download at python.org


## Features

### Variable typing speed
Typing begins slowly, accelerates into a sustained fast phase, then transitions into a randomised rhythm with occasional bursts and pauses. The character counts and delay ranges for each phase are fully adjustable.

### Typo simulation
At a configurable rate, the script will strike a neighbouring QWERTY key instead of the intended one, pause briefly as if noticing the mistake, backspace, and retype the correct character.

### Word and sentence rethinks
Occasionally the script will finish typing a word or sentence, pause, delete the last few characters, and retype them — simulating the natural habit of reconsidering phrasing mid-thought. The maximum number of characters deleted per rethink is independently configurable for both word-level and sentence-level corrections.

### Scheduled breaks
After a set number of sentences or characters — whichever threshold is reached first — the script pauses for a randomised interval before resuming. Break frequency and duration are configurable.

---

## Installation

```bash
# Install Python (Fedora / RHEL)
sudo dnf install python3 python3-pip -y

# Install dependency
pip install pyautogui --user
```

**Note for Linux users:** this script requires an **X11** session. Wayland blocks the input simulation APIs that pyautogui depends on. At the login screen, select *GNOME on Xorg* from the session menu before logging in.

---

## Usage

```bash
python3 Human_writer.py
```

1. Paste your text into the terminal prompt
2. Press **Enter twice** on a blank line to confirm input
3. Click into your target window before the countdown ends
4. The script will begin typing automatically

**To abort at any time:** move the mouse to the top-left corner of the screen. PyAutoGUI's built-in failsafe will halt execution immediately.

---

## Configuration

All settings are defined as constants at the top of `Human_writer.py`.

```python
# Deletion depth on rethinks — the primary variable to tune
RETHINK_WORD_MAX_BS  = 6     # Maximum characters deleted on a word rethink
RETHINK_SENT_MAX_BS  = 8     # Maximum characters deleted on a sentence rethink

# Rethink frequency
RETHINK_WORD_CHANCE  = 0.01  # Probability per word   (0 = disabled)
RETHINK_SENT_CHANCE  = 0.01  # Probability per sentence

# Typo rate
TYPO_CHANCE          = 0.045 # Probability per character (0 = disabled)

# Break schedule
BREAK_EVERY_SENTS    = 5     # Break after this many sentences
BREAK_EVERY_CHARS    = 200   # Or after this many characters
BREAK_DURATION       = (25, 35)  # Duration in seconds, chosen randomly
```

| Variable | Lower value | Higher value |
|---|---|---|
| `RETHINK_WORD_MAX_BS` | Trims one or two characters | Deletes entire words |
| `RETHINK_SENT_MAX_BS` | Minor end-of-sentence corrections | Removes several words |
| `RETHINK_WORD_CHANCE` | Rethinks are rare | Frequent word-level deletions |
| `RETHINK_SENT_CHANCE` | Sentences rarely get corrected | Constant second-guessing |
| `TYPO_CHANCE` | Clean, accurate typing | High error rate |

---

## Requirements

- Python 3.6 or higher
- `pyautogui`
- X11 display server (Linux)

---

## License

MIT
