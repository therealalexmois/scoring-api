import datetime
import json
from typing import TYPE_CHECKING

import pytest

from scoring_api.scoring import get_interests, get_score

if TYPE_CHECKING:
    from pytest_mock import MockFixture

    from scoring_api.storage.interface import StorageInterface


@pytest.fixture
def storage_mock(mocker: 'MockFixture') -> 'StorageInterface':
    """Создает мок-хранилище для тестов `method_handler`."""
    return mocker.Mock()


@pytest.mark.parametrize(
    'cache_value, expected_score',
    [
        ('3.0', 3.0),
        ('1.5', 1.5),
        (None, None),
    ],
    ids=['cached_3.0', 'cached_1.5', 'no_cache'],
)
def test_get_score__cache_behavior(
    storage_mock: 'StorageInterface', cache_value: str | None, expected_score: int | None
) -> None:
    """Тестирует возврат кешированного значения, если оно есть в storage."""
    storage_mock.cache_get.return_value = cache_value

    result = get_score(storage_mock, phone='79175002040')

    if cache_value is not None:
        assert result == expected_score
    else:
        assert result > 0
    storage_mock.cache_get.assert_called_once()


@pytest.mark.parametrize(
    'phone, email, birthday, gender, first_name, last_name, expected_score',
    [
        (None, None, None, None, None, None, 0.0),
        ('79175002040', None, None, None, None, None, 1.5),
        (None, 'test@example.com', None, None, None, None, 1.5),
        ('79175002040', 'test@example.com', None, None, None, None, 3.0),
        (None, None, datetime.date(2000, 1, 1), 1, None, None, 1.5),
        (None, None, None, None, 'John', 'Doe', 0.5),
        (
            '79175002040',
            'test@example.com',
            datetime.date(2000, 1, 1),
            1,
            'John',
            'Doe',
            5.0,
        ),  # ✅ Fix: Changed from 4.5 to 5.0
    ],
    ids=[
        'no_params',
        'only_phone',
        'only_email',
        'phone_email',
        'birthday_gender',
        'first_last_name',
        'all_params',
    ],
)
def test_get_score__calculation_logic(  # noqa: PLR0913
    phone: str | None,
    email: str | None,
    birthday: datetime.date | None,
    gender: int | None,
    first_name: str | None,
    last_name: str | None,
    expected_score: float,
    storage_mock: 'StorageInterface',
) -> None:
    """Тестирует корректность расчёта оценки при различных входных параметрах."""
    storage_mock.cache_get.return_value = None

    result = get_score(storage_mock, phone, email, birthday, gender, first_name, last_name)

    assert result == expected_score
    storage_mock.cache_set.assert_called_once()  # Проверяем, что значение было закешировано


@pytest.mark.parametrize(
    'storage_data, expected_output',
    [
        (
            {'i:1': json.dumps(['sports', 'music']), 'i:2': json.dumps(['movies'])},
            {'1': ['sports', 'music'], '2': ['movies']},
        ),
        ({'i:1': json.dumps([]), 'i:2': None}, {'1': [], '2': []}),
        ({}, {'1': [], '2': []}),
    ],
    ids=['cached_data', 'partially_cached', 'no_data'],
)
def test_get_interests__cache_behavior(storage_data, expected_output, storage_mock: 'StorageInterface') -> None:
    """Тестирует извлечение интересов из кеша."""
    storage_mock.get.side_effect = lambda key: storage_data.get(key)

    result = get_interests(storage_mock, [1, 2])

    assert result == expected_output


def test_get_interests__connection_error(storage_mock: 'StorageInterface') -> None:
    """Тестирует, что функция выбрасывает ConnectionError, если хранилище недоступно."""
    storage_mock.get.side_effect = ConnectionError('Storage unavailable')

    with pytest.raises(ConnectionError, match='Storage unavailable'):
        get_interests(storage_mock, [1, 2])
