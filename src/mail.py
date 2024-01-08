import os
from io import BytesIO

import pystmark
from dotenv import load_dotenv

from .models import User
from .tpl import get_template

load_dotenv()


class MailException(Exception):
    pass


def send_mail(
    to: str,
    subject: str,
    text: str,
    attachment: BytesIO | None = None,
    attachment_name: str = "",
) -> None:
    message = pystmark.Message(
        sender=os.getenv("MAIL_FROM"),
        to=to,
        subject=subject,
        text=text,
    )

    if attachment is not None:
        message.attach_binary(attachment.read(), attachment_name)

    result = pystmark.send(message, api_key=os.getenv("POSTMARK_API_KEY"))
    result.raise_for_status()


def send_confirmation_mail(user: User) -> None:
    send_mail(
        to=user.email,
        subject="[Selfmailbot] Please confirm your email",
        text=get_template("email/confirmation.txt").render(user=user),
    )
