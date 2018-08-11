from flask import Flask, render_template
from flask_env import MetaFlaskEnv

from .models import get_user_by_confirmation_link


class Configuration(metaclass=MetaFlaskEnv):
    DEBUG = False
    PORT = 5000


app = Flask(__name__)
app.config.from_object(Configuration)


@app.route('/confirm/<key>/')
def confirm(key):
    user = get_user_by_confirmation_link(key)

    if user is None:
        return render_template('html/confirmation_failure.html')

    user.is_confirmed = True
    user.save()

    return render_template('html/confirmation_ok.html')
