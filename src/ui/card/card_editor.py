import tkinter as tk
from tkinter import ttk, TclError
from tkinter.colorchooser import askcolor

from data.card import Aspect, Card, Keyword, CardEffect, Phase
from ui.card.card_image import CardImage
from ui.components.editor_window import EditorWindow


class CardEditor(EditorWindow):

    def _display(self, window, card):

        upper_frame = tk.Frame(window)
        form_frame = tk.Frame(upper_frame)
        card_image = CardImage(upper_frame, caching=False, scale=1.5)
        form_frame.pack(side=tk.LEFT, padx=(0, 10))
        card_image.pack(side=tk.LEFT)
        upper_frame.pack(side=tk.TOP, padx=10, pady=(10, 0))

        self.chosen_aspects = set()
        if card.id:
            self.chosen_aspects.update(card.aspects)

        phases = Phase.select()
        keywords = Keyword.select()
        self.card_effects = [(keywords[0] if len(keywords) > 0 else None, phases[0] if len(phases) > 0 else None, "")]
        active_effect = 0
        if card.id:
            self.card_effects = [(effect.condition, effect.phase, effect.description) for effect in card.effects]
            # Shouldn't ever be empty unless something goes wrong like partially deleted records
            if len(self.card_effects) == 0:
                self.card_effects = [(keywords[0] if len(keywords) > 0 else None, phases[0] if len(phases) > 0 else None, "")]

        def refresh():
            card_image.display(card, aspects=self.chosen_aspects, effects=self.card_effects)

        # Color
        def select_color():
            color_tup, color_hex = askcolor(color=card.color)
            if color_hex:
                card.color = color_hex
                color_button.config(text=color_hex, background=color_hex)
                refresh()
            window.lift()
        color_label = tk.Label(form_frame, text="Color")
        color_label.grid(row=0, column=0, pady=2, sticky="e")
        color_button = tk.Button(form_frame, text=card.color, background=card.color, foreground="white", command=select_color)
        color_button.grid(row=0, column=1, sticky="w")

        # Tier
        def handle_tier(*args):
            try:
                card.tier = tier_var.get()
            except TclError:
                card.tier = 0
            finally:
                refresh()
        tier_var = tk.IntVar(value=card.tier)
        tier_var.trace_add("write", handle_tier)
        tier_label = tk.Label(form_frame, text="Tier")
        tier_label.grid(row=1, column=0, pady=2, sticky="e")
        tier_input = tk.Spinbox(form_frame, from_=0, to=Card.HIGHEST_TIER, textvariable=tier_var)
        tier_input.grid(row=1, column=1, pady=2, sticky="w")

        # Name
        def handle_name(*args):
            card.name = name_var.get()
            refresh()
        name_var = tk.StringVar(value=card.name)
        name_var.trace_add("write", handle_name)
        name_label = tk.Label(form_frame, text="Name")
        name_label.grid(row=2, column=0, pady=2, sticky="e")
        name_input = tk.Entry(form_frame, textvariable=name_var)
        name_input.grid(row=2, column=1, pady=2, sticky="w")

        # Aspects
        aspect_label = tk.Label(form_frame, text="Aspect")
        aspect_label.grid(row=3, column=0, pady=2, sticky="e")
        aspects = Aspect.select().order_by(Aspect.name)
        aspect_select = ttk.Combobox(form_frame, values=[aspect.name for aspect in aspects])
        if len(aspects) > 0:
            aspect_select.set(aspects[0].name)
        aspect_select.grid(row=3, column=1, pady=2, sticky="w")

        def handle_add_aspect():
            aspect = Aspect.get(name=aspect_select.get())
            if aspect not in self.chosen_aspects:
                self.chosen_aspects.add(aspect)
                refresh_aspect_list()
                refresh()
        add_aspect_button = tk.Button(form_frame, text="+", width=2, command=handle_add_aspect)
        add_aspect_button.grid(row=3, column=2, padx=(2, 0))

        def refresh_aspect_list():
            aspect_box.delete(0, tk.END)
            for aspect in self.chosen_aspects:
                aspect_box.insert(tk.END, aspect.name)
        def get_selected_aspects():
            selections = aspect_box.curselection()
            if not selections:
                return []
            return Aspect.select().where(Aspect.name << [aspect_box.get(i) for i in selections])
        aspect_box = tk.Listbox(form_frame, selectmode=tk.MULTIPLE)
        aspect_box.grid(row=4, column=1, pady=(0, 10))

        def handle_rem_aspect():
            self.chosen_aspects.difference_update(get_selected_aspects())
            refresh_aspect_list()
            refresh()
        rem_aspect_button = tk.Button(form_frame, text="-", width=2, command=handle_rem_aspect)
        rem_aspect_button.grid(row=4, column=2, sticky="n", padx=(2, 0), pady=2)

        # Effects
        effect_frame = tk.Frame(window)
        def handle_effect(*args):
            condition_keyword = Keyword.get(keyword=condition_input.get())
            phase = Phase.get(name=phase_input.get())
            self.card_effects[active_effect] = (condition_keyword, phase, effect_input.get("1.0", "end-1c"))
            refresh()

        effect_condition_panel = tk.Frame(effect_frame)
        effect_label = tk.Label(effect_condition_panel, text="Effect")
        effect_label.pack(side=tk.LEFT)

        phase_input = ttk.Combobox(effect_condition_panel, width=10, values=[phase.name for phase in phases], state="readonly")
        phase_input.pack(side=tk.LEFT, padx=2)
        phase_input.bind("<<ComboboxSelected>>", handle_effect)
        if len(phases) > 0:
            phase_input.set(phases[0].name)
        condition_input = ttk.Combobox(effect_condition_panel, values=[keyword.keyword for keyword in keywords])
        condition_input.pack(side=tk.LEFT, padx=2)
        condition_input.bind("<<ComboboxSelected>>", handle_effect)
        if len(keywords) > 0:
            condition_input.set(keywords[0].keyword)
        effect_condition_panel.grid(row=0, column=0, pady=5, sticky=tk.W)

        effect_change_panel = tk.Frame(effect_frame)
        def refresh_effect():
            if self.card_effects[active_effect][0]:
                condition_input.set(self.card_effects[active_effect][0].keyword)
            if self.card_effects[active_effect][1]:
                phase_input.set(self.card_effects[active_effect][1].name)
            effect_input.delete("0.0", tk.END)
            effect_input.insert(tk.END, self.card_effects[active_effect][2])

            if active_effect > 0:
                swap_button.grid()
                prev_button.grid()
                del_button.config(state="active")
            else:
                swap_button.grid_remove()
                prev_button.grid_remove()
                del_button.config(state="disabled")

            if active_effect < len(self.card_effects)-1:
                next_button.config(text=">")
            else:
                next_button.config(text="+")
        def handle_prev():
            nonlocal active_effect
            if active_effect == 0:
                return
            active_effect -= 1
            refresh_effect()
        def handle_next():
            nonlocal active_effect
            active_effect += 1
            if active_effect == len(self.card_effects):
                self.card_effects.append((keywords[0] if len(keywords) > 0 else None, phases[0] if len(phases) > 0 else None, ""))
                refresh()
            refresh_effect()
        def handle_del():
            nonlocal active_effect
            if active_effect == 0:
                return
            self.card_effects.pop(active_effect)
            active_effect -= 1
            refresh()
            refresh_effect()
        def handle_swap():
            nonlocal active_effect
            if active_effect == 0:
                return
            current = self.card_effects[active_effect]
            self.card_effects[active_effect] = self.card_effects[active_effect-1]
            self.card_effects[active_effect-1] = current
            refresh()
            refresh_effect()
        swap_button = tk.Button(effect_change_panel, text="<< |", command=handle_swap)
        swap_button.grid(row=0, column=0, padx=(0, 20))
        prev_button = tk.Button(effect_change_panel, text="<", command=handle_prev)
        prev_button.grid(row=0, column=1, padx=2)
        next_button = tk.Button(effect_change_panel, text=">", command=handle_next)
        next_button.grid(row=0, column=2, padx=2)
        del_button = tk.Button(effect_change_panel, text="Delete", command=handle_del)
        del_button.grid(row=0, column=3, padx=2)
        effect_change_panel.grid(row=0, column=1, pady=5, sticky=tk.E)

        effect_input = tk.Text(effect_frame, width=70, height=5)
        effect_input.bind("<KeyRelease>", handle_effect)
        effect_input.grid(row=1, column=0, columnspan=2)
        effect_frame.pack(side=tk.TOP, padx=10)

        refresh()
        refresh_aspect_list()
        refresh_effect()

    def _new(self):
        return Card()

    def _title(self, card):
        return f"Edit Card - {card.name}" if card else "New Card"

    def _save(self, card):
        if not card.id:
            card.save()  # Pre-save to generate ID so we can use foreign keys
        card.aspects = list(self.chosen_aspects)
        CardEffect.delete().where(CardEffect.card == card).execute()
        for i, (keyword, phase, desc) in enumerate(self.card_effects):
            CardEffect.create(condition=keyword, phase=phase, card=card, description=desc, order=i)
        card.save()