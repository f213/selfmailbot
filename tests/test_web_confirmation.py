import uuid

import pytest


@pytest.fixture(autouse=True)
def user(db_user):
    return db_user()


def test_confirmation_ok(client, user):
    got = client.get(f"/confirm/{user.confirmation}/")

    assert "confirmation ok" in str(got.data)


def test_user_is_notified(client, user, bot):
    client.get(f"/confirm/{user.confirmation}/")

    assert bot.send_message.called

    kwargs = bot.send_message.call_args[1]

    assert kwargs["chat_id"] == user.chat_id
    assert "confirmed" in kwargs["text"]


def test_user_is_conrirmed(client, user, models):
    client.get(f"/confirm/{user.confirmation}/")

    user = models.User.get(pk=user.pk)

    assert user.is_confirmed is True


def test_key_mismatch(client):
    got = client.get(f"/confirm/{uuid.uuid4()}/")

    assert "confirmation failure" in str(got.data)


def test_user_is_not_confirmed(client, user, models):
    client.get(f"/confirm/{uuid.uuid4()}/")

    user = models.User.get(pk=user.pk)

    assert user.is_confirmed is False
