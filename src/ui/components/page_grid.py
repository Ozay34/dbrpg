import tkinter as tk
from itertools import zip_longest

from util.event_bus import EventBus


class PageGrid(tk.Frame):

    def __init__(self, root, create, x_len:int, y_len:int, spacing=2, selectable=False, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        if "width" in kwargs and "height" in kwargs:
            self.grid_propagate(False)
        self._pages = 1
        self._page = 1
        self._query = None
        self._widgets = []
        self._selected = None

        self.on_page = EventBus()
        self.on_select = EventBus()

        def handle_select(selected):
            if selectable:
                return lambda _: self.select(selected)
            return lambda _: ...

        for y in range(y_len):
            for x in range(x_len):
                widget = create(self, handle_select)
                widget.grid(
                    row=y,
                    column=x,
                    padx=(spacing if x > 0 else 0, 0),
                    pady=(spacing if y > 0 else 0, 0))
                widget.bind("<Button-1>", handle_select(widget))
                widget.grid_remove()
                self._widgets.append(widget)

    @property
    def first_page(self):
        return self._page <= 1

    @property
    def last_page(self):
        return self._page >= self._pages

    @property
    def pages(self):
        return self._pages

    @property
    def page(self):
        return self._page

    @property
    def selected(self):
        return self._selected

    def jump(self, page):
        self._page = page
        self._reload()

    def next(self):
        if not self.last_page:
            self._page += 1
            self._reload()

    def previous(self):
        if not self.first_page:
            self._page -= 1
            self._reload()

    def select(self, selected=None):
        if not selected or selected == self._selected:
            if self._selected:
                self._selected.config(relief="flat")
            self._selected = None
        else:
            if self._selected:
                self._selected.config(relief="flat")
            selected.config(relief="sunken")
            self._selected = selected

        self.on_select.publish(self._selected)

    def load(self, query):
        self._pages = (query.count() // (len(self._widgets) + 1)) + 1
        self._query = query
        self._reload()

    def clear(self):
        self._pages = 1
        self._page = 1
        self._query = None
        self.select(None)
        self._reload()

    def _reload(self, *args):
        paged_query = []
        if self._query:
            paged_query = self._query.paginate(self.page, len(self._widgets))
        for widget, item in zip_longest(self._widgets, paged_query):
            if item:
                widget.display(item)
                widget.grid()
            else:
                widget.grid_remove()
        self.on_page.publish(self._page, self._pages)