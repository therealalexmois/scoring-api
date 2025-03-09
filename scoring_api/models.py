"""Модели для общих структур данных."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from scoring_api.constants import HTTPStatus


@dataclass
class HTTPErrorResponse:
    """Представляет собой стандартизированный ответ на ошибку HTTP."""

    status: 'HTTPStatus'
    error: str | None = None

    def __post_init__(self) -> None:
        """Автоматически устанавливает сообщение об ошибке на основе статуса, если оно не указано."""
        if self.error is None:
            self.error = self.status.message

    def as_tuple(self) -> tuple[dict[str, str], int]:
        """Возвращает ошибку в виде кортежа."""
        return {'error': self.error or self.status.message}, self.status.value

    def __getitem__(self, index: int) -> dict[str, 'Any'] | int:
        """Allow unpacking like a tuple."""
        return self.as_tuple()[index]
