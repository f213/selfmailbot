from functools import wraps
from inspect import signature
from typing import Any, Callable, Coroutine

from telegram import Update
from telegram.ext import CallbackContext, filters

from .models import User, get_user_instance
from .t import HumanMessage, MessageUpdate


def _get_user(update: MessageUpdate) -> User:
    return get_user_instance(
        update.message.from_user,  # type: ignore[arg-type]
        chat_id=update.message.chat_id,
    )


def reply(fn: Callable) -> Callable[[Update, CallbackContext], Coroutine]:
    params = signature(fn).parameters

    @wraps(fn)
    async def call(update: Update, context: CallbackContext) -> Any:
        kwargs: dict[str, Any] = {
            "update": update,
        }
        if "user" in params:
            kwargs["user"] = _get_user(update)  # type: ignore[arg-type]

        if "context" in params:
            kwargs["context"] = context

        return await fn(**kwargs)

    return call


class Filter(filters.MessageFilter):
    def filter(self, message: HumanMessage) -> bool:  # type: ignore[override]
        return False


__all__ = [
    "reply",
    "Filter",
]
