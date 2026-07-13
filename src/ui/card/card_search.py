import tkinter as tk
from contextlib import suppress
from tkinter import TclError, messagebox

from peewee import fn

from data.card import Aspect, Card, CardAspect
from ui.card.card_image import CardImage
from ui.components.page_grid import PageGrid
from ui.components.view_frame import ViewFrame
from ui.export.export_menu import ExportMenu


class AspectList(tk.Menubutton):

    def __init__(self, root, text, on_change, *args, **kwargs):
        super().__init__(root, text=text, relief=tk.RAISED, *args, **kwargs)

        self.on_change = on_change
        self.selections = {}
        self.menu = tk.Menu(self, tearoff=0)
        self.config(menu=self.menu)

    def refresh(self):
        for aspect in Aspect.select():
            if aspect.name not in self.selections:
                var = tk.BooleanVar(value=False)
                var.trace_add("write", self.on_change)
                self.selections[aspect.name] = var
                self.menu.add_checkbutton(label=aspect.name, variable=var)

    @property
    def selected(self):
        return [selection for selection in self.selections if self.selections[selection].get()]


class CardSearch(ViewFrame):

    def __init__(self, root, card_editor, deck_editor, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        card_editor.on_save.subscribe(lambda _: self.refresh())

        def make_card_widget(frame, _):
            return CardImage(frame, bd=2, relief="flat")
        def update_pager(page, pages):
            prev_page_button.grid()
            next_page_button.grid()
            if self.card_widgets.first_page:
                prev_page_button.grid_remove()
            if self.card_widgets.last_page:
                next_page_button.grid_remove()
            page_label.config(text=f"{page} / {pages}")
        def on_select(card_image):
            nonlocal add_to_deck
            if card_image:
                self.selected_label.config(text=card_image.card.name)
                self.selection_panel.grid()
                if deck_editor.deck:
                    add_to_deck.grid()
                else:
                    add_to_deck.grid_remove()
            else:
                self.selection_panel.grid_remove()
        self.card_widgets = PageGrid(self, make_card_widget, 7, 3, width=1720, height=1024, selectable=True)
        self.card_widgets.on_page.subscribe(update_pager)
        self.card_widgets.on_select.subscribe(on_select)

        # Search Bar
        search_frame = tk.Frame(self)
        search_label = tk.Label(search_frame, text="Search")
        search_label.grid(column=0, row=0)
        self.search_var = tk.StringVar(value="")
        search_field = tk.Entry(search_frame, textvariable=self.search_var)
        search_field.grid(column=1, row=0)

        self.include_aspect = AspectList(search_frame, "Incl. Aspect", self.refresh)
        self.include_aspect.grid(column=2, row=0, padx=5)
        self.exclude_aspect = AspectList(search_frame, "Excl. Aspect", self.refresh)
        self.exclude_aspect.grid(column=3, row=0, padx=5)

        tier_label = tk.Label(search_frame, text="Tier")
        tier_label.grid(column=4, row=0)

        self.lowest_tier_var = tk.IntVar(value=0)
        lowest_tier_field = tk.Spinbox(search_frame, from_=0, to=Card.HIGHEST_TIER, width=5, textvariable=self.lowest_tier_var)
        lowest_tier_field.grid(column=5, row=0)

        tier_sep_label = tk.Label(search_frame, text="-")
        tier_sep_label.grid(column=6, row=0, padx=5)

        self.highest_tier_var = tk.IntVar(value=Card.HIGHEST_TIER)
        highest_tier_field = tk.Spinbox(search_frame, from_=0, to=Card.HIGHEST_TIER, width=5, textvariable=self.highest_tier_var)
        highest_tier_field.grid(column=7, row=0)

        export_search = ExportMenu(search_frame, lambda: self.search, lambda: self.search_var.get(), text="Export Search")
        export_search.grid(column=8, row=0, padx=(30, 0))

        def handle_add_to_deck():
            deck_editor.add(self.selected)
        def handle_edit():
            card_editor.open(self.selected)
        def handle_delete():
            if messagebox.askyesno("Delete", f"Are you sure you want to delete {self.selected.name}?"):
                self.selected.delete_instance()
                self.refresh()
        self.selection_panel = tk.Frame(search_frame)
        add_to_deck = tk.Button(self.selection_panel, text="Add To Deck", command=handle_add_to_deck)
        add_to_deck.grid(row=0, column=0, padx=2)
        self.selected_label = tk.Label(self.selection_panel, text="")
        self.selected_label.grid(row=0, column=1, padx=2, sticky="e")
        export_selected = ExportMenu(self.selection_panel, lambda: self.selected, lambda: self.selected.name, text="Export")
        export_selected.grid(row=0, column=2, padx=2)
        edit_button = tk.Button(self.selection_panel, text="Edit", command=handle_edit)
        edit_button.grid(row=0, column=3, padx=2)
        delete_button = tk.Button(self.selection_panel, text="Delete", foreground="red", command=handle_delete)
        delete_button.grid(row=0, column=4, padx=2)
        self.selection_panel.grid(column=9, row=0, padx=(50, 0))
        self.selection_panel.grid_remove()

        paging_panel = tk.Frame(self)
        prev_page_button = tk.Button(paging_panel, text="<", command=self.card_widgets.previous)
        prev_page_button.grid(row=0, column=0, padx=2)
        page_label = tk.Label(paging_panel, text="1 / 1")
        page_label.grid(row=0, column=1, padx=2)
        next_page_button = tk.Button(paging_panel, text=">", command=self.card_widgets.next)
        next_page_button.grid(row=0, column=2, padx=2)

        search_frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        paging_panel.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        self.card_widgets.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="w")

        # Refresh now and on updates to the search criteria
        self.search_var.trace_add("write", self.refresh)
        self.lowest_tier_var.trace_add("write", self.refresh)
        self.highest_tier_var.trace_add("write", self.refresh)

    def refresh(self, *args):
        self.card_widgets.select(None)

        self.include_aspect.refresh()
        self.exclude_aspect.refresh()

        self.card_widgets.load(self.search)

    @property
    def search(self):
        lowest_tier = 0
        highest_tier = 0
        with suppress(TclError):  # Suppress errors if set to an empty string
            lowest_tier = self.lowest_tier_var.get()
            highest_tier = self.highest_tier_var.get()

        include_aspects = self.include_aspect.selected
        exclude_aspects = self.exclude_aspect.selected
        search_query = Card.select() \
            .left_outer_join(CardAspect) \
            .left_outer_join(Aspect) \
            .where(fn.Upper(Card.name) % f"*{self.search_var.get().upper()}*") \
            .where((Card.tier <= highest_tier) & (Card.tier >= lowest_tier))

        if len(include_aspects) > 0:
            search_query = search_query.where(Aspect.name << self.include_aspect.selected)
        if len(exclude_aspects) > 0:
            search_query = search_query.where(Aspect.name.not_in(self.exclude_aspect.selected))

        return search_query.distinct().order_by(Card.tier, Card.name)

    @property
    def selected(self):
        return self.card_widgets.selected.card