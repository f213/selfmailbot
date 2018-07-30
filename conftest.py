from random import randint
from unittest.mock import MagicMock

import peewee as pw
import pytest
from faker import Faker

faker = Faker()


def factory(class_name: str = None, **kwargs):
    """Simple factory to create a class with attributes from kwargs"""
    class FactoryGeneratedClass:
        pass

    rewrite = {
        '__randint': lambda *args: randint(100_000_000, 999_999_999),
    }

    for key, value in kwargs.items():
        if value in rewrite:
            value = rewrite[value](value)

        setattr(FactoryGeneratedClass, key, value)

    if class_name is not None:
        FactoryGeneratedClass.__qualname__ = class_name
        FactoryGeneratedClass.__name__ = class_name

    return FactoryGeneratedClass


@pytest.fixture
def db():
    return pw.SqliteDatabase(':memory:', autocommit=False)


@pytest.fixture(autouse=True)
def models(db):
    """Emulate the transaction -- create a new db before each test and flush it after.

    Also, return the app.models module"""
    from src import models
    app_models = [models.User]

    db.bind(app_models, bind_refs=False, bind_backrefs=False)
    db.connect()
    db.create_tables(app_models)

    yield models

    db.drop_tables(app_models)
    db.close()


@pytest.fixture
def app(bot):
    """Our bot app, adds the magic curring `call` method to call it with fake bot"""
    from src import app
    setattr(app, 'call', lambda method, *args, **kwargs: getattr(app, method)(bot, *args, **kwargs))
    return app


@pytest.fixture
def bot():
    """Mocked instance of the bot"""
    class Bot:
        send_message = MagicMock()

    return Bot


@pytest.fixture
def user():
    """telegram.User"""
    class User(factory(
        'User',
        id='__randint',
        is_bot=False,
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        username=faker.user_name(),
    )):

        @property
        def full_name(self):
            return f'{self.first_name} {self.last_name}'

    return User


@pytest.fixture
def message():
    """telegram.Message"""
    return lambda **kwargs: factory(
        'Message',
        chat_id='__randint',
        **kwargs,
    )


@pytest.fixture
def update(message, user):
    """telegram.Update"""
    return factory(
        'Update',
        update_id='__randint',
        message=message(from_user=user()),
    )
