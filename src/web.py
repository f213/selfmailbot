import os

import sentry_sdk
from dotenv import load_dotenv
from flask import Flask, render_template
from sentry_sdk.integrations.flask import FlaskIntegration

from .models import get_user_by_confirmation_link

load_dotenv()

app = Flask(__name__)

if os.getenv("SENTRY_DSN") is not None:
    sentry_sdk.init(os.getenv("SENTRY_DSN"), integrations=[FlaskIntegration()])


@app.route("/confirm/<key>/")
def confirm(key: str) -> str:
    user = get_user_by_confirmation_link(key)

    if user is None:
        return render_template("html/confirmation_failure.html")

    user.is_confirmed = True
    user.save()

    return render_template("html/confirmation_ok.html")
