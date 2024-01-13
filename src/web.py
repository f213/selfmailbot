from dotenv import load_dotenv
from flask import Flask, render_template

from .helpers import init_sentry
from .models import get_user_by_confirmation_link

load_dotenv()

app = Flask("confirmation_webapp")

init_sentry()


@app.route("/confirm/<key>/")
def confirm(key: str) -> str:
    user = get_user_by_confirmation_link(key)

    if user is None:
        return render_template("html/confirmation_failure.html")

    user.is_confirmed = True
    user.save()

    return render_template("html/confirmation_ok.html")
