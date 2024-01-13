class AppException(Exception):
    ...


class AnonymousMessage(AppException):
    """Message without a user"""
