from typing import Type

from peewee import SqliteDatabase, Model, IntegerField, CharField, ManyToManyFieldAccessor
from playhouse.migrate import SqliteMigrator

db = SqliteDatabase('data.db', pragmas={
    'journal_mode': 'wal',  # Allow readers while writer active.
    'cache_size': -64000,  # 64 MB page cache.
})

def auto_create(model: Type[Model]):
    table_name = model._meta.table_name
    schema, created = SchemaVersion.get_or_create(table=table_name)
    if created:
        model.create_table()
    model._created = created
    return model

class BaseModel(Model):

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._created = False

    class Meta:
        database = db
        legacy_table_names = False

    @classmethod
    def migration(cls, version):
        def wrapper(func):
            schema = SchemaVersion.get(SchemaVersion.table == cls._meta.table_name)
            if schema.version < version and not cls._created:
                with db.atomic():
                    func(SqliteMigrator(db))
                    schema.version = version
                    schema.save()
            return func
        return wrapper


class SchemaVersion(BaseModel):
    table = CharField(max_length=255)
    version = IntegerField(default=0)

# Cannot be an annotation because the function depends on this schema
auto_create(SchemaVersion)
