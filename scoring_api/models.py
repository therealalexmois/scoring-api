"""Модели для общих структур данных."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from scoring_api.constants import HTTPStatus

if TYPE_CHECKING:
    from typing import Any


@dataclass
class HTTPResponse:
    """Представляет собой стандартизированный ответ HTTP об успехе."""

    response: dict[str, 'Any']
    status: HTTPStatus = HTTPStatus.OK

    def as_tuple(self) -> tuple[dict[str, 'Any'], int]:
        """Возвращает ответ в виде кортежа с целочисленным кодом состояния."""
        return {'response': self.response}, self.status.value

    def __getitem__(self, index: int) -> dict[str, 'Any'] | int:
        """Разрешить распаковку как кортежа."""
        return self.as_tuple()[index]


@dataclass
class HTTPErrorResponse:
    """Представляет собой стандартизированный ответ на ошибку HTTP."""

    error: str
    status: 'HTTPStatus'

    def as_tuple(self) -> tuple[dict[str, str], int]:
        """Возвращает ошибку в виде кортежа."""
        return {'error': self.error}, self.status.value

    def __getitem__(self, index: int) -> dict[str, 'Any'] | int:
        """Allow unpacking like a tuple."""
        return self.as_tuple()[index]
