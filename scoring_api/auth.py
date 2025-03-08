"""Модуль аутентификации для проверки доступа к API."""

import datetime
import hashlib
import logging
from typing import TYPE_CHECKING

from scoring_api.constants import ADMIN_SALT, SALT

if TYPE_CHECKING:
    from scoring_api.requests import MethodRequest


def check_auth(request: 'MethodRequest') -> bool:
    """Проверяет, аутентифицирован ли запрос.

    Args:
        request: Объект запроса, содержащий данные аутентификации.

    Returns:
        True, если аутентификация подтверждена, False в противном случае.
    """
    if request.is_admin:
        digest = hashlib.sha512((datetime.datetime.now().strftime('%Y%m%d%H') + ADMIN_SALT).encode('utf-8')).hexdigest()
        logging.info(f'🪚 Admin Auth Digest: {digest}')
        return digest == request.validated_data['token']

    digest = hashlib.sha512(
        (request.validated_data.get('account', '') + request.validated_data['login'] + SALT).encode('utf-8')
    ).hexdigest()

    logging.info(f'🪚 User Auth Digest: {digest}')
    return digest == request.validated_data['token']
