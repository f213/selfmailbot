import pystmark
from envparse import env

from .tpl import get_template

env.read_envfile()


class MailException(Exception):
    pass


def send_mail(to, subject, text, attachment=None, attachment_name=''):
    message = pystmark.Message(
        sender=env('MAIL_FROM'),
        to=to,
        subject=subject,
        text=text,
    )

    if attachment is not None:
        message.attach_binary(attachment.read(), attachment_name)

    result = pystmark.send(message, api_key=env('POSTMARK_API_KEY'))
    result.raise_for_status()

    return result


def send_confirmation_mail(user):
    return send_mail(
        to=user.email,
        subject='[Selfmailbot] Please confirm your email',
        text=get_template('email/confirmation.txt').render(user=user),
    )
