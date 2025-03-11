"""Модуль реализации хранилища на основе Memcached."""

import logging
import time

from pymemcache.client.base import Client
from pymemcache.exceptions import MemcacheError

from scoring_api.storage.constants import (
    DEFAULT_CACHE_EXPIRATION_SECONDS,
    DEFAULT_STORAGE_MAX_RETRIES,
    DEFAULT_STORAGE_RETRY_DELAY_SECONDS,
)
from scoring_api.storage.interface import StorageInterface

logger = logging.getLogger(__name__)

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 11211


class MemcacheStorage(StorageInterface):
    """Реализация хранилища с использованием Memcached."""

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        max_retries: int = DEFAULT_STORAGE_MAX_RETRIES,
        retry_delay: float = DEFAULT_STORAGE_RETRY_DELAY_SECONDS,
    ) -> None:
        """Создает соединение с Memcached."""
        self.host = host
        self.port = port
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.client: None | Client = None
        self._connect()

    def _connect(self) -> None:
        """Подключается к Memcached."""
        for attempt in range(self.max_retries):
            try:
                self.client = Client((self.host, self.port), timeout=1, connect_timeout=1)
                logger.info(f'Connected to Memcached at {self.host}:{self.port}')
                return
            except MemcacheError as error:
                wait_time = self.retry_delay * (2**attempt)
                logger.warning(f'⚠️ Memcached connection failed (attempt {attempt + 1}/{self.max_retries}): {error}')
                time.sleep(wait_time)

        logger.error('Failed to connect to Memcached after retries.')

    def get(self, key: str) -> str | None:
        """Получает значение из хранилища. Выбрасывает ошибку при недоступности."""
        if self.client is None:
            raise ConnectionError('Memcached is unavailable.')

        try:
            value = self.client.get(key)
            return value.decode('utf-8') if value else None
        except MemcacheError as error:
            logger.error(f'Error getting key {key} from Memcached: {error}')
            raise

    def cache_get(self, key: str) -> str | None:
        """Получает значение из кэша. Не выбрасывает ошибку при недоступности."""
        if self.client is None:
            return None

        try:
            value = self.client.get(key)
            return value.decode('utf-8') if value else None
        except MemcacheError:
            return None

    def cache_set(self, key: str, value: str | int | float, ttl: int = DEFAULT_CACHE_EXPIRATION_SECONDS) -> None:
        """Сохраняет значение в кэше с временем жизни."""
        if self.client is None:
            return

        try:
            self.client.set(key, str(value), ttl)
        except MemcacheError as error:
            logger.error(f'Error setting key {key} in Memcached: {error}')
