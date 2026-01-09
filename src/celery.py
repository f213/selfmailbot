import os
from io import BytesIO

import httpx
from celery import Celery
from dotenv import load_dotenv

from .exceptions import WrongTelegramResponse
from .helpers import init_sentry
from .mail import send_mail
from .models import User
from .tpl import get_template

load_dotenv()

celery = Celery("app")

celery.conf.update(
    broker_url=os.getenv("CELERY_BROKER_URL"),
    broker_connection_retry_on_startup=True,
    task_always_eager=os.getenv("CELERY_ALWAYS_EAGER", default=False),
    task_serializer="pickle",  # we transfer binary data like photos or voice messages,
    accept_content=["pickle"],
)

init_sentry()


@celery.task
def send_confirmation_mail(user_id: int) -> None:
    user = User.get(User.pk == user_id)
    send_mail(
        to=user.email,
        subject="[Selfmailbot] Confirm your email",
        text=get_template("email/confirmation.txt").render(user=user),
    )


@celery.task
def send_text(user_id: int, subject: str, text: str, reply_to: str) -> None:
    user = User.get(User.pk == user_id)

    send_mail(
        to=user.email,
        subject=subject,
        reply_to=reply_to,
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


@celery.task
def react(chat_id: str, message_id: int, reaction: str) -> None:
    """Temporary task while PTB rolls out their own reactions"""
    bot_token = os.getenv("BOT_TOKEN")

    response = httpx.post(
        f"https://api.telegram.org/bot{bot_token}/setMessageReaction",
        json={
            "chat_id": chat_id,
            "message_id": message_id,
            "reaction": [{"type": "emoji", "emoji": reaction}],
        },
    )

    if response.status_code != 200:
        raise WrongTelegramResponse
