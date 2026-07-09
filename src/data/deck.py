from peewee import AutoField, CharField, ManyToManyField, CompositeKey, ForeignKeyField, DeferredThroughModel, \
    IntegerField

from data.card import Card
from data.db import auto_create, BaseModel

@auto_create
class Deck(BaseModel):

    id = AutoField(primary_key=True)
    name = CharField(max_length=255, default="")

@auto_create
class DeckCard(BaseModel):

    class Meta:
        primary_key = CompositeKey("card", "deck")

    card = ForeignKeyField(Card, on_delete="CASCADE")
    deck = ForeignKeyField(Deck, on_delete="CASCADE", backref="cards")
    amount = IntegerField(default=1)
