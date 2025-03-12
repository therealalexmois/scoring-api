import socket
from typing import TYPE_CHECKING

import pytest
from pymemcache.exceptions import MemcacheError

from scoring_api.storage.memcached import MemcacheStorage

if TYPE_CHECKING:
    from pytest_docker.plugin import Services
    from pytest_mock import MockerFixture


def is_responsive(host: str, port: int) -> bool:
    """Проверяет готовность Memcached, попытавшись установить TCP-соединение."""
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except (OSError, ConnectionError):
        return False


@pytest.fixture(scope='session')
def memcached_container(docker_ip: str, docker_services: 'Services') -> str:
    """Ждет, пока Memcached будет готов, и возвращает строку подключения."""
    port = docker_services.port_for('memcached', 11211)

    docker_services.wait_until_responsive(timeout=30.0, pause=0.5, check=lambda: is_responsive(docker_ip, port))

    return f'{docker_ip}:{port}'


@pytest.fixture
def memcached_storage(memcached_container) -> MemcacheStorage:
    """Создает экземпляр MemcacheStorage с помощью тестового контейнера."""
    host, port = memcached_container.split(':')
    return MemcacheStorage(host=host, port=int(port))


def test_memcached__connection(memcached_storage: MemcacheStorage) -> None:
    """Проверяет подключение к Memcached."""
    assert memcached_storage.client is not None


@pytest.mark.parametrize(
    'key, value',
    [
        ('test_key_str', 'test_value'),
        ('test_key_int', 123),
        ('test_key_float', 12.34),
    ],
    ids=['set_get_string', 'set_get_integer', 'set_get_float'],
)
def test_memcached__set_get(memcached_storage: MemcacheStorage, key: str, value: str | float) -> None:
    """Тестирует запись и чтение значений в Memcached."""
    memcached_storage.cache_set(key, value)
    stored_value = memcached_storage.cache_get(key)
    assert stored_value == str(value)


@pytest.mark.parametrize('key', ['non_existing_key'], ids=['missing_key'])
def test_memcached__cache_get(memcached_storage: MemcacheStorage, key: str) -> None:
    """Тестирует `cache_get`, который не должен выбрасывать исключения при отсутствии ключа."""
    assert memcached_storage.cache_get(key) is None


def test_memcached__cache_get_error_handling(mocker: 'MockerFixture', memcached_storage: MemcacheStorage) -> None:
    """Тестирует, что cache_get не вызывает исключений, когда Memcached недоступен."""
    mock_get = mocker.patch.object(memcached_storage.client, 'get', side_effect=Exception('Mocked Memcached failure'))

    result = memcached_storage.cache_get('any_key')

    assert mock_get.called
    assert result is None


def test_memcached__set_error_handling(mocker: 'MockerFixture', memcached_storage: MemcacheStorage) -> None:
    """Тестирует обработку ошибок при записи в `cache_set`."""
    mocker.patch.object(memcached_storage.client, 'set', side_effect=MemcacheError('Mocked error'))
    try:
        memcached_storage.cache_set('any_key', 'any_value')
    except Exception as e:
        pytest.fail(f'cache_set should not raise exceptions: {e}')
