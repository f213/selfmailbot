import logging

from envparse import env
from telegram import Update
from telegram.ext import CommandHandler, Updater

from .models import with_user

env.read_envfile()
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@with_user
def start(bot, update: Update, user):
    bot.send_message(chat_id=update.message.chat_id, text=f'Your id is {user.id} and name is {user.full_name}')


updater = Updater(token=env('BOT_TOKEN'))
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)

dispatcher.add_handler(start_handler)

if __name__ == '__main__':
    updater.start_polling()
