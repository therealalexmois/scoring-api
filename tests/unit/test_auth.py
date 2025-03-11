import datetime
import hashlib
from typing import TYPE_CHECKING

import pytest

from scoring_api.auth import check_auth, generate_admin_auth_token, generate_auth_token
from scoring_api.constants import ADMIN_SALT, SALT
from scoring_api.requests.requests import MethodRequest

if TYPE_CHECKING:
    from pytest_mock import MockFixture


@pytest.mark.parametrize(
    'login, account, expected_token',
    [
        ('user1', 'account1', hashlib.sha512(('account1user1' + SALT).encode('utf-8')).hexdigest()),
        ('admin', '', hashlib.sha512(('admin' + SALT).encode('utf-8')).hexdigest()),
        ('test', 'test_account', hashlib.sha512(('test_accounttest' + SALT).encode('utf-8')).hexdigest()),
    ],
)
def test_generate_auth_token(login: str, account: str, expected_token: str) -> None:
    """Тестирует генерацию токена для обычных пользователей."""
    assert generate_auth_token(login, account) == expected_token


def test_generate_admin_token() -> None:
    """Тестирует генерацию токена для администратора."""
    expected_token = hashlib.sha512(
        (datetime.datetime.now().strftime('%Y%m%d%H') + ADMIN_SALT).encode('utf-8')
    ).hexdigest()
    assert generate_admin_auth_token() == expected_token


@pytest.mark.parametrize(
    'is_admin, login, account, valid_token, expected',
    [
        (False, 'user1', 'account1', hashlib.sha512(('account1user1' + SALT).encode('utf-8')).hexdigest(), True),
        (False, 'user2', '', hashlib.sha512(('user2' + SALT).encode('utf-8')).hexdigest(), True),
        (
            False,
            'user1',
            'wrong_account',
            hashlib.sha512(('wrong_accoMockFixtureuntuser1' + SALT).encode('utf-8')).hexdigest(),
            False,
        ),
        (
            True,
            'admin',
            '',
            hashlib.sha512((datetime.datetime.now().strftime('%Y%m%d%H') + ADMIN_SALT).encode('utf-8')).hexdigest(),
            True,
        ),
        (True, 'admin', '', 'invalid_token', False),
    ],
)
def test_check_auth(
    mocker: 'MockFixture', is_admin: bool, login: str, account: str, valid_token: str, expected: bool
) -> None:
    """Тестирует проверку аутентификации."""
    request = mocker.Mock(spec=MethodRequest)
    request.is_admin = is_admin
    request.validated_data = {'login': login, 'account': account, 'token': valid_token}

    assert check_auth(request) == expected
