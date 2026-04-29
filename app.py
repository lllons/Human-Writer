#!/usr/bin/env python3
"""
Drip Writer - Ultra-human typing simulator.
Requires: pip install pyautogui
"""

import pyautogui
import time
import random
import sys
import re

# ── Safety ───────────────────────────────────────────────────────────────────
pyautogui.FAILSAFE = True
pyautogui.PAUSE    = 0

# ── Config ────────────────────────────────────────────────────────────────────
COUNTDOWN            = 5        # Seconds to position your cursor

# Speed phases
SLOW_CHARS           = 60       # First N chars: slow warm-up
FAST_CHARS           = 150      # Next M chars: fast flow
SLOW_MIN, SLOW_MAX   = 0.07, 0.25
FAST_MIN, FAST_MAX   = 0.01, 0.06
RAND_MIN, RAND_MAX   = 0.00, 0.15

# Breaks
BREAK_EVERY_CHARS    = 200      # Break after ~N chars typed
BREAK_EVERY_SENTS    = 5        # OR after N sentences (whichever hits first)
BREAK_DURATION       = (25, 35) # Break length in seconds

# Micro-pauses (mid-sentence thinking)
MICRO_PAUSE_CHANCE   = 0.06
MICRO_PAUSE_DUR      = (0.4, 2.0)

# Typos
TYPO_CHANCE          = 0.045    # Per character
TYPO_NOTICE_DELAY    = (0.1, 0.5)
TYPO_FIX_DELAY       = (0.04, 0.14)

# Rethinks (delete & retype)
RETHINK_WORD_CHANCE  = 0.03     # Per word
RETHINK_SENT_CHANCE  = 0.04     # Per sentence
RETHINK_PAUSE        = (0.6, 2.5)

# Burst typing (no delay)
BURST_CHANCE         = 0.10

# QWERTY neighbour map for realistic typos
NEIGHBORS = {
    'a':'sqwz','b':'vghn','c':'xdfv','d':'serfcx','e':'wrds',
    'f':'drtgvc','g':'ftyhbv','h':'gyujnb','i':'ujko',
    'j':'huikmn','k':'jiolm','l':'kop;','m':'njk',
    'n':'bhjm','o':'iklp','p':'ol;','q':'wa',
    'r':'edft','s':'awedxz','t':'rfgy','u':'yhji',
    'v':'cfgb','w':'qase','x':'zsdc','y':'tghu','z':'asx',
}

SPECIAL = {'\n': 'enter', '\t': 'tab'}


# ── Low-level helpers ─────────────────────────────────────────────────────────
def tap(ch):
    if ch in SPECIAL:
        pyautogui.press(SPECIAL[ch])
    elif ch == '\r':
        return
    else:
        try:
            pyautogui.write(ch, interval=0)
        except Exception:
            pass


def backspace(n, fast=False):
    for _ in range(n):
        pyautogui.press('backspace')
        if not fast:
            time.sleep(random.uniform(0.04, 0.13))


def char_delay(idx):
    if idx < SLOW_CHARS:
        t = random.uniform(SLOW_MIN, SLOW_MAX)
    elif idx < SLOW_CHARS + FAST_CHARS:
        t = random.uniform(FAST_MIN, FAST_MAX)
    else:
        if random.random() < BURST_CHANCE:
            return 0.0
        t = random.uniform(RAND_MIN, RAND_MAX)
    if random.random() < MICRO_PAUSE_CHANCE:
        t += random.uniform(*MICRO_PAUSE_DUR)
    return t


def wrong_key(ch):
    pool = NEIGHBORS.get(ch.lower(), '')
    if pool:
        w = random.choice(pool)
        return w.upper() if ch.isupper() else w
    return random.choice('etaoinsrhl')


# ── Break ─────────────────────────────────────────────────────────────────────
def do_break(n):
    dur = random.uniform(*BREAK_DURATION)
    print(f"\n  ☕  Break #{n}  —  {dur:.0f}s ...", end='', flush=True)
    time.sleep(dur)
    print("  back.")
    time.sleep(random.uniform(0.5, 1.5))


# ── Word typer ────────────────────────────────────────────────────────────────
def type_word(word, gidx):
    """Type a word. May rethink (delete + retype) or produce typos."""

    # Rethink: type it, pause, delete it, retype
    if random.random() < RETHINK_WORD_CHANCE and len(word) > 2:
        for i, ch in enumerate(word):
            tap(ch)
            time.sleep(char_delay(gidx + i))
        time.sleep(random.uniform(*RETHINK_PAUSE))
        backspace(len(word))
        time.sleep(random.uniform(0.15, 0.5))
        for i, ch in enumerate(word):
            tap(ch)
            time.sleep(char_delay(gidx + i) * 0.75)
        return len(word)

    # Normal with possible typo
    typed = 0
    for ch in word:
        if ch.isalpha() and random.random() < TYPO_CHANCE:
            tap(wrong_key(ch))
            time.sleep(random.uniform(*TYPO_NOTICE_DELAY))
            backspace(1, fast=True)
            time.sleep(random.uniform(*TYPO_FIX_DELAY))
            tap(ch)
        else:
            tap(ch)
        time.sleep(char_delay(gidx + typed))
        typed += 1
    return typed


# ── Sentence typer ────────────────────────────────────────────────────────────
def type_sentence(sentence, gidx):
    """Type a sentence. May rethink (delete entire sentence + retype)."""
    tokens = re.split(r'(\s+)', sentence)   # words + whitespace tokens

    def _type_tokens(speed_factor=1.0):
        chars = 0
        for tok in tokens:
            if tok.strip():
                chars += type_word(tok, gidx + chars)
            else:
                for ch in tok:
                    tap(ch)
                    time.sleep(char_delay(gidx + chars) * speed_factor)
                    chars += 1
        return chars

    # Rethink entire sentence
    if random.random() < RETHINK_SENT_CHANCE and len(sentence) > 20:
        typed = _type_tokens()
        time.sleep(random.uniform(*RETHINK_PAUSE))
        backspace(typed, fast=False)
        time.sleep(random.uniform(0.3, 0.9))
        return _type_tokens(speed_factor=0.7)   # Retype a bit faster

    return _type_tokens()


# ── Main loop ─────────────────────────────────────────────────────────────────
def split_sentences(text):
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p for p in parts if p.strip()]


def type_text(text):
    sentences        = split_sentences(text)
    total            = len(sentences)
    gidx             = 0
    sent_since_break = 0
    char_since_break = 0
    break_num        = 0

    for i, sent in enumerate(sentences):
        n = type_sentence(sent, gidx)
        gidx             += n
        char_since_break += n
        sent_since_break += 1

        # Space between sentences
        if i < total - 1:
            tap(' ')
            time.sleep(random.uniform(0.05, 0.22))
            gidx             += 1
            char_since_break += 1

        # Break trigger
        hit_chars = char_since_break >= BREAK_EVERY_CHARS
        hit_sents = sent_since_break >= BREAK_EVERY_SENTS
        if (hit_chars or hit_sents) and i < total - 1:
            break_num       += 1
            char_since_break = 0
            sent_since_break = 0
            do_break(break_num)


# ── Entry ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 56)
    print("  💧  DRIP WRITER  —  ultra-human edition")
    print("=" * 56)
    print("  Paste your text below.")
    print("  End with a BLANK LINE (press Enter twice).\n")

    lines = []
    try:
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                lines.pop()
                break
            lines.append(line)
    except EOFError:
        pass

    text = "\n".join(lines).strip()
    if not text:
        print("\n  No text entered. Exiting.")
        sys.exit(0)

    sents      = split_sentences(text)
    est_breaks = max(0, len(sents) // BREAK_EVERY_SENTS - 1)

    print(f"\n  {len(text):,} chars  |  ~{len(sents)} sentences  |  ~{est_breaks} breaks")
    print(f"  Break: {BREAK_DURATION[0]}–{BREAK_DURATION[1]}s every "
          f"{BREAK_EVERY_SENTS} sentences or {BREAK_EVERY_CHARS} chars")
    print(f"  Typo: {TYPO_CHANCE*100:.0f}%  |  "
          f"Word rethink: {RETHINK_WORD_CHANCE*100:.0f}%  |  "
          f"Sentence rethink: {RETHINK_SENT_CHANCE*100:.0f}%")
    print(f"\n  FAILSAFE: move mouse to TOP-LEFT corner to abort!\n")

    # Countdown
    print(f"  Click into your target window NOW.\n")
    for i in range(COUNTDOWN, 0, -1):
        print(f"  Starting in {i}...", end="\r", flush=True)
        time.sleep(1)
    print("  Typing!              ")

    type_text(text)
    print("\n\n  ✅  Done!")


if __name__ == "__main__":
    main()
