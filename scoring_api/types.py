"""Определения типов для функций API скоринга."""

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from scoring_api.storage.interface import StorageInterface


MethodHandlerType = Callable[[dict[str, 'Any'], dict[str, 'Any'], 'StorageInterface'], tuple[dict[str, 'Any'], int]]
"""Псевдоним типа для функций-обработчиков методов.

Arguments:
- dict: Словарь запроса, содержащий "body" и "headers".
- dict: Словарь контекста, содержащий такие метаданные, как request_id.
- dict | None: Объект хранилища, может быть `None` или обработчиком хранилища.

Returns:
- tuple: Словарь ответов и код состояния HTTP.
"""
