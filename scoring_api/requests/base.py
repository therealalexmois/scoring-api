# ruff: noqa: D102, D107, ANN401
"""Базовый класс для всех типов запросов с автоматической проверкой полей."""

from typing import TYPE_CHECKING

from scoring_api.requests.exceptions import ValidationError
from scoring_api.requests.fields import Field

if TYPE_CHECKING:
    from typing import Any


class RequestMeta(type):
    """Метакласс, в котором собраны определения полей."""

    def __new__(cls, name: str, bases: tuple[type, ...], attrs: dict[str, 'Any']) -> type:
        fields = {k: v for k, v in attrs.items() if isinstance(v, Field)}

        for k in fields:
            attrs.pop(k)

        attrs['_fields'] = fields

        return super().__new__(cls, name, bases, attrs)


class BaseRequest(metaclass=RequestMeta):
    """Базовый класс для всех типов запросов с автоматической проверкой полей."""

    _fields: dict[str, Field] = {}

    def __init__(self, data: dict[str, 'Any']) -> None:
        self.errors: dict[str, list[str]] = {}
        self.validated_data: dict[str, Any] = {}
        self.validate(data)

    def validate(self, data: dict[str, 'Any']) -> None:
        """Проверяет и валидирует все поля запроса."""
        for field_name, field in self._fields.items():
            value = data.get(field_name)

            if value is None:
                if field.required:
                    self.errors.setdefault(field_name, []).append('Field is required')
                continue

            try:
                field.validate(value)
                self.validated_data[field_name] = value
            except ValidationError as e:
                self.errors.setdefault(field_name, []).append(str(e))

    def is_valid(self) -> bool:
        """Проверяет, что запрос действителен."""
        return not bool(self.errors)
