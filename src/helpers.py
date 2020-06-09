import re
import uuid
from io import BytesIO
from os import path

import telegram

from .models import with_user
from .tpl import get_template


def reply(fn):
    """Add a with_user decorator and a render function with additional ctx"""

    def _call(*args, user, **kwargs):
        def render(tpl: str, **kwargs):
            template = get_template('messages/' + tpl + '.txt')
            return template.render(user=user, **kwargs)

        return fn(*args, **kwargs, user=user, render=render)

    return with_user(_call)


def capfirst(x):
    """Capitalize the first letter of a string. Kindly borrowed from Django"""
    return x and str(x)[0].upper() + str(x)[1:]


def get_subject(text):
    """Generate subject based on message text"""
    words = [word.lower() for word in re.split(r'\s+', text)]
    words[0] = capfirst(words[0])

    if len(words) > 1:
        if len(words) in [2, 3]:
            return ' '.join(words[:3])

        return ' '.join(words[:3]) + '...'

    if len(words[0]) < 32:
        return words[0][:32]

    return words[0][:32] + '...'  # first 32 characters


def download(file: telegram.File) -> BytesIO:
    attachment = BytesIO()
    attachment.name = str(uuid.uuid4()) + '.' + path.splitext(file.file_path)[1]

    file.download(out=attachment)
    attachment.seek(0, 0)

    return attachment
