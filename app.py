#!/usr/bin/env python3
"""
Human Writer - Ultra-human typing simulator with live mid-type humaniser.
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

# ═══════════════════════════════════════════════════════════════════════════
#  CONFIG — tweak everything here
# ═══════════════════════════════════════════════════════════════════════════

COUNTDOWN            = 5

# ── Speed phases ─────────────────────────────────────────────────────────────
SLOW_CHARS           = 60
FAST_CHARS           = 150
SLOW_MIN, SLOW_MAX   = 0.01, 0.40
FAST_MIN, FAST_MAX   = 0.0001, 0.06
RAND_MIN, RAND_MAX   = 0.00, 0.90

# ── Breaks ────────────────────────────────────────────────────────────────────
BREAK_EVERY_CHARS    = 200
BREAK_EVERY_SENTS    = 5
BREAK_DURATION       = (3, 20)

# ── Micro-pauses ──────────────────────────────────────────────────────────────
MICRO_PAUSE_CHANCE   = 0.06
MICRO_PAUSE_DUR      = (0.4, 2.0)

# ── Burst typing ─────────────────────────────────────────────────────────────
BURST_CHANCE         = 0.20

# ── Typos ─────────────────────────────────────────────────────────────────────
TYPO_CHANCE          = 0.04
TYPO_NOTICE_DELAY    = (0.1, 0.8)
TYPO_FIX_DELAY       = (0.04, 0.14)

# ── Word rethink (deletes and retypes the same word unchanged) ────────────────
RETHINK_WORD_CHANCE  = 0.08
RETHINK_WORD_MAX_BS  = 8

# ── Sentence rethink (deletes end of sentence and retypes unchanged) ──────────
RETHINK_SENT_CHANCE  = 0.01
RETHINK_SENT_MAX_BS  = 8

RETHINK_PAUSE        = (0.6, 2.5)

# ── Live humaniser swap config ────────────────────────────────────────────────
#
# After the typer finishes a word or phrase it checks whether it just typed
# something swappable.  If the dice rolls yes it pauses (the "oh wait" moment),
# backspaces the original out, then retypes the casual replacement.
#
LIVE_SWAP_CHANCE       = 0.70   # Probability of swapping when a match is found.
                                 # 0.15 = rare/natural, 0.35 = noticeable,
                                 # 0.60 = swaps most things it can.

LIVE_SWAP_REALISE      = (0.5, 1.5)  # Pause BEFORE backspacing starts —
                                      # the "oh woops" realisation moment.
                                      # Medium: like actually re-reading it.

LIVE_SWAP_BS_DELAY     = (0.06, 0.14) # Delay between each backspace keystroke.

LIVE_SWAP_RETYPE_SPEED = 0.7    # Multiplier on char_delay when retyping the
                                 # replacement.  <1.0 = faster (more confident
                                 # second time around).

# ═══════════════════════════════════════════════════════════════════════════
#  END CONFIG
# ═══════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════
#  HUMANISER — full replacement tables
# ═══════════════════════════════════════════════════════════════════════════

# ── Contractions (ordered longest-match first) ────────────────────────────────
CONTRACTIONS = [
    ("I am not",           "I'm not"),
    ("I am",               "I'm"),
    ("I will",             "I'll"),
    ("I would",            "I'd"),
    ("I have",             "I've"),
    ("I had",              "I'd"),
    ("he will",            "he'll"),
    ("she will",           "she'll"),
    ("he would",           "he'd"),
    ("she would",          "she'd"),
    ("he is",              "he's"),
    ("she is",             "she's"),
    ("it is not",          "it isn't"),
    ("it is",              "it's"),
    ("it would",           "it'd"),
    ("that would",         "that'd"),
    ("that is",            "that's"),
    ("there is",           "there's"),
    ("there are not",      "there aren't"),
    ("what is",            "what's"),
    ("who is",             "who's"),
    ("you are not",        "you aren't"),
    ("you are",            "you're"),
    ("you will",           "you'll"),
    ("you have",           "you've"),
    ("they are not",       "they aren't"),
    ("they are",           "they're"),
    ("they will",          "they'll"),
    ("they have",          "they've"),
    ("we are",             "we're"),
    ("we will",            "we'll"),
    ("we have",            "we've"),
    ("are not",            "aren't"),
    ("was not",            "wasn't"),
    ("were not",           "weren't"),
    ("do not",             "don't"),
    ("does not",           "doesn't"),
    ("did not",            "didn't"),
    ("would not",          "wouldn't"),
    ("could not",          "couldn't"),
    ("should not",         "shouldn't"),
    ("will not",           "won't"),
    ("cannot",             "can't"),
    ("have not",           "haven't"),
    ("has not",            "hasn't"),
    ("had not",            "hadn't"),
]

# ── Formal → casual word/phrase swaps ────────────────────────────────────────
WORD_SWAPS = [
    # Connectives
    ("however",                     "but"),
    ("therefore",                   "so"),
    ("thus",                        "so"),
    ("hence",                       "so"),
    ("nevertheless",                "still"),
    ("nonetheless",                 "still"),
    ("furthermore",                 "also"),
    ("in addition",                 "also"),
    ("additionally",                "also"),
    ("moreover",                    "on top of that"),
    ("consequently",                "so"),
    ("subsequently",                "then"),
    ("previously",                  "before"),
    ("currently",                   "right now"),
    # Verbs
    ("utilise",                     "use"),
    ("utilize",                     "use"),
    ("commence",                    "start"),
    ("initiate",                    "start"),
    ("attempt",                     "try"),
    ("endeavour",                   "try"),
    ("endeavor",                    "try"),
    ("facilitate",                  "help"),
    ("implement",                   "put in place"),
    ("leverage",                    "use"),
    ("optimise",                    "improve"),
    ("optimize",                    "improve"),
    ("prioritise",                  "focus on"),
    ("prioritize",                  "focus on"),
    ("terminate",                   "end"),
    ("cease",                       "stop"),
    ("modify",                      "change"),
    ("require",                     "need"),
    ("necessitate",                 "need"),
    ("purchase",                    "buy"),
    ("assist",                      "help"),
    ("obtain",                      "get"),
    ("acquire",                     "get"),
    ("demonstrate",                 "show"),
    ("indicate",                    "show"),
    ("ensure",                      "make sure"),
    ("provide",                     "give"),
    ("receive",                     "get"),
    ("respond",                     "reply"),
    ("request",                     "ask for"),
    ("inform",                      "tell"),
    ("acknowledge",                 "admit"),
    ("observe",                     "notice"),
    ("consider",                    "think about"),
    ("anticipate",                  "expect"),
    ("encounter",                   "run into"),
    ("possess",                     "have"),
    ("retain",                      "keep"),
    ("discard",                     "get rid of"),
    ("inquire",                     "ask"),
    ("state",                       "say"),
    ("reside",                      "live"),
    ("depart",                      "leave"),
    ("be aware of",                 "know"),
    # Adjectives / nouns
    ("sufficient",                  "enough"),
    ("inadequate",                  "not good enough"),
    ("numerous",                    "a lot of"),
    ("multiple",                    "a few"),
    ("additional",                  "more"),
    ("significant",                 "big"),
    ("substantial",                 "a lot of"),
    ("minimal",                     "very little"),
    ("problematic",                 "an issue"),
    ("beneficial",                  "helpful"),
    ("detrimental",                 "harmful"),
    ("challenging",                 "tricky"),
    ("straightforward",             "pretty simple"),
    ("complex",                     "complicated"),
    ("optimal",                     "best"),
    ("majority",                    "most"),
    ("minority",                    "a few"),
    ("category",                    "type"),
    ("component",                   "part"),
    ("objective",                   "goal"),
    ("methodology",                 "approach"),
    # Long phrases
    ("approximately",               "about"),
    ("regarding",                   "about"),
    ("concerning",                  "about"),
    ("pertaining to",               "about"),
    ("with regard to",              "about"),
    ("with respect to",             "when it comes to"),
    ("prior to",                    "before"),
    ("subsequent to",               "after"),
    ("in order to",                 "to"),
    ("at this point in time",       "now"),
    ("at this juncture",            "at this point"),
    ("in the event that",           "if"),
    ("due to the fact that",        "because"),
    ("in spite of",                 "despite"),
    ("in proximity to",             "near"),
    ("in excess of",                "more than"),
    ("less than optimal",           "not great"),
]

# ── Stuffy adverbs → casual ───────────────────────────────────────────────────
ADVERB_SWAPS = [
    ("extremely",           "really"),
    ("very significantly",  "a lot"),
    ("entirely",            "completely"),
    ("considerably",        "quite a bit"),
    ("substantially",       "a lot"),
    ("predominantly",       "mostly"),
    ("primarily",           "mainly"),
    ("particularly",        "especially"),
    ("specifically",        "in particular"),
    ("generally",           "usually"),
    ("typically",           "normally"),
    ("essentially",         "basically"),
    ("fundamentally",       "basically"),
    ("inevitably",          "always"),
    ("arguably",            "you could say"),
    ("undoubtedly",         "definitely"),
    ("certainly",           "for sure"),
    ("simultaneously",      "at the same time"),
    ("accordingly",         "so"),
]

# ── Hedging / softening phrases ───────────────────────────────────────────────
HEDGE_SWAPS = [
    ("I believe that",              "I think"),
    ("in my opinion",               "to me"),
    ("from my perspective",         "to me"),
    ("it appears that",             "it seems like"),
    ("it seems that",               "it seems like"),
    ("it is possible that",         "maybe"),
    ("there is a possibility",      "there's a chance"),
    ("one might argue",             "you could argue"),
    ("one could say",               "you could say"),
    ("it is worth considering",     "worth thinking about"),
    ("to a certain extent",         "to some degree"),
    ("in some respects",            "in some ways"),
]

# ── Bloat strip phrases (replacement "" = delete, "So," = replace) ────────────
STRIP_PHRASES = [
    ("it is worth noting that",             ""),
    ("it should be noted that",             ""),
    ("it is important to note that",        ""),
    ("it is essential to understand that",  ""),
    ("it is crucial to recognise that",     ""),
    ("it is crucial to recognize that",     ""),
    ("it goes without saying that",         ""),
    ("as previously mentioned",             ""),
    ("as stated above",                     ""),
    ("as noted earlier",                    ""),
    ("as we can see",                       ""),
    ("it is clear that",                    ""),
    ("it is evident that",                  ""),
    ("needless to say",                     ""),
    ("for the purposes of this",            ""),
    ("in light of the above",               ""),
    ("based on the foregoing",              ""),
    ("in conclusion",                       "So,"),
    ("to summarise",                        "So,"),
    ("to summarize",                        "So,"),
    ("in summary",                          "So,"),
    ("to conclude",                         "So,"),
    ("taking everything into consideration","So,"),
]

# ── Filler sentence openers ───────────────────────────────────────────────────
FILLER_OPENERS = [
    "Honestly,",
    "Basically,",
    "To be fair,",
    "I mean,",
    "Look,",
    "To be honest,",
    "The thing is,",
    "Weirdly,",
    "Actually,",
    "Funny enough,",
    "Honestly though,",
    "The weird thing is,",
    "Here's the thing —",
    "If anything,",
    "At the end of the day,",
    "That said,",
    "Which is kind of wild,",
    "Not gonna lie,",
]

# ── Sentence closers ──────────────────────────────────────────────────────────
SENTENCE_CLOSERS = [
    ", though",
    ", to be fair",
    ", honestly",
    ", which helps",
    ", which is annoying",
    ", weirdly enough",
    ", so that's something",
    ", at least",
    ", in fairness",
    ", I guess",
]


# ═══════════════════════════════════════════════════════════════════════════
#  BUILD RUNTIME LOOKUP STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════

def _build_lookups():
    """
    Flatten all swap tables into two structures:

    SINGLE_SWAPS : dict  { lowercase_word -> replacement_string }
    MULTI_SWAPS  : list  [ (tuple_of_lowercase_words, replacement_string), ... ]
                   sorted longest-phrase-first so longer matches win.
    """
    single = {}
    multi  = []

    all_tables = CONTRACTIONS + WORD_SWAPS + ADVERB_SWAPS + HEDGE_SWAPS
    strip_as_swaps = [(orig, rep if rep else "__STRIP__") for orig, rep in STRIP_PHRASES]
    all_tables += strip_as_swaps

    seen = set()
    for orig, rep in all_tables:
        key = orig.lower().strip()
        if key in seen:
            continue
        seen.add(key)
        words = key.split()
        if len(words) == 1:
            single[words[0]] = rep
        else:
            multi.append((tuple(words), rep))

    # Longest phrase first so "I am not" beats "I am"
    multi.sort(key=lambda x: -len(x[0]))
    return single, multi

SINGLE_SWAPS, MULTI_SWAPS = _build_lookups()


# ═══════════════════════════════════════════════════════════════════════════
#  LOW-LEVEL TYPER HELPERS
# ═══════════════════════════════════════════════════════════════════════════

NEIGHBORS = {
    'a':'sqwz','b':'vghn','c':'xdfv','d':'serfcx','e':'wrds',
    'f':'drtgvc','g':'ftyhbv','h':'gyujnb','i':'ujko',
    'j':'huikmn','k':'jiolm','l':'kop;','m':'njk',
    'n':'bhjm','o':'iklp','p':'ol;','q':'wa',
    'r':'edft','s':'awedxz','t':'rfgy','u':'yhji',
    'v':'cfgb','w':'qase','x':'zsdc','y':'tghu','z':'asx',
}

SPECIAL = {'\n': 'enter', '\t': 'tab'}


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
            time.sleep(random.uniform(*LIVE_SWAP_BS_DELAY))


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


def do_break(n):
    dur = random.uniform(*BREAK_DURATION)
    print(f"\n  ☕  Break #{n}  —  {dur:.0f}s ...", end='', flush=True)
    time.sleep(dur)
    print("  back.")
    time.sleep(random.uniform(0.5, 1.5))


def _preserve_case(first_original_word, replacement):
    """If the original word started with a capital, capitalise the replacement."""
    if replacement == "__STRIP__":
        return ""
    if first_original_word and first_original_word[0].isupper():
        return replacement[0].upper() + replacement[1:] if replacement else ""
    return replacement


def _retype_string(text, gidx):
    """Type a string at the confident retype speed."""
    for i, ch in enumerate(text):
        tap(ch)
        time.sleep(char_delay(gidx + i) * LIVE_SWAP_RETYPE_SPEED)


# ═══════════════════════════════════════════════════════════════════════════
#  LIVE SWAP ENGINE
# ═══════════════════════════════════════════════════════════════════════════

def attempt_live_swap(word_history, raw_word_history, gidx):
    """
    Called after each word is typed.

    word_history     : list of lowercase stripped words typed so far this sentence
    raw_word_history : matching list of the raw typed strings (preserves case/punct)

    Checks multi-word phrases first (longest first), then single words.
    If a match is found and the dice rolls yes:
      1. Pauses (the realisation moment)
      2. Backspaces the original out
      3. Retypes the replacement

    Returns True if a swap happened, False otherwise.
    """
    # ── Multi-word check ─────────────────────────────────────────────────────
    for phrase_tuple, replacement in MULTI_SWAPS:
        n = len(phrase_tuple)
        if len(word_history) < n:
            continue
        if tuple(word_history[-n:]) == phrase_tuple:
            if random.random() > LIVE_SWAP_CHANCE:
                return False
            # How many characters are on screen for this phrase?
            # Each word in raw_word_history[-n:] plus the spaces between them.
            raw_words = raw_word_history[-n:]
            chars_on_screen = sum(len(w) for w in raw_words) + (n - 1)
            # Realisation pause
            time.sleep(random.uniform(*LIVE_SWAP_REALISE))
            # Backspace the whole phrase
            backspace(chars_on_screen)
            time.sleep(random.uniform(0.1, 0.35))
            # Retype replacement (preserving capitalisation of first word)
            rep = _preserve_case(raw_words[0], replacement)
            if rep:
                _retype_string(rep, gidx)
            return True

    # ── Single-word check ────────────────────────────────────────────────────
    if word_history:
        current_lower = word_history[-1]
        if current_lower in SINGLE_SWAPS:
            replacement = SINGLE_SWAPS[current_lower]
            if random.random() <= LIVE_SWAP_CHANCE:
                raw = raw_word_history[-1]
                # Only erase the actual word characters, not trailing punctuation
                word_part = raw.rstrip('.,!?;:')
                chars_on_screen = len(word_part)
                time.sleep(random.uniform(*LIVE_SWAP_REALISE))
                backspace(chars_on_screen)
                time.sleep(random.uniform(0.1, 0.35))
                rep = _preserve_case(word_part, replacement)
                if rep:
                    _retype_string(rep, gidx)
                return True

    return False


# ═══════════════════════════════════════════════════════════════════════════
#  WORD & SENTENCE TYPERS
# ═══════════════════════════════════════════════════════════════════════════

def type_word(word, gidx, word_history, raw_word_history):
    """
    Type a single word with typo simulation, then attempt a live swap.
    Returns (chars_typed, did_swap).
    """
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

    # Update word history (clean lowercase for matching, raw for backspace counting)
    clean = re.sub(r'[^a-z]', '', word.lower())
    if clean:
        word_history.append(clean)
        raw_word_history.append(word)

    # Attempt live humaniser swap
    did_swap = attempt_live_swap(word_history, raw_word_history, gidx + typed)
    if did_swap:
        return typed, True

    # Fallback plain word rethink (retypes the same word, no replacement)
    if random.random() < RETHINK_WORD_CHANCE and len(word) > 2:
        time.sleep(random.uniform(*RETHINK_PAUSE))
        bs_amount = min(len(word), random.randint(2, RETHINK_WORD_MAX_BS))
        backspace(bs_amount)
        time.sleep(random.uniform(0.15, 0.5))
        deleted_portion = word[len(word) - bs_amount:]
        for i, ch in enumerate(deleted_portion):
            tap(ch)
            time.sleep(char_delay(gidx + typed + i) * 0.75)

    return typed, False


def type_sentence(sentence, gidx):
    """
    Type a full sentence token by token.
    Live swaps can fire after any word.
    """
    tokens           = re.split(r'(\s+)', sentence)
    word_history     = []   # clean lowercase words this sentence
    raw_word_history = []   # matching raw typed strings
    chars            = 0
    any_swap         = False

    for tok in tokens:
        if tok.strip():
            n, did_swap = type_word(tok, gidx + chars, word_history, raw_word_history)
            chars    += n
            any_swap  = any_swap or did_swap
        else:
            for ch in tok:
                tap(ch)
                time.sleep(char_delay(gidx + chars))
                chars += 1

    # Sentence-level plain rethink — only if no live swap already happened
    if not any_swap and random.random() < RETHINK_SENT_CHANCE and len(sentence) > 20:
        time.sleep(random.uniform(*RETHINK_PAUSE))
        bs_amount = min(chars, random.randint(3, RETHINK_SENT_MAX_BS))
        backspace(bs_amount, fast=False)
        time.sleep(random.uniform(0.3, 0.9))
        deleted_text = sentence[len(sentence) - bs_amount:]
        for i, ch in enumerate(deleted_text):
            tap(ch)
            time.sleep(char_delay(gidx + i) * 0.7)

    return chars


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

        if i < total - 1:
            tap(' ')
            time.sleep(random.uniform(0.05, 0.22))
            gidx             += 1
            char_since_break += 1

        hit_chars = char_since_break >= BREAK_EVERY_CHARS
        hit_sents = sent_since_break >= BREAK_EVERY_SENTS
        if (hit_chars or hit_sents) and i < total - 1:
            break_num       += 1
            char_since_break = 0
            sent_since_break = 0
            do_break(break_num)


# ═══════════════════════════════════════════════════════════════════════════
#  ENTRY
# ═══════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 56)
    print("  💧  Human WRITER  —  ultra-human edition")
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
          f"Live swap: {LIVE_SWAP_CHANCE*100:.0f}% on match")
    print(f"\n  FAILSAFE: move mouse to TOP-LEFT corner to abort!\n")
    print(f"  Click into your target window NOW.\n")

    for i in range(COUNTDOWN, 0, -1):
        print(f"  Starting in {i}...", end="\r", flush=True)
        time.sleep(1)
    print("  Typing!              ")

    type_text(text)
    print("\n\n  ✅  Done!")


if __name__ == "__main__":
    main()
