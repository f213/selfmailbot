import pytest


@pytest.fixture
def send_mail(mocker):
    return mocker.patch('src.celery.send_mail')


@pytest.fixture
def update(update, tg_photo_size):
    update.message.photo = [tg_photo_size()]
    update.message.caption = None
    return update


@pytest.fixture(autouse=True)
def user(update, models):
    user = models.get_user_instance(update.message.from_user, 100500)
    user.email = 'mocked@test.org'
    user.save()


def test_send_photo_with_caption(bot_app, update, models, send_mail, mocker, photo):
    update.message.caption = 'Слоны идут на север'
    bot_app.call('send_photo', update)

    attachment = send_mail.call_args[1]['attachment']
    attachment.seek(0, 0)

    assert attachment.read() == photo

    send_mail.assert_called_once_with(
        user_id=update.message.from_user.id,
        to='mocked@test.org',
        subject='Photo: Слоны идут на...',
        text='Слоны идут на север',
        variables=dict(
            message_id=100800,
            chat_id=update.message.chat_id,
        ),
        attachment=attachment,
    )


def test_send_photo_without_caption(bot_app, update, models, send_mail, mocker, photo):
    bot_app.call('send_photo', update)

    attachment = send_mail.call_args[1]['attachment']
    attachment.seek(0, 0)

    assert attachment.read() == photo

    send_mail.assert_called_once_with(
        user_id=update.message.from_user.id,
        to='mocked@test.org',
        subject='Photo note to self',
        text=' ',
        variables=dict(
            message_id=100800,
            chat_id=update.message.chat_id,
        ),
        attachment=attachment,
    )
