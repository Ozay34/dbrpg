import json
import tkinter as tk
from tkinter.filedialog import asksaveasfile, asksaveasfilename
from tkinter.simpledialog import askinteger

from PIL import Image

from ui.card.card_image import render_card


class ExportMenu(tk.Menubutton):

    def __init__(self, root, get_cards, get_name=None, **kwargs):
        super().__init__(root, relief="raised", **kwargs)

        menu = tk.Menu(self, tearoff=0)
        self.config(menu=menu)

        def export_json():
            file = asksaveasfile(mode="w", initialfile=get_name() if get_name else "", defaultextension=".json",
                                 filetypes=[("JSON", "*.json")])
            if file is None:
                return
            obj = [card.export() for card in get_cards()]
            file.write(json.dumps(obj, indent=4))
            file.close()

        menu.add_command(label="JSON", command=export_json)

        def export_img():
            padding = 10
            images = [render_card(card, scale=2.0) for card in get_cards()]
            if len(images) == 0:
                return
            cards_wide = askinteger(title="Export Width", prompt="# of cards wide?", initialvalue=7)
            if cards_wide > len(images):
                cards_wide = len(images)
            cards_high = ((len(images)-1) // cards_wide) + 1
            card_width = images[0].width + padding
            card_height = images[0].height + padding

            sheet = Image.new("RGBA", (card_width * cards_wide - padding, card_height * cards_high - padding))
            for i, image in enumerate(images):
                card_x = i % cards_wide
                card_y = i // cards_wide
                sheet.paste(image, (card_x * card_width, card_y * card_height))

            file = asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")], initialfile=get_name())
            if file:
                sheet.save(file)


        menu.add_command(label="Img Sheet", command=export_img)