import tkinter as tk

from data.card import Aspect
from ui import aspect
from ui.components.page_grid import PageGrid
from ui.components.view_frame import ViewFrame
from util.render_tools import contrast


class AspectView(ViewFrame):

    class Display(tk.Frame):

        def __init__(self, root, editor, *args, **kwargs):
            super().__init__(root, *args, borderwidth=2, relief="ridge", **kwargs)

            self.aspect = None
            self.aspect_label = tk.Label(self, text="", font=("Arial", 12))
            self.aspect_label.grid(row=0, column=0, columnspan=2, pady=5)
            self.color_label = tk.Entry(self, relief=tk.FLAT)
            self.color_label.grid(row=1, column=0, pady=(0,5), padx=5, sticky=tk.W)
            self.edit_button = tk.Button(self, text="Edit", command=lambda: editor.open(self.aspect))
            self.edit_button.grid(row=1, column=1, pady=5, padx=5, sticky=tk.E)

        def display(self, aspect):
            self.aspect = aspect
            font_color = contrast(aspect.color)
            self.config(bg=aspect.color)
            self.aspect_label.config(text=aspect.name, fg=font_color, bg=aspect.color)
            self.color_label.config(state="normal")
            self.color_label.insert(tk.END, aspect.color)
            self.color_label.config(readonlybackground=aspect.color, fg=font_color, state="readonly")


    def __init__(self, root, editor, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        editor.on_save.subscribe(lambda _: self.refresh())

        def create_display(frame, _):
            return AspectView.Display(frame, editor)
        self.widgets = PageGrid(self, create_display, 8, 16, spacing=5)
        self.widgets.pack(side="top")

    def refresh(self):
        self.widgets.load(Aspect.select().order_by(Aspect.name))
