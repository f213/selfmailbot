import os
from pathlib import Path

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, filters

from . import celery as tasks
from .framework import reply
from .helpers import download, enable_logging, get_subject, init_sentry
from .models import User, create_tables, get_user_instance
from .types import HumanMessage, MessageUpdate, TemplateRenderFunction, TextMessageUpdate

load_dotenv()


@reply
async def start(update: TextMessageUpdate, render: TemplateRenderFunction) -> None:
    await update.message.reply_text(
        text=render("hello_message"),
    )


@reply
async def resend(update: TextMessageUpdate, user: User, render: TemplateRenderFunction) -> None:
    tasks.send_confirmation_mail.delay(user.pk)
    await update.message.reply_text(text=render("confirmation_message_is_sent"), reply_markup=ReplyKeyboardRemove())


@reply
async def reset_email(update: TextMessageUpdate, user: User, render: TemplateRenderFunction) -> None:
    user.email = ""
    user.is_confirmed = False
    user.save()

    await update.message.reply_text(text=render("email_is_reset"), reply_markup=ReplyKeyboardRemove())


@reply
async def confirm_email(update: TextMessageUpdate, user: User, render: TemplateRenderFunction) -> None:
    key = update.message.text.strip()

    if user.confirmation != key:
        await update.message.reply_text(text=render("confirmation_failure"))
        return

    user.is_confirmed = True
    user.save()

    await update.message.reply_text(text=render("email_is_confirmed"))


@reply
async def send_text_message(update: TextMessageUpdate, user: User, render: TemplateRenderFunction) -> None:
    text = update.message.text
    subject = get_subject(text)

    await update.message.reply_text(text=render("message_is_sent"))

    tasks.send_text.delay(
        user_id=user.pk,
        subject=subject,
        text=text,
    )


@reply
async def send_photo(update: MessageUpdate, user: User, render: TemplateRenderFunction) -> None:
    file = await update.message.photo[-1].get_file()
    photo = download(file)
    subject = "Photo note to self"
    text = ""

    if update.message.caption is not None:
        text = update.message.caption.strip()
        if text:
            subject = f"Photo: {get_subject(text)}"

    await update.message.reply_text(text=render("photo_is_sent"))

    tasks.send_file.delay(
        user_id=user.pk,
        file=photo,
        filename=Path(file.file_path).name,  # type: ignore[arg-type]
        subject=subject,
        text=text,
    )


@reply
async def prompt_for_setting_email(update: TextMessageUpdate, render: TemplateRenderFunction) -> None:
    await update.message.reply_text(text=render("please_send_email"))


@reply
async def send_confirmation(update: TextMessageUpdate, user: User, render: TemplateRenderFunction) -> None:
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
async def prompt_for_confirm(update: TextMessageUpdate, render: TemplateRenderFunction) -> None:
    reply_markup = ReplyKeyboardMarkup([["Resend confirmation email"], ["Change email"]])
    await update.message.reply_text(render("waiting_for_confirmation"), reply_markup=reply_markup)


class ConfirmedUserFilter(filters.MessageFilter):
    def filter(self, message: HumanMessage) -> bool:
        user = get_user_instance(message.from_user, message.chat_id)

        return user.is_confirmed


class UserWithoutEmailFilter(filters.MessageFilter):
    def filter(self, message: HumanMessage) -> bool:
        user = get_user_instance(message.from_user, message.chat_id)

        return user.email is None


class NonConfirmedUserFilter(filters.MessageFilter):
    def filter(self, message: HumanMessage) -> bool:
        user = get_user_instance(message.from_user, message.chat_id)

        return user.email is not None and user.is_confirmed is False


def main() -> Application:
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
            NonConfirmedUserFilter() & filters.TEXT & filters.Regex("Resend confirmation email"),
            resend,
        )
    )  # resend confirmation email
    application.add_handler(
        MessageHandler(
            NonConfirmedUserFilter() & filters.TEXT & filters.Regex("Change email"),
            reset_email,
        )
    )  # change email
    application.add_handler(
        MessageHandler(
            NonConfirmedUserFilter() & filters.TEXT & filters.Regex(r"\w{8}\-\w{4}\-\w{4}\-\w{4}\-\w{12}"),
            confirm_email,
        )
    )  # confirm email
    application.add_handler(MessageHandler(UserWithoutEmailFilter(), prompt_for_setting_email))
    application.add_handler(MessageHandler(NonConfirmedUserFilter(), prompt_for_confirm))
    application.add_handler(MessageHandler(ConfirmedUserFilter() & filters.TEXT, send_text_message))
    application.add_handler(MessageHandler(ConfirmedUserFilter() & filters.PHOTO, send_photo))

    return application


if __name__ == "__main__":
    enable_logging()
    create_tables()
    init_sentry()

    app = main()

    app.run_polling()
