"""Модуль аутентификации для проверки доступа к API."""

import datetime
import hashlib
from typing import TYPE_CHECKING

from scoring_api.constants import ADMIN_SALT, SALT

if TYPE_CHECKING:
    from scoring_api.requests.requests import MethodRequest


def generate_auth_token(login: str, account: str = '') -> str:
    """Генерирует токен аутентификации для пользователя.

    Args:
        login: Логин пользователя.
        account: Учетная запись пользователя (по умолчанию '').

    Returns:
        Строка токена.
    """
    return hashlib.sha512((account + login + SALT).encode('utf-8')).hexdigest()


def generate_admin_auth_token() -> str:
    """Генерирует токен аутентификации для администратора.

    Returns:
        Строка токена администратора.
    """
    return hashlib.sha512((datetime.datetime.now().strftime('%Y%m%d%H') + ADMIN_SALT).encode('utf-8')).hexdigest()


def is_authenticated(request: 'MethodRequest') -> bool:
    """Проверяет, аутентифицирован ли запрос.

    Args:
        request: Объект запроса, содержащий данные аутентификации.

    Returns:
        True, если аутентификация подтверждена, False в противном случае.
    """
    expected_token = (
        generate_admin_auth_token()
        if request.is_admin
        else generate_auth_token(request.validated_data['login'], request.validated_data.get('account', ''))
    )

    return bool(expected_token == request.validated_data['token'])
