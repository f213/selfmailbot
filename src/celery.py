from io import BytesIO

import sentry_sdk
from celery import Celery
from envparse import env
from sentry_sdk.integrations.celery import CeleryIntegration

from .mail import send_mail
from .models import User
from .tpl import get_template

env.read_envfile()

celery = Celery("app")

celery.conf.update(
    broker_url=env("CELERY_BROKER_URL"),
    task_always_eager=env("CELERY_ALWAYS_EAGER", cast=bool, default=False),
    task_serializer="pickle",  # we transfer binary data like photos or voice messages,
    accept_content=["pickle"],
)

if env("SENTRY_DSN", default=None) is not None:
    sentry_sdk.init(env("SENTRY_DSN"), integrations=[CeleryIntegration()])


@celery.task
def send_confirmation_mail(user_id: int) -> None:
    user = User.get(User.pk == user_id)
    send_mail(
        to=user.email,
        subject="[Selfmailbot] Confirm your email",
        text=get_template("email/confirmation.txt").render(user=user),
    )


@celery.task
def send_text(user_id: int, subject: str, text: str) -> None:
    user = User.get(User.pk == user_id)

    send_mail(
        to=user.email,
        subject=subject,
        text=text,
    )


@celery.task
def send_file(user_id: int, file: BytesIO, filename: str, subject: str, text: str = " ") -> None:
    user = User.get(User.pk == user_id)

    send_mail(
        to=user.email,
        text=text,
        subject=subject,
        attachment=file,
        attachment_name=filename,
    )
