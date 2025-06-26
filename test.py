import json

FONT_WIDTH=32
FONT_HEIGHT=64
MAX_WIDTH = 500
MAX_HEIGHT = 500

class GFX:
    def __init__(self):
        self.height = MAX_HEIGHT
        self.width = MAX_WIDTH
        self.font_height = FONT_HEIGHT
        self.font_width = FONT_WIDTH

def _text_width(gfx, s):
    # width, _ = gfx.font.getbbox(s)[2:4]
    width = len(s) * gfx.font_width  # assuming fixed-width font
    return width

def _debug(msg: str):
    # print(f"DEBUG: {msg}")
    pass

def _fit_text_chars(gfx, msg: str) -> int:
    n = 0
    last_n = 0
    max = len(msg)
    while True:
        if n >= max:
            return n
        last_n = n
        width = _text_width(gfx, msg[:n])
        if width > gfx.width:
            return last_n
        n += 1

def _fit_text_words(gfx, words: list[str]) -> int:
    n = 0
    last_n = 0
    max = len(words)
    while True:
        if n >= max:
            return n
        last_n = n
        test_words = words[:n]
        test_line = " ".join(test_words)
        width = _text_width(gfx, test_line)
        if width > gfx.width:
            return last_n
        n += 1

def _text_split_words(gfx, s) -> list[str]:
    words = s.split()
    n = 0
    end = len(words)
    lines = []
    while True:
        test_words = words[n:]
        l = _fit_text_words(gfx, test_words)
        lines.append(" ".join(words[n:n+l]))
        n += l
        if n >= end:
            break
    return lines

def _text_split_chars(gfx, s) -> list[str]:
    n = 0
    lines = []
    max = len(s)
    while True:
        if n >= max:
            break
        if s[n] == ' ':
            n += 1
            continue
        l = _fit_text_chars(gfx, s[n:])
        if l == 0:
            break
        lines.append(s[n:n+l])
        n += l
    return lines

def _text_split(gfx, s, split_fn=None) -> list[str]:
    results = []
    first_line = True
    height = 0
    for s in s.splitlines():
        height += gfx.font_height
        if height >= gfx.height:
            break
        if not first_line:
            results.append(f"")
        s = s.strip()
        split_lines = split_fn(gfx, s)
        results.extend(split_lines)
        first_line = False
    return results

def main():
    s = "Hello, World!  \n This is a test string to fit into a maximum width of 250 characters.\nLet's see how it handles splitting on characters and fitting within the specified width limit. This should be long enough to require multiple iterations to fit properly."
    gfx = GFX()
    lines = _text_split(gfx, s, _text_split_chars)
    print(json.dumps(lines, indent=2))
    lines = _text_split(gfx, s, _text_split_words)
    print(json.dumps(lines, indent=2))
main()