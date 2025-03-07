# ruff: noqa: ANN001, ANN201, ANN204, ANN401, D100, D101, D102, D103, D107, N804

import json
import logging
import uuid
from http.server import BaseHTTPRequestHandler
from typing import TYPE_CHECKING

from scoring_api.constants import (
    HTTPStatus,
)
from scoring_api.handlers import method_handler
from scoring_api.models import HTTPErrorResponse

if TYPE_CHECKING:
    from typing import Any, ClassVar

    from scoring_api.types import MethodHandlerType


class APIHandler(BaseHTTPRequestHandler):
    """Обрабатывает входящие HTTP-запросы и направляет их в соответствующий метод."""

    router: 'ClassVar[dict[str, MethodHandlerType]]' = {'method': method_handler}
    store: 'ClassVar[dict[str, Any] | None]' = None

    def _send_response(self, response: dict[str, 'Any'], status_code: int, context: dict[str, 'Any']) -> None:
        """Отправляет ответ в формате JSON обратно клиенту.

        Args:
            response: Ответные данные.
            status_code: Код состояния HTTP.
            context: Дополнительная информация о контексте запроса.
        """
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        final_response = {'response': response, 'code': status_code} if status_code == HTTPStatus.OK.value else response

        context.update(final_response)
        logging.info(context)

        self.wfile.write(json.dumps(final_response).encode('utf-8'))

    def get_request_id(self, headers) -> str:
        """Извлекает или генерирует идентификатор запроса."""
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self) -> None:  # noqa N802
        """Обрабатывает HTTP POST-запросы."""
        context = {'request_id': self.get_request_id(self.headers)}
        response, status_code = {}, HTTPStatus.OK.value

        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except (json.JSONDecodeError, ValueError):
            response, status_code = HTTPErrorResponse('Bad Request', HTTPStatus.BAD_REQUEST).as_tuple()
        else:
            path = self.path.strip('/')
            logging.info(f'{self.path} {data_string} {context["request_id"]}')

            if path in self.router:
                try:
                    method = self.router[path]
                    response, status_code = method({'body': request, 'headers': self.headers}, context, self.store)
                except Exception as error:
                    logging.exception(f'Unexpected error: {error}')
                    response, status_code = HTTPErrorResponse(
                        'Internal Server Error', HTTPStatus.INTERNAL_ERROR
                    ).as_tuple()
            else:
                response, status_code = HTTPErrorResponse('Not Found', HTTPStatus.NOT_FOUND).as_tuple()

        self._send_response(response, status_code, context)
