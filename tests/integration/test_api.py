import threading
from dataclasses import dataclass
from typing import TYPE_CHECKING

import httpx
import pytest

from scoring_api.constants import ADMIN_LOGIN, HTTPStatus
from scoring_api.handlers import MethodName
from scoring_api.server import run_server
from scoring_api.storage.memcached import MemcacheStorage

if TYPE_CHECKING:
    from collections.abc import Callable, Generator
    from typing import Any


@dataclass
class Config:
    port: int = 8082
    log_file: str | None = None


@pytest.fixture(scope='module')
def test_server() -> 'Generator[str]':
    """Запускает тестовый HTTP сервер в отдельном потоке."""
    config = Config()
    storage = MemcacheStorage()

    server_thread = threading.Thread(target=run_server, args=(config, storage), daemon=True)
    server_thread.start()

    yield f'http://localhost:{config.port}'


@pytest.fixture
def client() -> 'Generator[httpx.Client]':
    """HTTP-клиент для отправки запросов."""
    with httpx.Client() as client:
        yield client


def test_auth__valid_token(
    client: httpx.Client,
    test_server: str,
    make_valid_api_request: 'Callable[..., dict[str, Any]]',
) -> None:
    """Тестирует аутентификацию с действительным токеном.

    Ожидается:
    - Код состояния HTTP 200 (OK).
    - Ответ содержит ожидаемый результат.
    """
    request = make_valid_api_request(method=MethodName.ONLINE_SCORE)
    response = client.post(f'{test_server}/method', json=request)

    assert response.status_code == HTTPStatus.OK.value, f'Unexpected response: {response.json()}'


@pytest.mark.parametrize(
    'token',
    ['invalid_token'],
    ids=['invalid_auth_explicit_token'],
)
def test_auth__invalid_token(
    client: httpx.Client,
    test_server: str,
    make_valid_api_request: 'Callable[..., dict[str, Any]]',
    token: str,
) -> None:
    """Тестирует аутентификацию с недействительным токеном.

    Ожидается:
    - Код состояния HTTP 403 (FORBIDDEN).
    - Ответ содержит ошибку аутентификации.
    """
    request = make_valid_api_request(method=MethodName.ONLINE_SCORE, token=token)
    response = client.post(f'{test_server}/method', json=request)

    assert response.status_code == HTTPStatus.FORBIDDEN.value, f'Unexpected response: {response.json()}'


@pytest.mark.parametrize(
    'request_data, expected_status',
    [
        ({}, HTTPStatus.INVALID_REQUEST.value),
        (
            {'account': 'horns&hoofs', 'login': 'h&f', 'method': 'online_score', 'token': '', 'arguments': {}},
            HTTPStatus.FORBIDDEN.value,
        ),
        (
            {'account': 'horns&hoofs', 'login': 'admin', 'method': 'online_score', 'token': '', 'arguments': {}},
            HTTPStatus.FORBIDDEN.value,
        ),
        (
            {'account': 'horns&hoofs', 'login': 'h&f', 'method': 'clients_interests', 'arguments': {}},
            HTTPStatus.INVALID_REQUEST.value,
        ),
    ],
    ids=[
        'test_api__empty_request',
        'test_api__missing_token_non_admin',
        'test_api__missing_token_admin',
        'test_api__invalid_method',
    ],
)
def test_api__invalid_requests(
    client: httpx.Client, test_server: str, request_data: dict, expected_status: int
) -> None:
    """Тестирует различные некорректные запросы к API."""
    response = client.post(f'{test_server}/method', json=request_data)
    result = response.json()

    assert result.get('code') == expected_status, (
        f'Unexpected status code {result.get("code")} for test {request_data}. Response: {result}'
    )


@pytest.mark.parametrize(
    'arguments, expected_score',
    [
        ({'phone': '79175002040', 'email': 'stupnikov@otus.ru'}, 3.0),
        ({'phone': 79175002040, 'email': 'stupnikov@otus.ru'}, 3.0),
        ({'gender': 1, 'birthday': '01.01.2000', 'first_name': 'a', 'last_name': 'b'}, 2.0),
    ],
    ids=['valid_phone_email_1', 'valid_phone_email_2', 'valid_birthday_gender'],
)
def test_online_score__ok(
    client: httpx.Client,
    test_server: str,
    arguments: dict[str, str | int],
    expected_score: float,
    make_valid_api_request: 'Callable[..., dict[str, Any]]',
) -> None:
    """Тестирует успешный запрос к методу online_score."""
    request = make_valid_api_request(method=MethodName.ONLINE_SCORE, arguments=arguments)
    response = client.post(f'{test_server}/method', json=request)
    assert response.status_code == HTTPStatus.OK.code

    result = response.json()
    code = result.get('code')
    response = result.get('response')

    assert code == HTTPStatus.OK.code
    assert 'score' in response
    assert isinstance(response['score'], float)
    assert response['score'] == expected_score


def test_online_score_admin__ok(
    client: httpx.Client, test_server: str, make_valid_api_request: 'Callable[..., dict[str, Any]]'
) -> None:
    """Тестирует запрос с админскими правами, ожидаем 42."""
    request = make_valid_api_request(method=MethodName.ONLINE_SCORE, login=ADMIN_LOGIN)
    response = client.post(f'{test_server}/method', json=request)
    assert response.status_code == HTTPStatus.OK.code

    result = response.json()
    code = result.get('code')
    response = result.get('response')

    expected_score = 42

    assert code == HTTPStatus.OK.code
    assert response['score'] == expected_score, f'Unexpected response: {result}'


@pytest.mark.parametrize(
    'client_ids',
    [[1, 2, 3], [5], [10, 11, 12]],
    ids=['multiple_ids', 'single_id', 'different_ids'],
)
def test_get_interests__ok(
    client: httpx.Client,
    test_server: str,
    client_ids: list[int],
    make_valid_api_request: 'Callable[..., dict[str, Any]]',
) -> None:
    """Тестирует метод clients_interests с разными client_ids."""
    request = make_valid_api_request(method=MethodName.CLIENTS_INTERESTS, arguments={'client_ids': client_ids})
    response = client.post(f'{test_server}/method', json=request)
    assert response.status_code == HTTPStatus.OK.code

    result = response.json()
    assert result.get('code') == HTTPStatus.OK.code
    assert isinstance(result.get('response'), dict)
    assert all(isinstance(interests, list) for interests in result['response'].values())


@pytest.mark.parametrize(
    'client_ids',
    [[], ['invalid_id'], {'client': 'wrong_type'}],
    ids=['empty_list', 'invalid_string_id', 'wrong_type_dict'],
)
def test_clients_interests__error(
    client: httpx.Client,
    test_server: str,
    client_ids: list[int],
    make_valid_api_request: 'Callable[..., dict[str, Any]]',
) -> None:
    """Тестирует метод clients_interests с некорректными client_ids."""
    request = make_valid_api_request(method=MethodName.CLIENTS_INTERESTS, arguments={'client_ids': client_ids})
    response = client.post(f'{test_server}/method', json=request)
    result = response.json()

    assert result.get('code') == HTTPStatus.INVALID_REQUEST.code
