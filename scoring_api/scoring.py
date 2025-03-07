"""Модуль содержит функции для подсчета оценок пользователей и поиска интересов клиентов."""

import random
from enum import Enum

type Phone = str | int | None
type Email = str | None
type Birthday = str | None
type Gender = int | None
type FirstName = str | None
type LastName = str | None


def get_score(
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
        phone: Номер телефона пользователя.
        email: Адрес электронной почты пользователя.
        birthday: День рождения пользователя в формате "DD.MM.YYYY".
        gender: Пол пользователя (0, 1 или 2).
        first_name: Имя пользователя.
        last_name: Фамилия пользователя.

    Returns:
        Расчетная оценка.
    """
    return sum(
        [
            1.5 if phone else 0,
            1.5 if email else 0,
            1.5 if birthday and gender is not None else 0,
            0.5 if first_name and last_name else 0,
        ]
    )


class Interest(Enum):
    """Перечисление интересов клиентов."""

    CARS = 'cars'
    PETS = 'pets'
    TRAVEL = 'travel'
    HI_TECH = 'hi-tech'
    SPORT = 'sport'
    MUSIC = 'music'
    BOOKS = 'books'
    TV = 'tv'
    CINEMA = 'cinema'
    GEEK = 'geek'
    OTUS = 'otus'


INTERESTS_LIST = [interest.value for interest in Interest]


def get_interests(client_ids: list[int], _date: str | None = None) -> dict[str, list[str]]:
    """Возвращает случайные интересы для каждого идентификатора клиента.

    Args:
        client_ids: Список идентификаторов клиентов.
        _date: Параметр даты (не используется).

    Returns:
        Словарь, сопоставляющий идентификаторы клиентов со списком интересов.
    """
    return {str(client_id): random.sample(INTERESTS_LIST, 2) for client_id in client_ids}
