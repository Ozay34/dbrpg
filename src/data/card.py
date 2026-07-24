import re
from enum import Enum

from peewee import CharField, IntegerField, AutoField, ForeignKeyField, TextField, ManyToManyField, fn, \
    CompositeKey
from playhouse.migrate import migrate
from playhouse.shortcuts import model_to_dict

from data.db import BaseModel, auto_create, db
from util.event_bus import EventBus


@auto_create
class Aspect(BaseModel):

    on_save = EventBus()

    id = AutoField(primary_key=True)
    name = CharField(max_length=255, default="")
    color = CharField(max_length=7)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Aspect.on_save.publish(self)

@auto_create
class Keyword(BaseModel):

    on_save = EventBus()

    id = AutoField(primary_key=True)
    keyword = CharField(max_length=255)
    description = TextField(default="")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Keyword.on_save.publish(self)

    @classmethod
    def highlight(cls, line):
        return [(line, True)]

@auto_create
class Card(BaseModel):

    HIGHEST_TIER = 10

    on_save = EventBus()

    id = AutoField(primary_key=True)
    name = CharField(max_length=255, default="")
    aspects = ManyToManyField(Aspect, on_delete="CASCADE")
    tier = IntegerField(default=0)
    color = CharField(max_length=7, default="#000000")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Card.on_save.publish(self)

    @classmethod
    def import_all(cls, cards):
        with db.atomic():
            for card_dict in cards:
                card = Card.create(name=card_dict["name"], tier=card_dict["tier"], color=card_dict["color"])
                card.aspects = list(Aspect.select().where(Aspect.name << card_dict["aspects"]))
                for i, effect_dict in enumerate(card_dict["effects"]):
                    condition = Keyword.get(keyword=effect_dict["condition"])
                    CardEffect.create(condition=condition, card=card, description=effect_dict["description"], order=i)
                card.save()

    @classmethod
    def with_aspect(cls, aspect):
        return Card.select().distinct().join(CardAspect).where(CardAspect.aspect == aspect)

    @classmethod
    def with_keyword(cls, keyword):
        return Card.select().distinct().join(CardEffect).where(CardEffect.condition == keyword)

    def export(self):
        return model_to_dict(self, exclude=[Card.id]) | {
            "aspects": [aspect.name for aspect in self.aspects],
            "effects": [effect.export() for effect in self.effects.order_by(CardEffect.order)]
        }

    def tokenize_effect(self):

        base_color = "#000000"
        lines = []
        for line in self.effect.split("\n"):
            tokens = []
            lines.append(tokens)

            i = 0
            for match in re.finditer(r"[\[\{]((.+?)(:.*?)?)[\]\}]", line):
                color = base_color
                if match.group().startswith("["):
                    query = Keyword.select().where(fn.Upper(Keyword.keyword) == match.group(2).upper()).limit(1)
                    if len(query) == 0:
                        continue
                    color = "#FF000000"
                elif match.group().startswith("{"):
                    query = Aspect.select().where(fn.Upper(Aspect.name) == match.group(2).upper()).limit(1)
                    if len(query) == 0:
                        continue
                    color = query[0].color

                start, end = match.span()
                if i < start:
                    tokens.append((line[i:start], base_color))
                tokens.append((match.group(1), color))
                i = end + 1
            if i < len(line):
                tokens.append((line[i:], base_color))


        return lines

CardAspect = Card.aspects.get_through_model()
auto_create(CardAspect)

@auto_create
class Phase(BaseModel):

    name = CharField(max_length=255, default="")
    color = CharField(max_length=7, default="#000000")

@auto_create
class CardEffect(BaseModel):

    id = AutoField(primary_key=True)
    card = ForeignKeyField(Card, backref="effects", on_delete="CASCADE")
    phase = ForeignKeyField(Phase)
    condition = ForeignKeyField(Keyword)
    description = TextField(default="")
    order = IntegerField(default=0)

    def export(self):
        return {
            "condition": self.condition.keyword,
            "description": self.description
        }

@CardEffect.migration(1)
def add_phases(migrator):
    clash, created = Phase.get_or_create(name="Clash", color="#ed4e4e")
    respite, created = Phase.get_or_create(name="Respite", color="#009ae0")

    class PreCardEffect(BaseModel):
        class Meta:
            db_table = "card_effect"
            primary_key = CompositeKey("card", "condition")
        card = ForeignKeyField(Card, on_delete="CASCADE")
        condition = ForeignKeyField(Keyword)
        description = TextField(default="")
        order = IntegerField(default=0)
    class PostCardEffect(BaseModel):
        id = AutoField(primary_key=True)
        card = ForeignKeyField(Card, on_delete="CASCADE")
        phase = ForeignKeyField(Phase)
        condition = ForeignKeyField(Keyword)
        description = TextField(default="")
        order = IntegerField(default=0)

    PostCardEffect.create_table()
    PostCardEffect.insert_many([{
        PostCardEffect.card: effect.card,
        PostCardEffect.phase: clash,
        PostCardEffect.condition: effect.condition,
        PostCardEffect.description: effect.description,
        PostCardEffect.order: effect.order
    } for effect in PreCardEffect.select()]).execute()

    PreCardEffect.drop_table()
    migrate(
        migrator.rename_table("post_card_effect", "card_effect")
    )