import os
import sys
import tkinter as tk
from io import BytesIO

import cairosvg
from PIL import ImageTk, Image
from jinja2 import Environment, FileSystemLoader
import util.render_tools as tools

from data.card import Card, CardEffect
from util.paths import resolve_path

env = Environment(
    loader=FileSystemLoader(resolve_path("assets"))
)
template = env.get_template("card.svg")


def render_card(card, aspects=None, effects=None, scale=1.0):
    if card.id and aspects is None:
        aspects = list(card.aspects)
    if card.id and effects is None:
        effects = [(effect.condition, effect.description) for effect in card.effects.order_by(CardEffect.order)]
    png = cairosvg.svg2png(bytestring=template.render(
        card=card,
        aspects=aspects or [],
        effects=effects or [],
        tools=tools
    ), scale=scale, unsafe=True)
    return Image.open(BytesIO(png))


class CardCache:

    def __init__(self):
        self.cache = {}
        Card.on_save.subscribe(self.release)

    def get(self, card, callback):
        if card.id in self.cache:
            return self.cache[card.id]
        item = callback()
        self.cache[card.id] = item
        return item

    def release(self, card):
        if card.id and card.id in self.cache:
            self.cache.pop(card.id)

class CardImage(tk.Label):

    cache = CardCache()

    def __init__(self, root, caching=True, scale=1.0, **kwargs):
        super().__init__(root, **kwargs)
        self.card = None
        self._image = None
        self.scale = scale
        self.caching = caching

    def display(self, card, aspects=None, effects=None):

        def render():
            return ImageTk.PhotoImage(render_card(card, aspects, effects, self.scale))

        self.card = card

        if self.caching:
            image = CardImage.cache.get(card, render)
        else:
            image = render()

        self._image = image
        self.config(image=image)