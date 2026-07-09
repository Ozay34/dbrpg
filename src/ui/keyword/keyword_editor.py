import tkinter as tk

from data.card import Keyword
from ui.components.editor_window import EditorWindow


class KeywordEditor(EditorWindow):

    def _display(self, window, keyword):

        form_frame = tk.Frame(window)

        def handle_keyword(*args):
            keyword.keyword = keyword_var.get()
        keywrod_frame = tk.Frame(form_frame)
        keyword_var = tk.StringVar(value=keyword.keyword)
        keyword_var.trace_add("write", handle_keyword)
        keyword_label = tk.Label(keywrod_frame, text="Keyword")
        keyword_label.pack(side=tk.LEFT)
        keyword_input = tk.Entry(keywrod_frame, textvariable=keyword_var)
        keyword_input.pack(side=tk.LEFT)
        keywrod_frame.pack(anchor=tk.W)


        def handle_description(*args):
            keyword.description = description_input.get("1.0", "end-1c")
        description_label = tk.Label(form_frame, text="Description")
        description_label.pack(anchor=tk.W)
        description_input = tk.Text(form_frame, width=50, height=5)
        description_input.bind("<KeyRelease>", handle_description)
        description_input.insert(tk.END, keyword.description)
        description_input.pack()


        form_frame.pack(padx=10, pady=(10, 0))


    def _new(self):
        return Keyword()

    def _title(self, keyword):
        return f"Edit Keyword - {keyword.keyword}" if keyword else "New Keyword"
