class AppException(Exception):
    ...


class AnonymousMessage(AppException):
    """Message without a user"""


class WrongTelegramResponse(AppException):
    """Wrong response what direct calling telegram API"""
