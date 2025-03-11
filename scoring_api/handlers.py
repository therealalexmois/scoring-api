"""Обработчики для различных методов API."""

from enum import Enum
from typing import TYPE_CHECKING

from scoring_api.auth import check_auth
from scoring_api.constants import ADMIN_SCORE, HTTPStatus
from scoring_api.requests.exceptions import ValidationError
from scoring_api.requests.requests import ClientsInterestsRequest, MethodRequest, OnlineScoreRequest
from scoring_api.scoring import get_interests, get_score

if TYPE_CHECKING:
    from typing import Any

    from scoring_api.storage.interface import StorageInterface


class MethodName(str, Enum):
    """Допустимые методы API."""
    ONLINE_SCORE = 'online_score'
    CLIENTS_INTERESTS = 'clients_interests'


def handle_online_score(
    req: MethodRequest, data: dict[str, 'Any'], ctx: dict[str, 'Any'], storage: 'StorageInterface'
) -> dict[str, float]:
    """Обрабатывает метод `online_score`.

    Args:
        req: Проверенный объект запроса.
        data: Аргументы метода.
        ctx: Контекст запроса.
        storage: Экземпляр хранилища.

    Returns:
        Словарь со значением `score`.

    Raises:
        ValidationError: Если запрос содержит ошибки или не переданы обязательные пары полей.
    """
    score_request = OnlineScoreRequest(data)

    if not score_request.is_valid():
        raise ValidationError([{k: v for k, v in score_request.errors.items()}])

    required_pairs = [('phone', 'email'), ('first_name', 'last_name'), ('gender', 'birthday')]

    if not req.is_admin:
        is_valid_pair_present = any(
            score_request.validated_data.get(a) is not None and score_request.validated_data.get(b) is not None
            for a, b in required_pairs
        )

        if not is_valid_pair_present:
            raise ValidationError(
                [
                    f'At least one of the following required field pairs must be provided: '
                    f'{", ".join(str(pair) for pair in required_pairs)}'
                ]
            )

    ctx['has'] = [field for field, value in score_request.validated_data.items() if value is not None]

    score = ADMIN_SCORE if req.is_admin else get_score(storage, **score_request.validated_data)

    return {'score': score}


def handle_clients_interests(
    data: dict[str, 'Any'], ctx: dict[str, 'Any'], storage: 'StorageInterface'
) -> dict[str, list[str]]:
    """Обрабатывает метод `clients_interests`.

    Args:
        data: Аргументы метода.
        ctx: Контекст запроса.
        storage: Экземпляр хранилища.

    Returns:
        Словарь с интересами пользователей.

    Raises:
        ValidationError: Если переданы некорректные данные.
    """
    interests_request = ClientsInterestsRequest(data)

    if not interests_request.is_valid():
        raise ValidationError(', '.join(f'{k}: {v}' for k, v in interests_request.errors.items()))

    client_ids = interests_request.validated_data['client_ids']
    ctx['nclients'] = len(client_ids)

    interests = get_interests(storage, client_ids)

    return interests


def method_handler(
    request: dict[str, 'Any'], ctx: dict[str, 'Any'], storage: 'StorageInterface'
) -> tuple[dict[str, 'Any'], int]:
    """Обрабатывает запросы методов, направляя их в соответствующие обработчики.

    Args:
        request: Данные входящего запроса.
        ctx: Контекст запроса.
        storage: Экземпляр хранилища.

    Returns:
        Кортеж с ответом и кодом состояния HTTP.
    """
    req: MethodRequest = MethodRequest(request['body'])

    if not req.is_valid():
        return {'error': req.errors}, HTTPStatus.INVALID_REQUEST.value

    if not check_auth(req):
        return {'error': HTTPStatus.FORBIDDEN.message}, HTTPStatus.FORBIDDEN.value

    method = req.validated_data.get('method')
    arguments = req.validated_data.get('arguments', {})

    status_code = HTTPStatus.OK.value
    response: dict[str, Any] = {'error': HTTPStatus.NOT_FOUND.message}

    try:
        match method:
            case MethodName.ONLINE_SCORE:
                response = handle_online_score(req, arguments, ctx, storage)
            case MethodName.CLIENTS_INTERESTS:
                response = handle_clients_interests(arguments, ctx, storage)
            case _:
                status_code = HTTPStatus.NOT_FOUND.value
    except ValidationError as error:
        response = {'error': str(error)}
        status_code = HTTPStatus.INVALID_REQUEST.value

    return response, status_code
