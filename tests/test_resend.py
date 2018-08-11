import pytest


@pytest.fixture(autouse=True)
def send_mail(mocker):
    return mocker.patch('src.app.tasks.send_confirmation_mail')


def test(bot_app, update, models, send_mail):
    user = models.get_user_instance(update.message.from_user, 100500)
    user.email = 'test@test.org'
    user.save()

    bot_app.call('reset_email', update)
    user = models.User.get(models.User.pk == user.pk)

    assert user.email is None
