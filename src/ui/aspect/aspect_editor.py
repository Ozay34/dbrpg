import tkinter as tk
from tkinter.colorchooser import askcolor

from data.card import Aspect
from ui.components.editor_window import EditorWindow
from util.render_tools import contrast


class AspectEditor(EditorWindow):

    def _display(self, window, aspect):

        form_frame = tk.Frame(window)

        def handle_name(*args):
            aspect.name = name_var.get()
        name_var = tk.StringVar(value=aspect.name)
        name_var.trace_add("write", handle_name)
        name_label = tk.Label(form_frame, text="Name")
        name_label.grid(row=0, column=0, pady=5)
        name_input = tk.Entry(form_frame, textvariable=name_var)
        name_input.grid(row=0, column=1, pady=5)
        name_input.grid(row=0, column=1, pady=5)

        def select_color():
            color_tup, color_hex = askcolor(color=aspect.color)
            if color_hex:
                aspect.color = color_hex
                color_select.config(bg=color_hex, fg=contrast(color_hex))
            window.lift()
        color_select = tk.Button(form_frame, width=16, text="Color", command=select_color, bg=aspect.color if aspect.color else "#ffffff")
        color_select.grid(row=1, column=0, columnspan=2, pady=5)

        form_frame.pack(padx=10, pady=(10, 0))

    def _new(self):
        return Aspect()

    def _title(self, aspect):
        return f"Edit Aspect - {aspect.name}" if aspect else "New Aspect"