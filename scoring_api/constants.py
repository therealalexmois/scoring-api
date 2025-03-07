"""Константы для API скоринга."""

from enum import Enum


class HTTPStatus(Enum):
    """Перечисление кодов состояния HTTP и соответствующих им сообщений об ошибках."""

    OK = 200
    BAD_REQUEST = 400
    FORBIDDEN = 403
    NOT_FOUND = 404
    INVALID_REQUEST = 422
    INTERNAL_ERROR = 500

    @property
    def message(self) -> str:
        """Возвращает стандартное сообщение для каждого кода состояния HTTP."""
        return {
            self.BAD_REQUEST: 'Bad Request',
            self.FORBIDDEN: 'Forbidden',
            self.NOT_FOUND: 'Not Found',
            self.INVALID_REQUEST: 'Invalid Request',
            self.INTERNAL_ERROR: 'Internal Server Error',
        }.get(self, 'Unknown Error')


SALT = 'Otus'
ADMIN_LOGIN = 'admin'
ADMIN_SALT = '42'
ADMIN_SCORE = 42

PHONE_COUNTRY_CODE = 7
PHONE_LENGTH = 11
MAX_AGE = 70

OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND_STATUS_CODE = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: 'Bad Request',
    FORBIDDEN: 'Forbidden',
    NOT_FOUND_STATUS_CODE: 'Not Found',
    INVALID_REQUEST: 'Invalid Request',
    INTERNAL_ERROR: 'Internal Server Error',
}

UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: 'unknown',
    MALE: 'male',
    FEMALE: 'female',
}
