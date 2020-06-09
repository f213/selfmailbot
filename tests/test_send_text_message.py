import pytest


@pytest.fixture
def send_mail(mocker):
    return mocker.patch('src.celery.send_mail')


@pytest.fixture
def update(update):
    update.message.text = 'Слоны идут на север'

    return update


@pytest.fixture(autouse=True)
def user(update, models):
    user = models.get_user_instance(update.message.from_user, 100500)
    user.email = 'mocked@test.org'
    user.save()


def test(bot_app, update, models, send_mail, mocker):
    bot_app.call('send_text_message', update)

    send_mail.assert_called_once_with(
        to='mocked@test.org',
        subject='Слоны идут на...',
        text='Слоны идут на север',
    )
