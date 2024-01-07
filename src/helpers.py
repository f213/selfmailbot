import logging
import os
import re
import uuid
from io import BytesIO
from pathlib import Path

import sentry_sdk
import telegram


def enable_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def init_sentry() -> None:
    sentry_dsn = os.getenv("SENTRY_DSN", None)

    if sentry_dsn:
        sentry_sdk.init(sentry_dsn)


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
