import uuid

import pytest


@pytest.fixture(autouse=True)
def user(update, models):
    user = models.get_user_instance(update.message.from_user, 100500)
    return user


def test_user_is_notified(bot_app, update, user, bot):
    update.message.text = user.confirmation
    bot_app.call("confirm_email", update)

    assert update.message.reply_text.called

    kwargs = update.message.reply_text.call_args[1]
    assert "confirmed" in kwargs["text"]


def test_user_is_confirmed(bot_app, update, user, models):
    update.message.text = user.confirmation
    bot_app.call("confirm_email", update)

    user = models.User.get(pk=user.pk)
    assert user.is_confirmed is True


def test_key_mismatch(bot_app, update, user):
    update.message.text = str(uuid.uuid4())
    bot_app.call("confirm_email", update)

    msg = update.message.reply_text.call_args[1]["text"]
    assert "wrong" in msg


def test_user_is_not_confirmed(bot_app, update, user, models):
    update.message.text = str(uuid.uuid4())
    bot_app.call("confirm_email", update)

    user = models.User.get(pk=user.pk)
    assert user.is_confirmed is False
