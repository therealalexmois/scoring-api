"""Константы для API скоринга."""

from enum import Enum


class HTTPStatus(Enum):
    """Перечисление кодов состояния HTTP и соответствующих им сообщений об ошибках."""

    code: int
    message: str

    OK = 200, 'OK'
    BAD_REQUEST = 400, 'Bad Request'
    FORBIDDEN = 403, 'Forbidden'
    NOT_FOUND = 404, 'Not Found'
    INVALID_REQUEST = 422, 'Unprocessable Entity'
    INTERNAL_ERROR = 500, 'Internal Server Error'

    def __new__(cls, code: int, message: str) -> 'HTTPStatus':
        """Позволяет устанавливать `code` и `message` как атрибуты."""
        obj = object.__new__(cls)
        obj._value_ = code
        obj.code = code
        obj.message = message
        return obj


class Gender(Enum):
    """Перечисление возможных значений пола."""

    label: str

    UNKNOWN = 0, 'unknown'
    MALE = 1, 'male'
    FEMALE = 2, 'female'

    def __new__(cls, value: int, label: str) -> 'Gender':
        """Позволяет устанавливать `value` и `label` как атрибуты."""
        obj = object.__new__(cls)
        obj._value_ = value
        obj.label = label
        return obj


SALT = 'Otus'
ADMIN_LOGIN = 'admin'
ADMIN_SALT = '42'
ADMIN_SCORE = 42

PHONE_COUNTRY_CODE = 7
PHONE_LENGTH = 11
MAX_AGE = 70
