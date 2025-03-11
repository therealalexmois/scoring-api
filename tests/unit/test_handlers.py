from typing import TYPE_CHECKING

import pytest

from scoring_api.constants import ADMIN_LOGIN, HTTPStatus
from scoring_api.handlers import method_handler, MethodName

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    from pytest_mock import MockFixture

    from scoring_api.storage.interface import StorageInterface


@pytest.fixture
def context() -> dict[str, int]:
    """Создает фикстуру для контекста запроса."""
    return {}


@pytest.fixture
def headers() -> dict[str, str]:
    """Создает фикстуру для заголовков запроса."""
    return {}


@pytest.fixture
def storage_mock(mocker: 'MockFixture') -> 'StorageInterface':
    """Создает мок-хранилище для тестов `method_handler`."""
    return mocker.Mock()


def get_response(
    request: dict[str, str],
    headers: dict[str, str],
    context: dict[str, int],
    storage_mock: 'StorageInterface',
) -> tuple[dict[str, 'Any'], int]:
    """Вызывает `method_handler` и возвращает ответ."""
    return method_handler({'body': request, 'headers': headers}, context, storage_mock)


@pytest.mark.parametrize(
    'request_data',
    [{}],
    ids=['test_method_handler__empty_request'],
)
def test_method_handler__empty_request(
    request_data: dict[str, str], headers: dict[str, str], context: dict[str, int], storage_mock: 'StorageInterface'
) -> None:
    """Тестирует пустой запрос."""
    response, code = get_response(request_data, headers, context, storage_mock)
    assert code == HTTPStatus.INVALID_REQUEST.value
    assert 'error' in response


@pytest.mark.parametrize(
    'request_data',
    [
        {'account': 'horns&hoofs', 'login': 'h&f', 'method': MethodName.ONLINE_SCORE},
        {'account': 'horns&hoofs', 'login': 'h&f', 'arguments': {}},
        {'account': 'horns&hoofs', 'method': MethodName.ONLINE_SCORE, 'arguments': {}},
    ],
    ids=lambda req: f'test_method_handler__invalid_request: {req}',
)
def test_method_handler__invalid_request(
    request_data: dict[str, str], headers: dict[str, str], context: dict[str, int], storage_mock: 'StorageInterface'
) -> None:
    """Тестирует обработку запроса с недопустимой структурой метода."""
    response, code = get_response(request_data, headers, context, storage_mock)
    assert code == HTTPStatus.INVALID_REQUEST.value
    assert 'error' in response


@pytest.mark.parametrize(
    'auth_valid',
    [False],
    ids=['test_method_handler__unauthorized'],
)
def test_method_handler__unauthorized_request(
    mocker: 'MockFixture',
    make_valid_api_request: 'Callable[..., dict[str, Any]]',
    auth_valid: bool,
    headers: dict[str, str],
    context: dict[str, int],
    storage_mock: 'StorageInterface',
) -> None:
    """Тестирует обработку запроса с неудачной аутентификацией."""
    mocker.patch('scoring_api.handlers.is_authenticated', return_value=auth_valid)

    request_data = make_valid_api_request(method=MethodName.ONLINE_SCORE)
    response, code = get_response(request_data, headers, context, storage_mock)

    assert code == HTTPStatus.FORBIDDEN.value
    assert 'error' in response


@pytest.mark.parametrize(
    'arguments',
    [
        {},
        {'phone': '79175002040'},
        {'phone': '89175002040', 'email': 'stupnikov@otus.ru'},
        {'phone': '79175002040', 'email': 'stupnikovotus.ru'},
        {'phone': '79175002040', 'email': 'stupnikov@otus.ru', 'gender': -1},
        {'phone': '79175002040', 'email': 'stupnikov@otus.ru', 'gender': '1'},
        {'phone': '79175002040', 'email': 'stupnikov@otus.ru', 'gender': 1, 'birthday': '01.01.1890'},
        {'phone': '79175002040', 'email': 'stupnikov@otus.ru', 'gender': 1, 'birthday': 'XXX'},
        {'phone': '79175002040', 'email': 'stupnikov@otus.ru', 'gender': 1, 'birthday': '01.01.2000', 'first_name': 1},
        {
            'phone': '79175002040',
            'email': 'stupnikov@otus.ru',
            'gender': 1,
            'birthday': '01.01.2000',
            'first_name': 's',
            'last_name': 2,
        },
        {'phone': '79175002040', 'birthday': '01.01.2000', 'first_name': 's'},
        {'email': 'stupnikov@otus.ru', 'gender': 1, 'last_name': 2},
    ],
    ids=lambda args: f'test_handle_online_score__invalid_request: {args}',
)
def test_handle_online_score__invalid_request(
    arguments: dict[str, 'Any'],
    mocker: 'MockFixture',
    make_valid_api_request: 'Callable[..., dict[str, Any]]',
    storage_mock: 'StorageInterface',
    headers: dict[str, str],
    context: dict[str, int],
) -> None:
    """Тестирует обработку запроса `online_score` с некорректными аргументами."""
    mocker.patch('scoring_api.auth.is_authenticated', return_value=True)

    request = make_valid_api_request(method='online_score', arguments=arguments)
    response, code = get_response(request, headers, context, storage_mock)

    assert code == HTTPStatus.INVALID_REQUEST.value, f'Expected 400, got {code}. Arguments: {arguments}'
    assert 'error' in response, 'Expected error message in response'


@pytest.mark.parametrize(
    'arguments, expected_score',
    [
        ({'phone': '79175002040', 'email': 'stupnikov@otus.ru'}, 3.0),
        ({'phone': 79175002040, 'email': 'stupnikov@otus.ru'}, 3.0),
        ({'gender': 1, 'birthday': '01.01.2000', 'first_name': 'a', 'last_name': 'b'}, 2.0),  # Fixed from 3.5
        ({'gender': 0, 'birthday': '01.01.2000'}, 1.5),
        ({'gender': 2, 'birthday': '01.01.2000'}, 1.5),
        ({'first_name': 'a', 'last_name': 'b'}, 0.5),
        (
            {
                'phone': '79175002040',
                'email': 'stupnikov@otus.ru',
                'gender': 1,
                'birthday': '01.01.2000',
                'first_name': 'a',
                'last_name': 'b',
            },
            5.0,  # Fixed from 4.5
        ),
    ],
    ids=[
        'test_handle_online_score__valid_phone_email_1',
        'test_handle_online_score__valid_phone_email_2',
        'test_handle_online_score__valid_birthday_gender_1',
        'test_handle_online_score__valid_birthday_gender_2',
        'test_handle_online_score__valid_birthday_gender_3',
        'test_handle_online_score__valid_first_last_name',
        'test_handle_online_score__valid_all_fields',
    ],
)
def test_handle_online_score__request_ok(
    arguments: dict[str, str],
    expected_score: float,
    make_valid_api_request: 'Callable[..., dict[str, Any]]',
    headers: dict[str, str],
    context: dict[str, int],
    storage_mock: 'StorageInterface',
) -> None:
    """Тестирует валидные запросы `handle_online_score`."""
    storage_mock.cache_get.return_value = None  # Mock cache to return None

    request_data = make_valid_api_request(MethodName.ONLINE_SCORE, arguments=arguments)
    response, code = get_response(request_data, headers, context, storage_mock)

    assert code == HTTPStatus.OK.value
    assert 'score' in response
    assert isinstance(response['score'], float)
    assert response['score'] == expected_score  # ✅ Now matches correct values


def test_handle_online_score__admin_request_ok(
    make_valid_api_request: 'Callable[..., dict[str, Any]]',
    headers: dict[str, str],
    context: dict[str, int],
    storage_mock: 'StorageInterface',
) -> None:
    """Тестирует `handle_online_score` для администратора."""
    request_data = make_valid_api_request(
        method=MethodName.ONLINE_SCORE,
        login=ADMIN_LOGIN,
        arguments={'phone': '79175002040', 'email': 'stupnikov@otus.ru'},
    )
    response, code = get_response(request_data, headers, context, storage_mock)
    expected_score = 42
    assert code == HTTPStatus.OK.value
    assert response.get('score') == expected_score


@pytest.mark.parametrize(
    'client_ids, storage_data, expected_response',
    [
        (
            [1, 2, 3],
            {'i:1': '["sports"]', 'i:2': '["travel"]', 'i:3': '["music"]'},
            {'1': ['sports'], '2': ['travel'], '3': ['music']},
        ),
        ([5], {'i:5': '["gaming"]'}, {'5': ['gaming']}),
        ([10, 11, 12], {}, {'10': [], '11': [], '12': []}),  # No cache
    ],
    ids=[
        'test_handle_clients_interests__multiple_ids',
        'test_handle_clients_interests__single_id',
        'test_handle_clients_interests__no_cache',
    ],
)
def test_handle_clients_interests__ok(  # noqa: PLR0913
    make_valid_api_request: 'Callable[..., dict[str, Any]]',
    client_ids: list[int],
    storage_data: dict[str, str],
    expected_response: dict[str, list[str]],
    headers: dict[str, str],
    context: dict[str, int],
    storage_mock: 'StorageInterface',
) -> None:
    """Тестирует `handle_clients_interests` с валидными client_ids."""

    def mock_get(key: str) -> str | None:
        return storage_data.get(key)

    storage_mock.get.side_effect = mock_get

    request_data = make_valid_api_request(method=MethodName.CLIENTS_INTERESTS, arguments={'client_ids': client_ids})
    response, code = get_response(request_data, headers, context, storage_mock)

    assert code == HTTPStatus.OK.value
    assert response == expected_response
