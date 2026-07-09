import tkinter as tk
from itertools import zip_longest

from data.card import Keyword
from ui.components.page_grid import PageGrid
from ui.components.view_frame import ViewFrame
from util.event_bus import EventBus


class KeywordView(ViewFrame):

    class Display(tk.Frame):

        def __init__(self, root, editor, *args, **kwargs):
            super().__init__(root, *args, **kwargs)

            self.on_delete = EventBus()

            self.keyword = None
            self.keyword_label = tk.Label(self, text="", font=("Arial", 12))
            self.keyword_label.grid(row=0, column=0, pady=(5,2), padx=5, sticky="w")
            right_panel = tk.Frame(self)
            edit_button = tk.Button(right_panel, text="Edit", command=lambda: editor.open(self.keyword))
            edit_button.grid(row=0, column=0, padx=5, sticky="e")
            def handle_delete():
                if self.keyword:
                    self.keyword.delete_instance()
                    self.on_delete.publish()
            delete_button = tk.Button(right_panel, text="Delete", command=handle_delete, fg="red")
            delete_button.grid(row=0, column=1)
            right_panel.grid(row=0, column=1, pady=(5,2), padx=5, sticky="e")
            self.keyword_desc = tk.Text(self, width=100, height=3)
            self.keyword_desc.grid(row=1, column=0, columnspan=2, padx=5)

        def display(self, keyword):
            self.keyword = keyword
            self.keyword_label.config(text=keyword.keyword)
            self.keyword_desc.config(state="normal")
            self.keyword_desc.delete("1.0", tk.END)
            self.keyword_desc.insert(tk.END, keyword.description)
            self.keyword_desc.config(state="disabled")


    def __init__(self, root, editor, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        editor.on_save.subscribe(lambda _: self.refresh())

        def create_display(frame, _):
            display = KeywordView.Display(frame, editor)
            display.on_delete.subscribe(self.refresh)
            return display
        self.widgets = PageGrid(self, create_display, 2, 16, spacing=5)
        self.widgets.pack(side="top")

    def refresh(self):
        self.widgets.load(Keyword.select().order_by(Keyword.keyword))
