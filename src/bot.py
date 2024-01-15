import asyncio
import os
from pathlib import Path

import kombu
import uvicorn
from asgiref.wsgi import WsgiToAsgi
from dotenv import load_dotenv
from flask import Flask, Response, request
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, filters

from . import celery as tasks
from .framework import reply
from .helpers import download, enable_logging, get_subject, init_sentry
from .models import User, create_tables, get_user_instance
from .t import HumanMessage, MessageUpdate, TextMessageUpdate
from .tpl import render

load_dotenv()


@reply
async def start(update: TextMessageUpdate) -> None:
    await update.message.reply_text(
        text=render("hello_message"),
    )


@reply
async def reset_email(update: TextMessageUpdate, user: User) -> None:
    user.email = None
    user.is_confirmed = False
    user.save()

    await update.message.reply_text(text=render("email_is_reset"), reply_markup=ReplyKeyboardRemove())


@reply
async def confirm_email(update: TextMessageUpdate, user: User) -> None:
    key = update.message.text.strip()

    if user.confirmation != key:
        await update.message.reply_text(text=render("confirmation_failure"))
        return

    user.is_confirmed = True
    user.save()

    await update.message.reply_text(text=render("email_is_confirmed"))


@reply
async def send_text_message(update: TextMessageUpdate, user: User) -> None:
    text = update.message.text
    subject = get_subject(text)

    send = tasks.send_text.si(
        user_id=user.pk,
        subject=subject,
        text=text,
    )
    if "@" in text:
        send.apply_async()
        await update.message.reply_text(text=render("message_is_sent", invite_to_change_email=("@" in text)))
    else:
        send.apply_async(
            link=tasks.react.si(
                chat_id=update.message.chat_id,
                message_id=update.message.message_id,
                reaction="👌",
            )
        )


@reply
async def send_photo(update: MessageUpdate, user: User) -> None:
    file = await update.message.photo[-1].get_file()
    photo = await download(file)
    subject = "Photo note to self"
    text = " "

    if update.message.caption is not None:
        text = update.message.caption.strip()
        if text:
            subject = f"Photo: {get_subject(text)}"

    tasks.send_file.apply_async(
        kwargs={
            "user_id": user.pk,
            "file": photo,
            "filename": Path(file.file_path).name,  # type: ignore[arg-type]
            "subject": subject,
            "text": text,
        },
        link=tasks.react.si(
            chat_id=update.message.chat_id,
            message_id=update.message.message_id,
            reaction="👌",
        ),
    )


@reply
async def prompt_for_setting_email(update: TextMessageUpdate) -> None:
    await update.message.reply_text(text=render("please_send_email"))


@reply
async def send_confirmation(update: TextMessageUpdate, user: User) -> None:
    email = update.message.text.strip()

    if User.select().where(User.email == email):
        await update.message.reply_text(text=render("email_is_occupied"))
        return

    user.email = email
    user.save()

    tasks.send_confirmation_mail.delay(user.pk)

    await update.message.reply_text(
        text=render("confirmation_message_is_sent", user=user),
    )


@reply
async def prompt_for_confirm(update: TextMessageUpdate) -> None:
    reply_markup = ReplyKeyboardMarkup([["Change email"]])
    await update.message.reply_text(render("waiting_for_confirmation"), reply_markup=reply_markup)


class UserWithoutEmailFilter(filters.MessageFilter):
    def filter(self, message: HumanMessage) -> bool:
        user = get_user_instance(message.from_user, message.chat_id)

        return user.email is None


class ConfirmedUserFilter(filters.MessageFilter):
    def filter(self, message: HumanMessage) -> bool:
        user = get_user_instance(message.from_user, message.chat_id)

        return user.email is not None and user.is_confirmed is True


def bot_app() -> Application:
    bot_token = os.getenv("BOT_TOKEN")
    if bot_token is None:
        raise RuntimeError("Please set BOT_TOKEN")  # NOQA: TRY003

    application = ApplicationBuilder().token(bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reset", reset_email))
    application.add_handler(
        MessageHandler(UserWithoutEmailFilter() & filters.TEXT & filters.Regex("@"), send_confirmation)
    )  # looks like email, so send confirmation to it
    application.add_handler(
        MessageHandler(
            ~ConfirmedUserFilter() & filters.TEXT & filters.Regex("Change email"),
            reset_email,
        )
    )  # change email
    application.add_handler(
        MessageHandler(
            ~ConfirmedUserFilter() & filters.TEXT & filters.Regex(r"\w{8}\-\w{4}\-\w{4}\-\w{4}\-\w{12}"),
            confirm_email,
        )
    )  # confirm email
    application.add_handler(MessageHandler(UserWithoutEmailFilter(), prompt_for_setting_email))
    application.add_handler(MessageHandler(~ConfirmedUserFilter(), prompt_for_confirm))
    application.add_handler(MessageHandler(ConfirmedUserFilter() & filters.TEXT, send_text_message))
    application.add_handler(MessageHandler(ConfirmedUserFilter() & filters.PHOTO, send_photo))

    return application


def flask_app_from_bot(bot_app: Application) -> uvicorn.Server:
    flask_app = Flask("bot_webhook")
    secret = os.getenv("INCOMING_WEBHOOK_SECRET")

    @flask_app.post(f"/telegram-webhook-{secret}")
    async def telegram() -> Response:
        """Telegram updates"""
        await bot_app.update_queue.put(Update.de_json(data=request.json, bot=bot_app.bot))
        return Response(status=200)

    @flask_app.get("/healthcheck")
    def healthcheck() -> Response:
        with kombu.Connection(os.getenv("CELERY_BROKER_URL")) as connection:
            connection.connect()
            return Response("ok")

    return uvicorn.Server(
        config=uvicorn.Config(
            app=WsgiToAsgi(flask_app),  # type: ignore[no-untyped-call]
            port=int(os.getenv("PORT", default=8000)),
            host="0.0.0.0",
        )
    )


async def prod(bot_app: Application) -> None:
    init_sentry()
    flask = flask_app_from_bot(bot_app)
    url = os.getenv("INCOMING_WEBHOOK_URL")
    secret = os.getenv("INCOMING_WEBHOOK_SECRET")
    async with bot:
        await bot_app.bot.set_webhook(url=f"{url}/telegram-webhook-{secret}", allowed_updates=Update.ALL_TYPES)
        await bot.start()
        await flask.serve()
        await bot.stop()


def dev(bot: Application) -> None:
    enable_logging()
    bot.run_polling()


if __name__ == "__main__":
    create_tables()
    bot = bot_app()

    if os.getenv("BOT_ENV", default="dev") == "production":
        asyncio.run(prod(bot))
    else:
        dev(bot)
