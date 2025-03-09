"""Интерфейс для реализации различных хранилищ."""

from abc import ABC, abstractmethod

from scoring_api.storage.constants import DEFAULT_CACHE_EXPIRATION_SECONDS


class StorageInterface(ABC):
    """Интерфейс хранилища для абстрагирования доступа к кэшу."""

    @abstractmethod
    def get(self, key: str) -> str | None:
        """Получает значение из хранилища."""
        pass

    @abstractmethod
    def cache_get(self, key: str) -> str | None:
        """Получает значение из кэша, не выбрасывая ошибку при недоступности хранилища."""
        pass

    @abstractmethod
    def cache_set(self, key: str, value: str | int | float, expire: int = DEFAULT_CACHE_EXPIRATION_SECONDS) -> None:
        """Устанавливает значение в кэше с временем жизни."""
        pass
