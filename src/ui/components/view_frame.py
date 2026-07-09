import tkinter as tk

from ui.components.editor_window import EditorWindow


class ViewManager:

    def __init__(self, menu):
        self._menu = menu

    def add(self, command, frame: ViewFrame):
        self._menu.add_command(label=command, command=frame.show)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.pack_propagate(False)
        frame.grid_propagate(False)
        if not frame.shown:
            frame.grid_remove()
        else:
            frame.refresh()
        return frame


class ViewFrame(tk.Frame):

    _shown: ViewFrame = None

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, width=1920, height=1080, *args, **kwargs)
        if not ViewFrame._shown:
            ViewFrame._shown = self

    @property
    def shown(self):
        return self == ViewFrame._shown

    def show(self):
        ViewFrame._shown.grid_remove()
        self.refresh()
        self.grid()
        ViewFrame._shown = self

    def refresh(self):
        ...