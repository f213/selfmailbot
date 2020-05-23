from base64 import b64encode

from envparse import env
from mailjet_rest import Client

from .tpl import get_template

env.read_envfile()


class MailException(Exception):
    pass


def post(payload, attachment=None):
    payload = {key: value for key, value in payload.items() if value is not None and value}

    if attachment is not None:
        payload['InlinedAttachments'] = [{
            'ContentType': 'image/png',
            'Filename': 'note.png',
            'Base64Content': b64encode(attachment.read()),
        }]

    mailjet = Client(auth=(env('MAILJET_API_KEY'), env('MAILJET_API_SECRET')), version='v3.1')

    response = mailjet.send.create(data=payload)

    if response.status_code != 200:
        raise MailException('Non-200 response from mailjet: {} ({})'.format(response.status_code, response.json()['ErrorMessage']))

    return response.json()


def send_mail(to, subject, text, user_id, attachment=None):
    return post({
        'Messages': [{
            'From': {
                'Email': env('MAILJET_FROM'),
                'Name': 'Note to self',
            },
            'To': [{
                'Email': to,
            }],
            'Subject': subject,
            'TextPart': text,
        }]
    }, attachment=attachment)


def send_confirmation_mail(user):
    return send_mail(
        to=user.email,
        subject='[Selfmailbot] Please confirm your email',
        user_id=user.id,
        text=get_template('email/confirmation.txt').render(user=user),
    )
