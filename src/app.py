import logging

from envparse import env
from telegram import Message, Update
from telegram.ext import CommandHandler, MessageHandler, Updater
from telegram.ext.filters import BaseFilter, Filters

from .mail import send_mail
from .models import User, create_tables, get_user_instance, with_user
from .tpl import get_template

env.read_envfile()
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@with_user
def start(bot, update: Update, user: User):
    bot.send_message(chat_id=update.message.chat_id, text=f'Your id is {user.id} and name is {user.full_name}')


@with_user
def send_text_message(bot, update: Update, user: User):
    bot.send_message(chat_id=update.message.chat_id, text='Ok, sending text msg')


@with_user
def send_photo(bot, update: Update, user: User):
    bot.send_message(chat_id=update.message.chat_id, text='Ok, sending photo')


@with_user
def prompt_for_setting_email(bot, update: Update, user: User):
    bot.send_message(chat_id=update.message.chat_id, text=get_template('messages/please_send_email.txt').render())


@with_user
def send_confirmation(bot, update: Update, user: User):
    email = update.message.text.strip()

    if User.select().where(User.email == email):
        bot.send_message(chat_id=update.message.chat_id, text=get_template('messages/email_is_occupied.txt').render())
        return

    user.email = email
    user.save()
    bot.send_message(chat_id=update.message.chat_id, text=f'ok, email {email}')


@with_user
def prompt_for_confirm(bot, update: Update, user):
    send_mail(
        to=user.email,
        subject='[Selfmailbot] Please confirm your email',
        user_id=user.id,
        text=get_template('email/confirmation.txt').render(user=user),
    )
    bot.send_message(chat_id=update.message.chat_id, text=f'Confirmation message is sent to {user.email}. Click the link from it, and we are all set up!')


class ConfirmedUserFilter(BaseFilter):
    def filter(self, message: Message):
        user = get_user_instance(message.from_user)
        return user.is_confirmed


class UserWithoutEmailFilter(BaseFilter):
    def filter(self, message: Message):
        user = get_user_instance(message.from_user)
        return user.email is None


class NonConfirmedUserFilter(BaseFilter):
    def filter(self, message: Message):
        user = get_user_instance(message.from_user)
        return user.email is not None and user.is_confirmed is False


updater = Updater(token=env('BOT_TOKEN'))
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(UserWithoutEmailFilter() & Filters.text & Filters.regex('@'), send_confirmation))
dispatcher.add_handler(MessageHandler(UserWithoutEmailFilter(), prompt_for_setting_email))
dispatcher.add_handler(MessageHandler(NonConfirmedUserFilter(), prompt_for_confirm))
dispatcher.add_handler(MessageHandler(ConfirmedUserFilter() & Filters.text, send_text_message))
dispatcher.add_handler(MessageHandler(ConfirmedUserFilter() & Filters.photo, send_photo))

if __name__ == '__main__':
    create_tables()
    updater.start_polling()
