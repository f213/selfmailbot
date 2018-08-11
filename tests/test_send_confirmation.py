import pytest


@pytest.fixture(autouse=True)
def send_mail(mocker):
    return mocker.patch('src.app.tasks.send_confirmation_mail.delay')


def test_occupied_email(bot_app, update, db_user):
    db_user(email='occu@pie.d')
    update.message.text = 'occu@pie.d'

    bot_app.call('send_confirmation', update)

    msg = update.message.reply_text.call_args[1]['text']
    assert 'occupied' in msg


def test_email_is_not_sent_to_occupied_one(bot_app, update, db_user, send_mail):
    db_user(email='occu@pie.d')
    update.message.text = 'occu@pie.d'

    bot_app.call('send_confirmation', update)

    assert not send_mail.called


def test_ok(bot_app, update, bot, send_mail):
    update.message.text = 'ok@e.mail'

    bot_app.call('send_confirmation', update)

    assert send_mail.called


def test_email_is_sent_to_correct_user(bot_app, update, send_mail, models):
    user = models.get_user_instance(update.message.from_user, 100500)
    update.message.text = 'ok@e.mail'

    bot_app.call('send_confirmation', update)

    send_mail.assert_called_once_with(user.pk)


def test_email_is_updated(bot_app, update, send_mail, models):
    user = models.get_user_instance(update.message.from_user, 100500)
    update.message.text = 'ok@e.mail'

    bot_app.call('send_confirmation', update)
    user = models.User.get(models.User.pk == user.pk)

    assert user.email == 'ok@e.mail'
