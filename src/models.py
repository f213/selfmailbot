import contextlib
import os
import uuid

import peewee as pw
import telegram
from dotenv import load_dotenv
from playhouse.db_url import connect

load_dotenv()

db = connect(os.getenv("DATABASE_URL"))


class User(pw.Model):
    pk = pw.BigIntegerField(index=True, unique=True)
    created = pw.DateTimeField(constraints=[pw.SQL("DEFAULT CURRENT_TIMESTAMP")])
    full_name = pw.CharField()
    username = pw.CharField(null=True)
    email = pw.CharField(index=True, null=True)
    is_confirmed = pw.BooleanField(default=False, index=True)
    sent_message_count = pw.IntegerField(default=0)
    confirmation = pw.CharField(max_length=36, index=True)
    chat_id = pw.BigIntegerField(unique=True)

    class Meta:
        database = db


def get_user_instance(user: telegram.User, chat_id: int) -> User:
    """DB user instance based on telegram user data"""
    return User.get_or_create(
        pk=user.id,
        defaults={
            "pk": user.id,
            "full_name": user.full_name,
            "username": user.username,
            "confirmation": str(uuid.uuid4()),
            "chat_id": chat_id,
        },
    )[0]


def get_user_by_confirmation_link(link: str) -> User | None:
    with contextlib.suppress(User.DoesNotExist):
        return User.get(User.confirmation == link)


def create_tables() -> None:
    db.create_tables([User])
