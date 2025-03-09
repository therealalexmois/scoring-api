# ruff: noqa: D102, D107, ANN401
"""Определение типов полей и их валидации."""

import datetime
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from scoring_api.constants import MAX_AGE, PHONE_COUNTRY_CODE, PHONE_LENGTH
from scoring_api.requests.exceptions import ValidationError

if TYPE_CHECKING:
    from typing import Any


class Field(ABC):
    """Базовый класс для полей запроса с проверкой."""

    def __init__(self, required: bool = False, nullable: bool = False) -> None:
        self.required = required
        self.nullable = nullable

    @abstractmethod
    def validate(self, value: 'Any') -> None:
        if self.required and value is None:
            raise ValidationError('This field is required')

        if not self.nullable and not value:
            raise ValidationError('This field cannot be empty')


class CharField(Field):
    """Строковое поле."""

    def validate(self, value: 'Any') -> None:
        super().validate(value)

        if value is not None and not isinstance(value, str):
            raise ValidationError('Must be a string')


class ArgumentsField(Field):
    """Dictionary field."""

    def validate(self, value: 'Any') -> None:
        if value is not None and not isinstance(value, dict):
            raise ValidationError('Must be a dictionary')


class EmailField(CharField):
    """Поле электронной почты с валидацией '@'."""

    def validate(self, value: 'Any') -> None:
        super().validate(value)
        if value and '@' not in value:
            raise ValidationError('Invalid email format')


class PhoneField(Field):
    """Поле номера телефона, который должен начинаться с '7' и состоять из 11 цифр."""

    def validate(self, value: 'Any') -> None:
        if value is None:
            return

        if not isinstance(value, (str | int)):
            raise ValidationError('Must be a string or an integer')

        value_str = str(value)
        if not value_str.startswith(str(PHONE_COUNTRY_CODE)) or len(value_str) != PHONE_LENGTH:
            raise ValidationError('Invalid phone number format')


class DateField(Field):
    """Поле даты в формате DD.MM.YYYY."""

    def validate(self, value: 'Any') -> None:
        if value is None:
            return

        if not isinstance(value, str):
            raise ValidationError('Must be a string')

        try:
            datetime.datetime.strptime(value, '%d.%m.%Y')
        except ValueError as error:
            raise ValidationError('Invalid date format') from error


class BirthDayField(DateField):
    """Date field with an age restriction (max 70 years)."""

    def validate(self, value: 'Any') -> None:
        if value is None:
            return

        super().validate(value)
        birth_date = datetime.datetime.strptime(value, '%d.%m.%Y')

        if (datetime.datetime.now().year - birth_date.year) > MAX_AGE:
            raise ValidationError('Date is too old')


class GenderField(Field):
    """Поле пола, которое должно быть равно 0, 1 или 2."""

    def validate(self, value: 'Any') -> None:
        if value is None:
            return

        if not isinstance(value, int) or value not in {0, 1, 2}:
            raise ValidationError('Invalid gender value')


class ClientIDsField(Field):
    """Поле для списка целочисленных идентификаторов клиентов."""

    def validate(self, value: 'Any') -> None:
        if not isinstance(value, list) or not all(isinstance(i, int) for i in value):
            raise ValidationError('Must be a list of integers')

        if not value:
            raise ValidationError('Client IDs cannot be empty')
