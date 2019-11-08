from celery import Celery
from envparse import env

from .helpers import get_subject
from .mail import send_mail
from .models import User
from .recognize import recognize
from .tpl import get_template

env.read_envfile()

celery = Celery('app')

celery.conf.update(
    broker_url=env('CELERY_BROKER_URL'),
    task_always_eager=env('CELERY_ALWAYS_EAGER', cast=bool, default=False),
    task_serializer='pickle',  # we transfer binary data like photos or voice messages,
    accept_content=['pickle'],
)


@celery.task
def send_confirmation_mail(user_id):
    user = User.get(User.pk == user_id)
    send_mail(
        to=user.email,
        subject='[Selfmailbot] Confirm your email',
        user_id=user.id,
        text=get_template('email/confirmation.txt').render(user=user),
    )


@celery.task
def send_text(user_id, subject, text, variables=None):
    user = User.get(User.pk == user_id)

    send_mail(
        to=user.email,
        user_id=user_id,
        subject=subject,
        text=text,
        variables=variables,
    )


@celery.task
def send_file(user_id, file, subject, text='', variables=None):
    user = User.get(User.pk == user_id)

    if not text:
        text = ' '

    send_mail(
        to=user.email,
        user_id=user_id,
        text=text,
        subject=subject,
        variables=variables,
        attachment=file,
    )


@celery.task
def send_recognized_voice(user_id, file, duration, variables=None):
    if duration <= 60:
        recognized_text = recognize(file.read())
        subject = 'Voice: {}'.format(get_subject(recognized_text)) if recognized_text else 'Voice note to self'
    else:
        recognized_text = ''
        subject = 'Voice note to self'

    send_file(
        user_id=user_id,
        file=file,
        subject=subject,
        text=recognized_text,
        variables=variables,
    )
