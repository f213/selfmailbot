import pytest


@pytest.fixture(autouse=True)
def send_mail(mocker):
    return mocker.patch('src.app.tasks.send_confirmation_mail.delay')


def test(bot_app, update, models, send_mail):
    user = models.get_user_instance(update.message.from_user)

    bot_app.call('resend', update)

    send_mail.assert_called_once_with(user.pk)
