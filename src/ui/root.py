import json
import tkinter as tk
from tkinter.filedialog import askopenfile

from data.card import Card
from ui.aspect.aspect_view import AspectView
from ui.aspect.aspect_editor import AspectEditor
from ui.card.card_editor import CardEditor
from ui.card.card_search import CardSearch
from ui.components.view_frame import ViewManager
from ui.deck.deck_editor import DeckEditor
from ui.keyword.keyword_editor import KeywordEditor
from ui.keyword.keyword_view import KeywordView
from util.render_tools import load_fonts

root = tk.Tk()
root.title("Deck Builder")

# Install fonts
load_fonts()

menu = tk.Menu(root)
root.config(menu=menu)

def import_cards():
    file = askopenfile(mode="r", filetypes=[("JSON", "*.json")])
    if file is None:
        return
    Card.import_all(json.loads(file.read()))
    file.close()
    card_view.refresh()

card_editor = CardEditor(root)
aspect_editor = AspectEditor(root)
keyword_editor = KeywordEditor(root)
deck_menu = tk.Menu(menu, tearoff=False)
deck_editor = DeckEditor(root, deck_menu, card_editor)

new_menu = tk.Menu(menu, tearoff=False)
menu.add_cascade(label="New", menu=new_menu)
new_menu.add_command(label="Card", command=card_editor.open)
new_menu.add_command(label="Aspect", command=aspect_editor.open)
new_menu.add_command(label="Keyword", command=keyword_editor.open)
new_menu.add_command(label="Deck", command=deck_editor.open)
new_menu.add_separator()
new_menu.add_command(label="Import", command=import_cards)

view_menu = tk.Menu(menu, tearoff=False)
menu.add_cascade(label="View", menu=view_menu)
view_manager = ViewManager(view_menu)
card_view = view_manager.add("Cards", CardSearch(root, card_editor, deck_editor))
aspect_view = view_manager.add("Aspects", AspectView(root, aspect_editor))
keyword_view = view_manager.add("Keywords", KeywordView(root, keyword_editor))

menu.add_cascade(label="Deck", menu=deck_menu)
root.lift()