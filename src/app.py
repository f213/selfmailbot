import logging

from envparse import env
from telegram import Message, Update
from telegram.ext import CommandHandler, MessageHandler, Updater
from telegram.ext.filters import BaseFilter, Filters

from .mail import send_confirmation_mail
from .models import User, create_tables, get_user_instance, with_user
from .tpl import get_template

env.read_envfile()
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def reply(fn):
    """Add a with_user decorator and a render function with additional ctx"""

    def _call(*args, user, **kwargs):
        def render(tpl: str, **kwargs):
            template = get_template('messages/' + tpl + '.txt')
            return template.render(user=user, **kwargs)

        return fn(*args, **kwargs, user=user, render=render)

    return with_user(_call)


@reply
def start(bot, update: Update, user: User, **kwargs):
    update.message.reply_text(text=f'Your id is {user.id} and name is {user.full_name}')


@reply
def send_text_message(bot, update: Update, user: User, **kwargs):
    update.message.reply_text(text='Ok, sending text msg')


@reply
def send_photo(bot, update: Update, user: User, **kwargs):
    update.message.reply_text(text='Ok, sending photo')


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

    send_confirmation_mail(user)

    update.message.reply_text(text=render('confirmation_message_is_sent'))


@reply
def prompt_for_confirm(bot, update: Update, user, render):
    send_confirmation_mail(user)
    update.message.reply_text(text=render('confirmation_message_is_sent'))


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
