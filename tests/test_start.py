import pytest


@pytest.fixture
def create_user_from_tg(models, user):
    def _create(**kwargs):
        created = models.get_user_instance(user)

        for key, value in kwargs.items():
            setattr(created, key, value)

        created.save()
        return created

    return _create


def test(bot_app, bot, update):
    bot_app.call('start', update)

    assert update.message.reply_text.called


def test_user_creation(bot_app, update, models, user):
    bot_app.call('start', update)

    saved = models.User.get(pk=user.id)

    assert saved.pk == user.id
    assert saved.full_name == f'{user.first_name} {user.last_name}'
    assert saved.is_confirmed is False
    assert saved.email is None


def test_second_start_for_existing_user_does_not_update_name(bot_app, update, create_user_from_tg, models):
    created = create_user_from_tg(full_name='Fixed and not updated')

    bot_app.call('start', update)
    updated = models.User.get(pk=created.pk)

    assert updated.full_name == 'Fixed and not updated'


def test_second_start_for_confirmed_user_does_not_reset_the_confirmation_flag(bot_app, update, create_user_from_tg, models):
    created = create_user_from_tg(is_confirmed=True)

    bot_app.call('start', update)
    updated = models.User.get(pk=created.pk)

    assert updated.is_confirmed is True
