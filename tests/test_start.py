def test(app, bot, update):
    app.call('start', update)

    assert bot.send_message.called


def test_user_creation(app, update, models, user):
    app.call('start', update)

    saved = models.User.get(id=user.id)
    assert saved.id == user.id
    assert saved.full_name == f'{user.first_name} {user.last_name}'
    assert saved.is_confirmed is False
    assert saved.email is None


def test_second_start_for_existing_user(app, update, models, user):
    created = models.User.create(
        id=user.id,
        full_name='Petr Lvovich',
        is_confirmed=True,
        email='test@e.mail',
    )

    app.call('start', update)

    created = models.User.get(id=user.id)

    assert created.is_confirmed is True
    assert created.full_name == 'Petr Lvovich'
    assert created.email == 'test@e.mail'
