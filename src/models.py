import peewee as pw
from envparse import env
from playhouse.db_url import connect

env.read_envfile()

db = connect(env('DATABASE_URL', cast=str, default='sqlite://db.sqlite'))


class User(pw.Model):
    id = pw.BigIntegerField(index=True, unique=True)
    full_name = pw.CharField()
    username = pw.CharField()
    email = pw.CharField(index=True)
    is_confirmed = pw.BooleanField(default=False, index=True)

    class Meta:
        database = db
