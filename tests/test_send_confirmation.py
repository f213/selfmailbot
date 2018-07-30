import pytest


@pytest.fixture
def db_user(user, models):
    db_user = models.get_user_instance(user)
    db_user.email = 'occu@pie.d'
    db_user.save()

    return db_user


def test_occupied_email(app, update, bot, models, db_user):
    update.message.text = 'occu@pie.d'

    app.call('send_confirmation', update)

    msg = bot.send_message.call_args[1]['text']

    assert 'occupied' in msg
