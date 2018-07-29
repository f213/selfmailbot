import peewee as pw
from envparse import env
from playhouse.db_url import connect

env.read_envfile()

db = connect(env('DATABASE_URL', cast=str, default='sqlite://db.sqlite'))


def with_user(fn):
    """Decorator to add kwarg with registered user instance to the telegram.ext handler"""
    def call(bot, update, *args, **kwargs):
        from_user = update.message.from_user
        kwargs['user'], created = User.get_or_create(
            id=from_user.id,
            defaults=dict(
                full_name=from_user.full_name,
                username=from_user.username,
            ),
        )

        return fn(bot, update, *args, **kwargs)

    return call


class User(pw.Model):
    id = pw.BigIntegerField(index=True, unique=True)
    full_name = pw.CharField()
    username = pw.CharField(null=True)
    email = pw.CharField(index=True, null=True)
    is_confirmed = pw.BooleanField(default=False, index=True)

    class Meta:
        database = db
