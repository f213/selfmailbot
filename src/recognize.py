from typing import Iterable

from envparse import env
from google.cloud import speech
from google.cloud.speech import enums, types

env.read_envfile()


def do_recognition(stream: bytes) -> Iterable:
    client = speech.SpeechClient()

    audio = types.RecognitionAudio(content=stream)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.OGG_OPUS,
        sample_rate_hertz=16000,
        language_code='ru-RU',
    )
    recognition = client.long_running_recognize(config, audio).result(timeout=90)
    return [result.alternatives[0].transcript for result in recognition.results]


def recognize(stream: bytes) -> str:
    recognized = do_recognition(stream)
    return ' '.join(recognized)
