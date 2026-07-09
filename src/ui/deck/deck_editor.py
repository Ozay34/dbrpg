import tkinter as tk
from contextlib import suppress

from peewee import IntegrityError, DoesNotExist

from data.card import Card
from data.deck import Deck, DeckCard
from ui.card.card_image import CardImage
from ui.components.editor_window import EditorWindow
from ui.components.page_grid import PageGrid
from util.event_bus import EventBus


class NumberedCardImage(tk.Frame):
    def __init__(self, root, caching=True, scale=1.0, **kwargs):
        super().__init__(root, **kwargs)
        self.deck_card = None
        self.on_click = EventBus()
        self.card_image = CardImage(self, caching, scale=scale, **kwargs)
        self.card_image.pack()
        def handle_click(*args):
            self.on_click.publish(*args)
        self.card_image.bind("<Button-1>", handle_click)
        self.number_label = tk.Label(self, text="Number", justify="right", font=("Ariel", 12))
        self.number_label.place(relx=0.9, rely=0, anchor="ne")

    def display(self, deck_card, aspects=None, effects=None):
        self.deck_card = deck_card
        try:
            self.card_image.display(deck_card.card, aspects=aspects, effects=effects)
        except DoesNotExist, AttributeError:
            self.card_image.display(Card(), aspects=aspects, effects=effects)
        self.number_label.config(text=deck_card.amount)


class DeckEditor(EditorWindow):

    def __init__(self, root, menu, card_editor):
        super().__init__(root)
        self._deck = None
        self._name_var = tk.StringVar()
        self._window = None
        self._menu = menu
        self._menu_vars = []
        self._card_editor = card_editor
        self._card_editor.on_save.subscribe(lambda _: self.refresh())
        self.refresh_menu()

    def close(self):
        self._deck = None
        self._window.quit()
        self._window.destroy()
        self._window = None
        self.on_save.publish()
        self.refresh_menu()

    def open(self, deck=None):
        if deck is None:
            deck = self._new()
        self._deck = deck
        if self._window:
            self._window.lift()
            self.refresh()
            return

        self._window = tk.Toplevel(self._root)
        self._window.protocol("WM_DELETE_WINDOW", self.close)
        self._display(self._window, deck)
        self.refresh_menu()
        self.refresh()
        self._window.mainloop()

    def _display(self, window, deck):

        def handle_quick_create():
            card = self._card_editor.open()
            if card.id:
                DeckCard.create(card=card, deck=self._deck)
                self.refresh()
                self._window.lift()
        edit_frame = tk.Frame(window)
        self.quick_create = tk.Button(edit_frame, text="Quick Create", command=handle_quick_create)
        if not deck.id:
            self.quick_create.config(state="disabled")
        self.quick_create.grid(row=0, column=0, padx=5)

        def handle_del():
            self._deck.delete_instance()
            self.close()
        name_input = tk.Entry(edit_frame, textvariable=self._name_var)
        name_input.grid(row=0, column=1, padx=(20, 0))
        save_button = tk.Button(edit_frame, text="Save", command=lambda: self._save(self._deck))
        save_button.grid(row=0, column=2, padx=5)
        del_button = tk.Button(edit_frame, text="Delete", command=handle_del)
        del_button.grid(row=0, column=3, padx=5)

        def handle_edit():
            self._card_editor.open(self.card_widgets.selected.deck_card.card)
            self.refresh()
            self._window.lift()
        def handle_remove():
            card = self.card_widgets.selected.card
            self._deck.cards.remove(card)
            self.card_widgets.select(None)
            self.refresh()
        selection_panel = tk.Frame(edit_frame)
        selection_label = tk.Label(selection_panel)
        selection_label.pack(side="left", padx=5)

        def handle_amt(*args):
            try:
                amount = amt_var.get()
            except tk.TclError:
                amount = 1
            deck_card = self.card_widgets.selected.deck_card
            deck_card.amount = amount
            deck_card.save()
            self.refresh()
        amt_var = tk.IntVar(value=1)
        amt_input = tk.Spinbox(selection_panel, from_=1, to=99, textvariable=amt_var, width=5)
        amt_input.pack(side="left", padx=5)

        edit_button = tk.Button(selection_panel, text="Edit", command=handle_edit)
        edit_button.pack(side="left", padx=5)
        remove_button = tk.Button(selection_panel, text="Remove", command=handle_remove)
        remove_button.pack(side="left", padx=5)
        selection_panel.grid(row=0, column=4, padx=(40, 0))
        selection_panel.grid_remove()

        def handle_select(deck_card_widget):
            nonlocal amt_trace_id
            if deck_card_widget:
                selection_panel.grid()
                selection_label.config(text=deck_card_widget.deck_card.card.name)
                amt_var.trace_remove("write", amt_trace_id)
                amt_var.set(deck_card_widget.deck_card.amount)
                amt_trace_id = amt_var.trace_add("write", handle_amt)
            else:
                selection_panel.grid_remove()
        def make_card_widget(frame, do_select):
            card_image = NumberedCardImage(frame, bd=2, relief="flat")
            card_image.on_click.subscribe(do_select(card_image))
            return card_image
        self.card_widgets = PageGrid(window, make_card_widget, 7, 3, spacing=0, width=1734, height=1034, selectable=True)
        self.card_widgets.on_select.subscribe(handle_select)
        amt_trace_id = amt_var.trace_add("write", handle_amt)

        def update_pager(page, pages):
            prev_page_button.grid()
            next_page_button.grid()
            if self.card_widgets.first_page:
                prev_page_button.grid_remove()
            if self.card_widgets.last_page:
                next_page_button.grid_remove()
            page_label.config(text=f"{page} / {pages}")
        paging_panel = tk.Frame(window)
        prev_page_button = tk.Button(paging_panel, text="<", command=self.card_widgets.previous)
        prev_page_button.grid(row=0, column=0, padx=2)
        page_label = tk.Label(paging_panel, text="1 / 1")
        page_label.grid(row=0, column=1, padx=2)
        next_page_button = tk.Button(paging_panel, text=">", command=self.card_widgets.next)
        next_page_button.grid(row=0, column=2, padx=2)
        self.card_widgets.on_page.subscribe(update_pager)

        edit_frame.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        paging_panel.grid(row=0, column=1, sticky="e", padx=10)
        self.card_widgets.grid(row=1, column=0, columnspan=2, padx=10, pady=(0,10))

    def _new(self):
        return Deck()

    def _title(self, deck):
        return f"Edit Deck - {deck.name}" if deck.name else "New Deck"

    def _save(self, deck):
        deck.name = self._name_var.get()
        deck.save()
        self.quick_create.config(state="normal")
        self.refresh()
        self.refresh_menu()
        return True  # Keep window alive

    def refresh_menu(self):

        def open_deck(deck):
            def callback():
                self.open(deck)
                self.refresh_menu()
            return callback

        self._menu.delete(0, tk.END)
        self._menu_vars = []
        for deck in Deck.select().order_by(Deck.name):
            var = tk.BooleanVar(value = deck == self._deck)
            self._menu_vars.append(var)
            self._menu.add_checkbutton(label=deck.name, variable=var, command=open_deck(deck))

    def refresh(self):
        self._window.title(self._title(self._deck))
        self._name_var.set(self._deck.name)

        if self._deck.id:
            query = self._deck.cards.select(DeckCard, Card).join(Card).order_by(Card.tier, Card.name)
            self.card_widgets.load(query)
        else:
            self.card_widgets.clear()
            self.refresh_menu()

    def add(self, card):
        if self._deck:
            with suppress(IntegrityError):
                DeckCard.create(card=card, deck=self._deck)
                self.refresh()

    @property
    def deck(self):
        if self._deck and self._deck.id:
            return self._deck
        return None