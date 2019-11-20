import sentry_sdk
from flask import Flask, g, render_template
from flask_env import MetaFlaskEnv
from sentry_sdk.integrations.flask import FlaskIntegration
from telegram import Bot

from .models import get_user_by_confirmation_link


class Configuration(metaclass=MetaFlaskEnv):
    DEBUG = False
    PORT = 5000
    BOT_TOKEN = ''
    SENTRY_DSN = None


app = Flask(__name__)
app.config.from_object(Configuration)

if Configuration.SENTRY_DSN is not None:
    sentry_sdk.init(Configuration.SENTRY_DSN, integrations=[FlaskIntegration()])


def get_bot():
    return Bot(app.config['BOT_TOKEN'])


@app.before_request
def init_bot():
    g.bot = get_bot()


@app.route('/confirm/<key>/')
def confirm(key):
    user = get_user_by_confirmation_link(key)

    if user is None:
        return render_template('html/confirmation_failure.html')

    user.is_confirmed = True
    user.save()

    g.bot.send_message(chat_id=user.chat_id, text=render_template('messages/email_is_confirmed.txt'))

    return render_template('html/confirmation_ok.html')
