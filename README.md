<div align="center">

# 💧 Human Writer

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](#requirements)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#license)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](#installation)

**An ultra-human typing simulator with a live mid-type humaniser.**

[Overview](#overview) • [Quick Start](#quick-start) • [Features](#features) • [Installation](#installation) • [Usage](#usage) • [Configuration](#configuration)

</div>

---

## 📖 Overview

**Human Writer** takes your text as input and replays it keystroke by keystroke into whatever window has focus. Rather than typing at a fixed speed, it moves through distinct phases — slow, fast, and unpredictable — and introduces the kinds of imperfections that characterize real human typing: adjacent-key errors, brief hesitations, partial deletions, and second-guessing. 

**Ultra-human Edition:** This version introduces the **Live Humaniser Engine**. As the script types, it actively scans for overly formal words, corporate bloat, or uncontracted phrases. When it hits a match, it pauses (simulating an "oh wait" realization), backspaces the formal phrase, and retypes a natural, casual alternative.

All behavior is controlled through a set of named constants at the top of the file. No configuration files, no arguments — just edit the values and run.

---

## 🚀 Quick Start

**Windows (PowerShell):**
```powershell

irm [https://raw.githubusercontent.com/lllons/Human-Writer/main/app.py](https://raw.githubusercontent.com/lllons/Human-Writer/main/app.py) -OutFile app.py; python app.py
```
MacOS/Linux
```powershell
Linux / Mac:Bashcurl -O [https://raw.githubusercontent.com/lllons/Human-Writer/main/app.py](https://raw.githubusercontent.com/lllons/Human-Writer/main/app.py) && python3 app.py
```
> Requires [Python 3.6+](https://www.python.org/).

## ✨ Features
* **🧠 Live Humaniser:** Swaps formal text (e.g., *utilize* → *use*) and corporate bloat for casual language mid-type.
* **⏱️ Dynamic Speed:** Transitions through slow, fast, and random phases with realistic micro-pauses.
* **🐛 Typo Simulation:** Occasionally hits neighboring keys and auto-corrects after a brief pause.
* **🤔 Rethinks:** Simulates "second-guessing" by deleting and retyping phrases unchanged.
* **☕ Natural Breaks:** Random pauses based on character or sentence count thresholds.

## 🛠️ Installation & Usage
```bash
pip install pyautogui --user
python3 dripapp.py
Input: Paste text and press Enter twice.

Target: Focus your destination window during the countdown.

🛑 Failsafe: Move mouse to top-left corner to abort immediately.

Linux Note: Requires X11/Xorg; Wayland is not supported.

⚙️ Configuration
Tweak variables like LIVE_SWAP_CHANCE, TYPO_CHANCE, and RETHINK_WORD_CHANCE at the top of the script to adjust behavior.

Python
# Live Humaniser config
LIVE_SWAP_CHANCE       = 0.70   # Probability of swapping when a formal word is found
LIVE_SWAP_REALISE      = (0.5, 1.5) # Pause BEFORE backspacing starts ("oh woops" moment)

# Deletion depth on plain rethinks (retyping the same word)
RETHINK_WORD_MAX_BS    = 8      # Maximum characters deleted on a word rethink
RETHINK_SENT_MAX_BS    = 8      # Maximum characters deleted on a sentence rethink

# Rethink frequency
RETHINK_WORD_CHANCE    = 0.08   # Probability per word
RETHINK_SENT_CHANCE    = 0.01   # Probability per sentence

# Typo rate
TYPO_CHANCE            = 0.04   # Probability per character (0 = disabled)

# Break schedule
BREAK_EVERY_SENTS      = 5      # Break after this many sentences
BREAK_EVERY_CHARS      = 200    # Or after this many characters
BREAK_DURATION         = (3, 20)# Duration in seconds, chosen randomly
Tuning GuideVariableLower Value EffectHigher Value EffectLIVE_SWAP_CHANCE0.15 = Rare, subtle naturalization0.80 = Swaps almost every formal phrase it findsRETHINK_WORD_MAX_BSTrims one or two charactersDeletes entire wordsRETHINK_SENT_MAX_BSMinor end-of-sentence correctionsRemoves several wordsRETHINK_WORD_CHANCERethinks are rareFrequent word-level deletionsTYPO_CHANCEClean, accurate typingHigh error rate, constantly fixing mistakes📋 RequirementsPython 3.6 or higherpyautogui moduleX11 display server (for Linux users)📄 LicenseThis project is licensed under the MIT License.
