"""Модуль содержит функции для подсчета оценок пользователей и поиска интересов клиентов."""

import datetime
import hashlib
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scoring_api.storage.interface import StorageInterface

type Phone = str | int | None
type Email = str | None
type Birthday = datetime.date | None
type Gender = int | None
type FirstName = str | None
type LastName = str | None


def get_score(  # noqa: PLR0913
    storage: 'StorageInterface',
    phone: Phone = None,
    email: Email = None,
    birthday: Birthday = None,
    gender: Gender = None,
    first_name: FirstName = None,
    last_name: LastName = None,
) -> float:
    """Рассчитывает оценку на основе предоставленных атрибутов пользователя.

    Система подсчета очков соответствует этим правилам:
    - +1,5, если указан `телефон`.
    - +1,5, если указана `email`.
    - +1,5, если указаны `день рождения` и `гендер`.
    - +0.5, если указаны `первое_имя` и `последнее_имя`.

    Args:
        storage: Экземпляр хранилища.
        phone: Номер телефона пользователя.
        email: Адрес электронной почты пользователя.
        birthday: День рождения пользователя в формате "DD.MM.YYYY".
        gender: Пол пользователя (0, 1 или 2).
        first_name: Имя пользователя.
        last_name: Фамилия пользователя.

    Returns:
        Расчетная оценка.
    """
    key_parts = [
        first_name or '',
        last_name or '',
        phone or '',
        birthday.strftime('%Y%m%d') if birthday else '',
    ]
    key = 'uid:' + hashlib.md5(''.join(key_parts).encode('utf-8')).hexdigest()

    if score := storage.cache_get(key) is not None:
        return float(score)

    score = sum(
        [
            1.5 if phone else 0,
            1.5 if email else 0,
            1.5 if birthday and gender is not None else 0,
            0.5 if first_name and last_name else 0,
        ]
    )

    storage.cache_set(key, score, 60 * 60)
    return score


def get_interests(storage: 'StorageInterface', cid: str) -> list:
    """Возвращает интересы пользователя из кэша. Ошибка при недоступности хранилища.

    Args:
        storage: Экземпляр хранилища.
        cid: ID клиента.

    Returns:
        Список интересов.

    Raises:
        ConnectionError: Если хранилище недоступно.
    """
    key = f'i:{cid}'
    data = storage.get(key)
    return json.loads(data) if data else []
