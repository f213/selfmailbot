import os

import kombu
from dotenv import load_dotenv
from flask import Flask, render_template

from .helpers import init_sentry
from .models import get_user_by_confirmation_link

load_dotenv()

app = Flask("confirmation_webapp", template_folder="src/templates/html")

init_sentry()


@app.route("/healthcheck/")
def healthcheck() -> str:
    with kombu.Connection(os.getenv("CELERY_BROKER_URL")) as connection:
        connection.connect()
        return render_template("ok.html")


@app.route("/<uuid:key>/")
def confirm(key: str) -> str:
    user = get_user_by_confirmation_link(key)

    if user is None:
        return render_template("confirmation_failure.html")

    user.is_confirmed = True
    user.save()

    return render_template("confirmation_ok.html")
