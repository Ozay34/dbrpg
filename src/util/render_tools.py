import os
import subprocess
from pathlib import Path
from tkinter import font

from PIL import ImageFont

from util.paths import resolve_path, EXE

FONT_DIR = Path(resolve_path("assets/fonts/"))
ROMAN_NUMERALS = {
    "I": 1,
    "IV": 4,
    "V": 5,
    "IX": 9,
    "X": 10
}

def contrast(color_hex):
    color_hex = color_hex.lstrip("#")
    r, g, b = tuple(int(color_hex[i:i + 2], 16) for i in (0, 2, 4))
    y = (r * 299 + g * 587 + b * 114) / 1000
    if y >= 128:
        return "#000000"
    return "#ffffff"

def to_roman_numerals(val):
    if val == 0:
        return "0"

    numerals = ""
    numeral_table = list(ROMAN_NUMERALS.items())
    i = len(numeral_table) - 1
    number = val

    while number:
        sym, num = numeral_table[i]
        div = number // num
        number %= num
        while div:
            numerals += sym
            div -= 1
        i -= 1

    return numerals

def get_card_art(card):
    files = list(resolve_path("assets/card_art/").glob(f"{card.name}.*"))
    if EXE:
        files += list(Path("assets/card_art").resolve().glob(f"{card.name}.*"))
    if len(files) == 0:
        return ""

    return f'<image width="2.5in" height="3.5in" href="{files[0].as_uri()}" />'

class TextBounds:

    def __init__(self, text, size, font):
        self.text = text
        self.size = size
        img_font = ImageFont.truetype(FONT_DIR / font, size)
        if len(text) > 0:
            self._bounds = img_font.getbbox(text)
        else:
            self._bounds = (0,0,0,0)

    @property
    def width(self):
        return self._bounds[2] - self._bounds[0]

    @property
    def height(self):
        return self._bounds[3] - self._bounds[1]

    @classmethod
    def fit(cls, text, width, max_size, font):
        font_size = max_size
        bounds = TextBounds(text, font_size, font)
        while bounds.width > width:
            font_size -= 1
            bounds = TextBounds(text, font_size, font)
        return bounds

def load_fonts():
    fonts = font.families()
    for font_file in FONT_DIR.iterdir():
        img_font = ImageFont.truetype(font_file)
        font_family, font_style = img_font.getname()
        font_name = font_family
        if font_style != "Regular":
            font_name += " " + font_style
        if font_name not in fonts:
            subprocess.run(f'start /wait "" "{font_file.resolve()}"', shell=True)