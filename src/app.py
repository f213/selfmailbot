import logging

from envparse import env
from telegram import Update
from telegram.ext import CommandHandler, Updater

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

env.read_envfile()

updater = Updater(token=env('BOT_TOKEN'))
dispatcher = updater.dispatcher


def start(bot, update: Update):
    user = update.message.from_user
    # user = User.get_or_create(id=update.effective_user.id, defaults=dict(
    #     full_name=update.effective_user.full_name,
    #     username=update.effective_user.username,
    # ))

    bot.send_message(chat_id=update.message.chat_id, text=f'Your id is {user.id} and name is {user.full_name}')


start_handler = CommandHandler('start', start)

dispatcher.add_handler(start_handler)

if __name__ == '__main__':
    updater.start_polling()
