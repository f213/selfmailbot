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


@pytest.fixture
def voice():
    """1 sec ogg file without speech in base64"""
    ogg_b64 = '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'
    return base64.b64decode(ogg_b64)


@pytest.fixture
def tg_voice_file(voice):
    """telegram.File"""
    def _mock_download(custom_path=None, out=None, timeout=None):
        if out:
            out.write(voice)
        return out

    return lambda **kwargs: factory(
        'File',
        file_id='__randint',
        file_size=None,
        file_path='/tmp/path/to/file.ogg',
        download=MagicMock(side_effect=_mock_download),
        **kwargs,
    )()


@pytest.fixture
def tg_voice(tg_voice_file):
    """telegram.Voice"""
    return lambda **kwargs: factory(
        'Voice',
        file_id='__randint',
        duration=1,
        mime_type='audio/ogg',
        file_size=3645,
        get_file=MagicMock(return_value=tg_voice_file()),
        **kwargs,
    )()
