import uuid
from random import randint
from unittest.mock import MagicMock, patch

import peewee as pw
import pytest
from faker import Faker

import base64

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
    return pw.SqliteDatabase(':memory:')


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
def bot_app(bot):
    """Our bot app, adds the magic curring `call` method to call it with fake bot"""
    from src import app
    setattr(app, 'call', lambda method, *args, **kwargs: getattr(app, method)(bot, *args, **kwargs))
    return app


@pytest.fixture
def bot(message):
    """Mocked instance of the bot"""
    class Bot:
        send_message = MagicMock()

    return Bot()


@pytest.fixture
def app(bot, mocker):
    mocker.patch('src.web.get_bot', return_value=bot)
    from src.web import app
    app.testing = True
    return app


@pytest.fixture
def tg_user():
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

    return User()


@pytest.fixture
def db_user(models):
    return lambda **kwargs: models.User.create(**{**dict(
        pk=randint(100_000_000, 999_999_999),
        is_confirmed=False,
        email='user@e.mail',
        full_name='Petrovich',
        confirmation=str(uuid.uuid4()),
        chat_id=randint(100_000_000, 999_999_999),
    ), **kwargs})


@pytest.fixture
def message():
    """telegram.Message"""
    return lambda **kwargs: factory(
        'Message',
        chat_id='__randint',
        reply_text=MagicMock(return_value=factory(message_id=100800)()),  # always 100800 as the replied message id
        **kwargs,
    )()


@pytest.fixture
def update(message, tg_user):
    """telegram.Update"""
    return factory(
        'Update',
        update_id='__randint',
        message=message(from_user=tg_user),
    )()


@pytest.fixture
def photo():
    # 1x1 png pixel, base64
    png_b64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAABHNCSVQICAgIfAhkiAAAAA1JREFUCJlj+P///38ACfsD/QjR6B4AAAAASUVORK5CYII='
    return base64.b64decode(png_b64)


@pytest.fixture
def tg_photo_file(photo):
    """telegram.File"""
    def _mock_download(custom_path=None, out=None, timeout=None):
        if out:
            out.write(photo)
        return out

    return lambda **kwargs: factory(
        'File',
        file_id='__randint',
        file_size=None,
        file_path='/tmp/path/to/file.png',
        download=MagicMock(side_effect=_mock_download),
        **kwargs,
    )()


@pytest.fixture
def tg_photo_size(tg_photo_file):
    """telegram.PhotoSize"""
    return lambda **kwargs: factory(
        'PhotoSize',
        file_id='__randint',
        width=1,
        height=1,
        get_file=MagicMock(return_value=tg_photo_file()),
        **kwargs,
    )()
