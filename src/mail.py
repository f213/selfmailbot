import requests
from envparse import env

from .tpl import get_template

env.read_envfile()


class MailException(BaseException):
    pass


def get_url():
    return 'https://api.mailgun.net/v3/{}/messages'.format(env('MAILGUN_DOMAIN'))


def post(payload):
    payload = {key: value for key, value in payload.items() if value is not None and value}

    response = requests.post(get_url(), auth=('api', env('MAILGUN_API_KEY')), data=payload)
    if response.status_code != 200:
        raise MailException('Non-200 response from mailgun: {} ({})'.format(response.status_code, response.text))

    return response.json()


def send_mail(to, subject, text, user_id, variables=None):
    if variables is None:
        variables = dict()

    return post({
        'to': to,
        'from': env('MAILGUN_FROM'),
        'subject': subject,
        'text': text,
        'h:X-telegram-id': user_id,
        'h:X-Mailgun-Variables': variables,
    })


def send_confirmation_mail(user: 'User'):
    return send_mail(
        to=user.email,
        subject='[Selfmailbot] Please confirm your email',
        user_id=user.id,
        text=get_template('email/confirmation.txt').render(user=user),
    )
