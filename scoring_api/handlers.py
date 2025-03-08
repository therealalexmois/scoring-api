"""Обработчики для различных методов API."""

from typing import TYPE_CHECKING

from scoring_api.auth import check_auth
from scoring_api.constants import ADMIN_SCORE, HTTPStatus
from scoring_api.models import HTTPErrorResponse, HTTPResponse
from scoring_api.requests import ClientsInterestsRequest, MethodRequest, OnlineScoreRequest
from scoring_api.scoring import get_interests, get_score

if TYPE_CHECKING:
    from typing import Any


def handle_online_score(
    req: MethodRequest, arguments: dict[str, 'Any'], ctx: dict[str, 'Any']
) -> 'HTTPResponse | HTTPErrorResponse':
    """Обрабатывает метод `online_score`.

    Args:
        req: Проверенный объект запроса.
        arguments: Аргументы метода.
        ctx: Контекст запроса.

    Returns:
        HTTPResponse или HTTPErrorResponse.
    """
    score_request = OnlineScoreRequest(arguments)

    if not score_request.is_valid():
        return HTTPErrorResponse(
            HTTPStatus.INVALID_REQUEST,
            ', '.join(f'{k}: {v}' for k, v in score_request.errors.items()),
        )

    required_pairs = [('phone', 'email'), ('first_name', 'last_name'), ('gender', 'birthday')]

    missing_pairs = [
        f"('{a}', '{b}')"
        for a, b in required_pairs
        if not (score_request.validated_data.get(a) and score_request.validated_data.get(b))
    ]

    if missing_pairs:
        return HTTPErrorResponse(
            HTTPStatus.INVALID_REQUEST,
            f'At least one of the following required field pairs must be provided: {", ".join(missing_pairs)}',
        )

    ctx['has'] = [field for field, value in score_request.validated_data.items() if value]

    score = ADMIN_SCORE if req.is_admin else get_score(**score_request.validated_data)

    return HTTPResponse({'score': score})


def handle_clients_interests(arguments: dict[str, 'Any'], ctx: dict[str, 'Any']) -> 'HTTPResponse | HTTPErrorResponse':
    """Обрабатывает метод `clients_interests`.

    Args:
        arguments: Аргументы метода.
        ctx: Контекст запроса.

    Returns:
        HTTPResponse или HTTPErrorResponse.
    """
    interests_request = ClientsInterestsRequest(arguments)

    if not interests_request.is_valid():
        return HTTPErrorResponse(
            HTTPStatus.INVALID_REQUEST,
            ', '.join(f'{k}: {v}' for k, v in interests_request.errors.items()),
        )

    ctx['nclients'] = len(interests_request.validated_data['client_ids'])

    interests = get_interests(interests_request.validated_data['client_ids'])

    return HTTPResponse(interests)


def method_handler(
    request: dict[str, 'Any'], ctx: dict[str, 'Any'], _store: dict[str, 'Any'] | None = None
) -> 'HTTPResponse | HTTPErrorResponse':
    """Обрабатывает запросы методов, направляя их в соответствующие обработчики.

    Args:
        request: Данные входящего запроса.
        ctx: Контекст запроса.
        _store: Хранилище данных (в настоящее время не используется).

    Returns:
        HTTPResponse или HTTPErrorResponse.
    """
    req = MethodRequest(request['body'])

    if not req.is_valid():
        return HTTPErrorResponse(
            HTTPStatus.INVALID_REQUEST,
            ', '.join(f'{k}: {v}' for k, v in req.errors.items()),
        )

    if not check_auth(req):
        return HTTPErrorResponse(HTTPStatus.FORBIDDEN)

    method = req.validated_data['method']
    arguments = req.validated_data['arguments']

    match method:
        case 'online_score':
            return handle_online_score(req, arguments, ctx)
        case 'clients_interests':
            return handle_clients_interests(arguments, ctx)
        case _:
            return HTTPErrorResponse(HTTPStatus.NOT_FOUND)
