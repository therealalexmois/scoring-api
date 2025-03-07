"""Проверка и обработка запросов."""

import datetime
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from scoring_api.constants import ADMIN_LOGIN, MAX_AGE, PHONE_COUNTRY_CODE, PHONE_LENGTH

if TYPE_CHECKING:
    from typing import Any, ClassVar


class ValidationError(Exception):
    """Исключение, возникающее при неудачной проверке."""


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


class RequestMeta(type):
    """Метакласс, в котором собраны определения полей."""

    def __new__(mcls, name: str, bases: tuple, attrs: dict) -> type:
        fields = {k: v for k, v in attrs.items() if isinstance(v, Field)}

        for k in fields:
            attrs.pop(k)

        attrs['_fields'] = fields

        return super().__new__(mcls, name, bases, attrs)


class BaseRequest(metaclass=RequestMeta):
    """Базовый класс для всех типов запросов с автоматической проверкой полей."""

    _fields: dict[str, Field] = {}

    def __init__(self, data: dict[str, 'Any']) -> None:
        self.errors: dict[str, str] = {}
        self.validated_data: dict[str, Any] = {}
        self.validate(data)

    def validate(self, data: dict[str, 'Any']) -> None:
        for field_name, field in self._fields.items():
            value = data.get(field_name)

            try:
                field.validate(value)
                self.validated_data[field_name] = value
            except ValidationError as e:
                self.errors[field_name] = str(e)

    def is_valid(self) -> bool:
        """Проверяет, что запрос действителен."""
        return not bool(self.errors)


class ClientsInterestsRequest(BaseRequest):
    """Запрос интересов клиента."""

    client_ids: 'ClassVar[ClientIDsField]' = ClientIDsField(required=True)
    date: 'ClassVar[DateField]' = DateField(required=False, nullable=True)


class OnlineScoreRequest(BaseRequest):
    """Запрос на расчет баллов в режиме онлайн."""

    first_name: 'ClassVar[CharField]' = CharField(required=False, nullable=True)
    last_name: 'ClassVar[CharField]' = CharField(required=False, nullable=True)
    email: 'ClassVar[EmailField]' = EmailField(required=False, nullable=True)
    phone: 'ClassVar[PhoneField]' = PhoneField(required=False, nullable=True)
    birthday: 'ClassVar[BirthDayField]' = BirthDayField(required=False, nullable=True)
    gender: 'ClassVar[GenderField]' = GenderField(required=False, nullable=True)


class MethodRequest(BaseRequest):
    """Запрос общего метода с аутентификацией."""

    account: 'ClassVar[CharField]' = CharField(required=False, nullable=True)
    login: 'ClassVar[CharField]' = CharField(required=True, nullable=True)
    token: 'ClassVar[CharField]' = CharField(required=True, nullable=True)
    arguments: 'ClassVar[ArgumentsField]' = ArgumentsField(required=True, nullable=True)
    method: 'ClassVar[CharField]' = CharField(required=True, nullable=False)

    def __init__(self, data):
        super().__init__(data)

    @property
    def is_admin(self) -> bool:
        """Проверьте, является ли пользователь администратором."""
        return self.validated_data.get('login') == ADMIN_LOGIN
