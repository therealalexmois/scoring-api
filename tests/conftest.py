import os
from typing import TYPE_CHECKING

import pytest

from tests.utils.auth import generate_auth_token

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    from scoring_api.handlers import MethodName

DEFAULT_LOGIN = 'h&f'
DEFAULT_ARGUMENTS = {'phone': '79175002040', 'email': 'test@example.com'}


@pytest.fixture
def make_valid_api_request() -> 'Callable[..., dict[str, Any]]':
    """Фабрика для создания корректного API-запроса с опциональными параметрами.

    Args:
        method: Название метода API (например, `MethodName.ONLINE_SCORE`).
        token: Токен аутентификации (по умолчанию сгенерированный).
        login: Логин пользователя (по умолчанию `h&f`).
        arguments: Словарь аргументов метода (по умолчанию телефон + email).

    Returns:
        Готовый API-запрос в виде словаря.
    """

    def _create(
        method: 'MethodName',
        token: str | None = None,
        login: str | None = None,
        arguments: dict[str, str] | None = None,
    ) -> dict[str, str | dict[str, str]]:
        login = login if login is not None else DEFAULT_LOGIN
        token = token if token is not None else generate_auth_token(login)
        arguments = arguments if arguments is not None else DEFAULT_ARGUMENTS

        return {
            'account': 'horns&hoofs',
            'login': login,
            'method': method,
            'token': token,
            'arguments': arguments,
        }

    return _create


@pytest.fixture(scope='session')
def docker_compose_file(pytestconfig) -> str:  # noqa: ANN001
    """Set the correct path for docker-compose.yml in tests/docker/"""
    return os.path.join(str(pytestconfig.rootdir), 'tests', 'docker', 'docker-compose.yml')
