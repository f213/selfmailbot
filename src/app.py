import logging

from envparse import env
from telegram import Message, Update
from telegram.ext import CommandHandler, MessageHandler, Updater
from telegram.ext.filters import BaseFilter, Filters

from models import create_tables, get_user_instance, with_user
from tpl import get_template

env.read_envfile()
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@with_user
def start(bot, update: Update, user):
    bot.send_message(chat_id=update.message.chat_id, text=f'Your id is {user.id} and name is {user.full_name}')


@with_user
def send_text_message(bot, update: Update, user):
    bot.send_message(chat_id=update.message.chat_id, text='Ok, sending text msg')


@with_user
def send_photo(bot, update: Update, user):
    bot.send_message(chat_id=update.message.chat_id, text='Ok, sending photo')


@with_user
def prompt_for_setting_email(bot, update: Update, user):
    bot.send_message(chat_id=update.message.chat_id, text=get_template('messages/please_send_email.txt').render())


@with_user
def send_confirmation(bot, update: Update, user):
    email = update.message.text.strip()

    bot.send_message(chat_id=update.message.chat_id, text=f'ok, email {email}')


@with_user
def prompt_for_confirm(bot, update: Update, user):
    bot.send_message(chat_id=update.message.chat_id, text='Please confirm email')


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
