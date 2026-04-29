#!/usr/bin/env python3
"""
Drip Writer - Web App Backend
Run: python app.py
Then open: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify
import pyautogui
import time
import random
import threading
import sys

app = Flask(__name__)

# Global state
typing_thread = None
stop_flag = threading.Event()
status = {"running": False, "progress": 0, "total": 0, "phase": "idle"}

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0

SPECIAL = {'\n': 'enter', '\t': 'tab'}


def delay_for(index, slow_chars, fast_chars, slow_min, slow_max,
              fast_min, fast_max, rand_min, rand_max,
              burst_chance, pause_chance, pause_min, pause_max):
    if index < slow_chars:
        t = random.uniform(slow_min, slow_max)
    elif index < slow_chars + fast_chars:
        t = random.uniform(fast_min, fast_max)
    else:
        if random.random() < burst_chance:
            return 0.0
        t = random.uniform(rand_min, rand_max)

    if random.random() < pause_chance:
        t += random.uniform(pause_min, pause_max)

    return t


def type_text(text, config):
    global status
    total = len(text)
    status["total"] = total
    status["running"] = True
    status["progress"] = 0

    slow_chars  = config["slow_chars"]
    fast_chars  = config["fast_chars"]

    for i, ch in enumerate(text):
        if stop_flag.is_set():
            break

        if i < slow_chars:
            status["phase"] = "slow"
        elif i < slow_chars + fast_chars:
            status["phase"] = "fast"
        else:
            status["phase"] = "random"

        if ch in SPECIAL:
            pyautogui.press(SPECIAL[ch])
        elif ch == '\r':
            pass
        else:
            try:
                pyautogui.write(ch, interval=0)
            except Exception:
                pyautogui.hotkey('shift', ch)

        status["progress"] = i + 1
        d = delay_for(
            i,
            slow_chars, fast_chars,
            config["slow_min"], config["slow_max"],
            config["fast_min"], config["fast_max"],
            config["rand_min"], config["rand_max"],
            config["burst_chance"], config["pause_chance"],
            config["pause_min"], config["pause_max"],
        )
        if d > 0:
            time.sleep(d)

    status["running"] = False
    status["phase"] = "done" if not stop_flag.is_set() else "stopped"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start():
    global typing_thread, stop_flag, status

    if status["running"]:
        return jsonify({"error": "Already running"}), 400

    data = request.json
    text = data.get("text", "")
    if not text.strip():
        return jsonify({"error": "No text provided"}), 400

    config = {
        "slow_chars":   int(data.get("slow_chars", 80)),
        "fast_chars":   int(data.get("fast_chars", 200)),
        "slow_min":     float(data.get("slow_min", 0.08)),
        "slow_max":     float(data.get("slow_max", 0.22)),
        "fast_min":     float(data.get("fast_min", 0.01)),
        "fast_max":     float(data.get("fast_max", 0.05)),
        "rand_min":     float(data.get("rand_min", 0.00)),
        "rand_max":     float(data.get("rand_max", 0.18)),
        "burst_chance": float(data.get("burst_chance", 0.12)),
        "pause_chance": float(data.get("pause_chance", 0.04)),
        "pause_min":    float(data.get("pause_min", 0.3)),
        "pause_max":    float(data.get("pause_max", 1.2)),
    }

    countdown = int(data.get("countdown", 5))
    stop_flag.clear()
    status = {"running": False, "progress": 0, "total": len(text), "phase": "countdown"}

    def run():
        time.sleep(countdown)
        type_text(text, config)

    typing_thread = threading.Thread(target=run, daemon=True)
    typing_thread.start()
    return jsonify({"ok": True, "total": len(text)})


@app.route("/stop", methods=["POST"])
def stop():
    stop_flag.set()
    status["running"] = False
    status["phase"] = "stopped"
    return jsonify({"ok": True})


@app.route("/status")
def get_status():
    return jsonify(status)


if __name__ == "__main__":
    print("\n  💧 Drip Writer")
    print("  Open http://localhost:5000 in your browser\n")
    app.run(debug=False, port=5000)
