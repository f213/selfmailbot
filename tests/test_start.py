def test(app, bot, update, user):
    app.start(bot, update)

    assert bot.send_message.called
