import logging

from envparse import env
from telegram import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CommandHandler, MessageHandler, Updater
from telegram.ext.filters import BaseFilter, Filters

from . import celery as tasks
from .helpers import get_file, get_subject, reply
from .models import User, create_tables, get_user_instance

env.read_envfile()
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@reply
def start(bot, update: Update, user: User, render):
    update.message.reply_text(text=render('hello_message'))


@reply
def resend(bot, update: Update, user, render):
    tasks.send_confirmation_mail.delay(user.pk)
    update.message.reply_text(text=render('confirmation_message_is_sent'), reply_markup=ReplyKeyboardRemove())


@reply
def reset_email(bot, update: Update, user, render):
    user.email = None
    user.save()

    update.message.reply_text(text=render('email_is_reset'), reply_markup=ReplyKeyboardRemove())


@reply
def confirm_email(bot, update: Update, user, render):
    key = update.message.text.strip()
    if user.confirmation != key:
        update.message.reply_text(text=render('confirmation_failure'))
        return

    user.is_confirmed = True
    user.save()

    update.message.reply_text(text=render('email_is_confirmed'))


@reply
def send_text_message(bot, update: Update, user: User, render, **kwargs):
    text = update.message.text
    subject = get_subject(text)

    message = update.message.reply_text(text=render('message_is_sent'))

    tasks.send_text.delay(
        user_id=user.pk,
        subject=subject,
        text=text,
        variables=dict(
            message_id=message.message_id,
            chat_id=update.message.chat_id,
        ),
    )


@reply
def send_photo(bot, update: Update, user: User, render):
    file = update.message.photo[-1].get_file()
    photo = get_file(file)

    message = update.message.reply_text(text=render('photo_is_sent'))

    tasks.send_file.delay(
        user_id=user.pk,
        file=photo,
        subject='Photo note to self',
        variables=dict(
            message_id=message.message_id,
            chat_id=update.message.chat_id,
        ),
    )


@reply
def send_voice(bot, update: Update, user: User, render):
    file = update.message.voice.get_file()
    voice = get_file(file)

    message = update.message.reply_text(text=render('voice_is_sent'))

    tasks.send_file.delay(
        user_id=user.pk,
        file=voice,
        subject='Voice note to self',
        variables=dict(
            message_id=message.message_id,
            chat_id=update.message.chat_id,
        ),
    )


@reply
def prompt_for_setting_email(bot, update: Update, user: User, render):
    update.message.reply_text(text=render('please_send_email'))


@reply
def send_confirmation(bot, update: Update, user: User, render):
    email = update.message.text.strip()

    if User.select().where(User.email == email):
        update.message.reply_text(text=render('email_is_occupied'))
        return

    user.email = email
    user.save()

    tasks.send_confirmation_mail.delay(user.pk)

    update.message.reply_text(text=render('confirmation_message_is_sent'))


@reply
def prompt_for_confirm(bot, update: Update, user: User, render):
    reply_markup = ReplyKeyboardMarkup([['Resend confirmation email'], ['Change email']])
    update.message.reply_text(render('waiting_for_confirmation'), reply_markup=reply_markup)


class ConfirmedUserFilter(BaseFilter):
    def filter(self, message: Message):
        user = get_user_instance(message.from_user, message.chat_id)
        return user.is_confirmed


class UserWithoutEmailFilter(BaseFilter):
    def filter(self, message: Message):
        user = get_user_instance(message.from_user, message.chat_id)
        return user.email is None


class NonConfirmedUserFilter(BaseFilter):
    def filter(self, message: Message):
        user = get_user_instance(message.from_user, message.chat_id)
        return user.email is not None and user.is_confirmed is False


updater = Updater(token=env('BOT_TOKEN'))
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(UserWithoutEmailFilter() & Filters.text & Filters.regex('@'), send_confirmation))  # looks like email, so send confirmation to it
dispatcher.add_handler(MessageHandler(NonConfirmedUserFilter() & Filters.text & Filters.regex('Resend confirmation email'), resend))  # resend confirmation email
dispatcher.add_handler(MessageHandler(NonConfirmedUserFilter() & Filters.text & Filters.regex('Change email'), reset_email))  # change email
dispatcher.add_handler(MessageHandler(NonConfirmedUserFilter() & Filters.text & Filters.regex('\w{8}\-\w{4}\-\w{4}\-\w{4}\-\w{12}'), confirm_email))  # confirm email
dispatcher.add_handler(MessageHandler(UserWithoutEmailFilter(), prompt_for_setting_email))
dispatcher.add_handler(MessageHandler(NonConfirmedUserFilter(), prompt_for_confirm))
dispatcher.add_handler(MessageHandler(ConfirmedUserFilter() & Filters.text, send_text_message))
dispatcher.add_handler(MessageHandler(ConfirmedUserFilter() & Filters.photo, send_photo))
dispatcher.add_handler(MessageHandler(ConfirmedUserFilter() & Filters.voice, send_voice))

if __name__ == '__main__':
    create_tables()
    updater.start_polling()
