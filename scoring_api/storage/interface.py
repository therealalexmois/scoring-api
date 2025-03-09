from abc import ABC, abstractmethod


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
    def cache_set(self, key: str, value: str | int | float, expire: int = 3600) -> None:
        """Устанавливает значение в кэше с временем жизни."""
        pass
