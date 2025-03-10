# ruff: noqa: D102, D107, ANN401
"""Проверка и обработка запросов."""

from datetime import datetime
from typing import TYPE_CHECKING

from scoring_api.constants import ADMIN_LOGIN
from scoring_api.requests.base import BaseRequest
from scoring_api.requests.fields import (
    ArgumentsField,
    BirthDayField,
    CharField,
    ClientIDsField,
    DateField,
    EmailField,
    GenderField,
    PhoneField,
)

if TYPE_CHECKING:
    from typing import Any, ClassVar


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

    def is_valid(self) -> bool:
        """Дополнительная валидация после основного метода."""
        valid = super().is_valid()

        if valid and 'birthday' in self.validated_data and isinstance(self.validated_data['birthday'], str):
            try:
                self.validated_data['birthday'] = datetime.strptime(
                    self.validated_data['birthday'], '%d.%m.%Y'
                ).date()
            except ValueError:
                self.errors['birthday'] = 'Invalid date format. Expected DD.MM.YYYY'
                return False

        return valid


class MethodRequest(BaseRequest):
    """Запрос общего метода с аутентификацией."""

    account: 'ClassVar[CharField]' = CharField(required=False, nullable=True)
    login: 'ClassVar[CharField]' = CharField(required=True, nullable=True)
    token: 'ClassVar[CharField]' = CharField(required=True, nullable=True)
    arguments: 'ClassVar[ArgumentsField]' = ArgumentsField(required=True, nullable=True)
    method: 'ClassVar[CharField]' = CharField(required=True, nullable=False)

    def __init__(self, data: dict[str, 'Any']):  # noqa: ANN204
        super().__init__(data)

    @property
    def is_admin(self) -> bool:
        """Проверьте, является ли пользователь администратором."""
        return self.validated_data.get('login') == ADMIN_LOGIN
