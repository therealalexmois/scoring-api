"""Модели для общих структур данных."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from scoring_api.constants import HTTPStatus


@dataclass
class HTTPErrorResponse:
    """Представляет собой стандартизированный ответ на ошибку HTTP."""

    error: str
    status: 'HTTPStatus'

    def as_tuple(self) -> tuple[dict[str, str], int]:
        """Возвращает ошибку в виде кортежа."""
        return {'error': self.error}, self.status.value

    def __getitem__(self, index: int) -> 'Any':
        """Allow unpacking like a tuple."""
        return self.as_tuple()[index]
