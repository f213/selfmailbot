import re
import uuid
from io import BytesIO
from pathlib import Path
from typing import Callable, no_type_check

import telegram

from .models import with_user
from .tpl import get_template


@no_type_check
def reply(fn: Callable) -> Callable:
    """Add a with_user decorator and a render function with additional ctx"""

    def _call(*args, user, **kwargs) -> None:
        def render(tpl: str, **kwargs):
            template = get_template("messages/" + tpl + ".txt")
            return template.render(user=user, **kwargs)

        return fn(*args, **kwargs, user=user, render=render)

    return with_user(_call)


def capfirst(x: str) -> str:
    """Capitalize the first letter of a string. Kindly borrowed from Django"""
    return x and str(x)[0].upper() + str(x)[1:]


def get_subject(text: str) -> str:
    """Generate subject based on message text"""
    words = [word.lower() for word in re.split(r"\s+", text)]
    words[0] = capfirst(words[0])

    if len(words) > 1:
        if len(words) in [2, 3]:
            return " ".join(words[:3])

        return " ".join(words[:3]) + "..."

    if len(words[0]) < 32:
        return words[0][:32]

    return words[0][:32] + "..."  # first 32 characters


async def download(file: telegram.File) -> BytesIO:
    attachment = BytesIO()
    attachment.name = str(uuid.uuid4()) + "." + Path(file.file_path).suffix  # type: ignore[arg-type]

    downloaded = await file.download_as_bytearray()
    return BytesIO(downloaded)
