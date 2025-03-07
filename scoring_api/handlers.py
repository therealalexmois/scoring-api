"""Обработчики для различных методов API."""

from typing import TYPE_CHECKING

from scoring_api.auth import check_auth
from scoring_api.constants import ADMIN_SCORE, HTTPStatus, INVALID_REQUEST
from scoring_api.models import HTTPErrorResponse
from scoring_api.requests import ClientsInterestsRequest, MethodRequest, OnlineScoreRequest
from scoring_api.scoring import get_interests, get_score

if TYPE_CHECKING:
    from typing import Any


def handle_online_score(
    req: MethodRequest, arguments: dict[str, 'Any'], ctx: dict[str, 'Any']
) -> tuple[dict[str, 'Any'], int]:
    """Обрабатывает метод `online_score`.

    Args:
        req: Проверенный объект запроса.
        arguments: Аргументы метода.
        ctx: Контекст запроса.

    Returns:
        Словарь ответа и код состояния.
    """
    score_request = OnlineScoreRequest(arguments)

    if not score_request.is_valid():
        return {'error': score_request.errors}, INVALID_REQUEST

    required_pairs = [('phone', 'email'), ('first_name', 'last_name'), ('gender', 'birthday')]

    if not any(score_request.validated_data.get(a) and score_request.validated_data.get(b) for a, b in required_pairs):
        return {'error': 'At least one required pair of fields must be provided'}, INVALID_REQUEST

    ctx['has'] = [field for field, value in score_request.validated_data.items() if value]

    score = ADMIN_SCORE if req.is_admin else get_score(**score_request.validated_data)

    return {'score': score}, HTTPStatus.OK.value


def handle_clients_interests(arguments: dict[str, 'Any'], ctx: dict[str, 'Any']) -> tuple[dict[str, 'Any'], int]:
    """Обрабатывает метод `clients_interests`.

    Args:
        arguments: Аргументы метода.
        ctx: Контекст запроса.

    Returns:
        Словарь ответа и код состояния.
    """
    interests_request = ClientsInterestsRequest(arguments)

    if not interests_request.is_valid():
        return {'error': interests_request.errors}, INVALID_REQUEST

    ctx['nclients'] = len(interests_request.validated_data['client_ids'])

    interests = get_interests(interests_request.validated_data['client_ids'])

    return {'response': interests}, HTTPStatus.OK.value


def method_handler(
    request: dict[str, 'Any'], ctx: dict[str, 'Any'], _store: dict[str, 'Any'] | None = None
) -> tuple[dict[str, 'Any'], int]:
    """Обрабатывает запросы методов, направляя их в соответствующие обработчики.

    Args:
        request: Данные входящего запроса.
        ctx: Контекст запроса.
        _store: Хранилище данных (в настоящее время не используется).

    Returns:
        Словарь ответа и код состояния.
    """
    req = MethodRequest(request['body'])

    if not req.is_valid():
        return HTTPErrorResponse(
            ', '.join(f'{k}: {v}' for k, v in req.errors.items()), HTTPStatus.INVALID_REQUEST
        ).as_tuple()

    if not check_auth(req):
        return HTTPErrorResponse('Forbidden', HTTPStatus.FORBIDDEN).as_tuple()

    method = req.validated_data['method']
    arguments = req.validated_data['arguments']

    match method:
        case 'online_score':
            return handle_online_score(req, arguments, ctx)
        case 'clients_interests':
            return handle_clients_interests(arguments, ctx)
        case _:
            return HTTPErrorResponse('Method not found', HTTPStatus.NOT_FOUND).as_tuple()
