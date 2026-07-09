import tkinter as tk
from abc import abstractmethod, ABC

from data.db import db
from util.event_bus import EventBus


class EditorWindow(ABC):

    def __init__(self, root):
        self._root = root
        self.on_save = EventBus()
        self.on_close = EventBus()

    @abstractmethod
    def _new(self):
        ...

    @abstractmethod
    def _title(self, item):
        ...

    @abstractmethod
    def _display(self, window, item):
        ...

    def _save(self, item):
        item.save()

    def open(self, item=None):
        window = tk.Toplevel(self._root)
        window.title(self._title(item))
        def close():
            window.quit()
            window.destroy()
            self.on_close.publish()
        window.protocol("WM_DELETE_WINDOW", close)

        if item is None:
            item = self._new()
        self._display(window, item)

        def save():
            with db.atomic():
                self._save(item)
                self.on_save.publish(item)
                close()

        save_button = tk.Button(window, text="Save", command=save)
        save_button.pack(anchor="e", padx=10, pady=10)

        window.mainloop()
        return item