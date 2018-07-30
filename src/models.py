import peewee as pw
import telegram
from envparse import env
from playhouse.db_url import connect

env.read_envfile()

db = connect(env('DATABASE_URL', cast=str, default='sqlite:///db.sqlite'))


class User(pw.Model):
    id = pw.BigIntegerField(index=True, unique=True)
    created = pw.DateTimeField(constraints=[pw.SQL('DEFAULT CURRENT_TIMESTAMP')])
    full_name = pw.CharField()
    username = pw.CharField(null=True)
    email = pw.CharField(index=True, null=True)
    is_confirmed = pw.BooleanField(default=False, index=True)
    sent_message_count = pw.IntegerField(default=0)

    class Meta:
        database = db


def get_user_instance(user: telegram.User) -> User:
    instance, created = User.get_or_create(
        id=user.id,
        defaults=dict(
            full_name=user.full_name,
            username=user.username,
        ),
    )
    return instance


def with_user(fn):
    """Decorator to add kwarg with registered user instance to the telegram.ext handler"""
    def call(bot, update, *args, **kwargs):
        kwargs['user'] = get_user_instance(update.message.from_user)

        return fn(bot, update, *args, **kwargs)

    return call


def create_tables():
    db.create_tables([User])
