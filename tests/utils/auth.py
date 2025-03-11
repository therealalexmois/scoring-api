import datetime
import hashlib

from scoring_api.constants import ADMIN_LOGIN, ADMIN_SALT, SALT


def generate_auth_token(login: str, account: str = 'horns&hoofs') -> str:
    """Генерирует валидный токен."""
    if login == ADMIN_LOGIN:
        return hashlib.sha512((datetime.datetime.now().strftime('%Y%m%d%H') + ADMIN_SALT).encode('utf-8')).hexdigest()
    else:
        msg = (account + login + SALT).encode('utf-8')
        return hashlib.sha512(msg).hexdigest()
