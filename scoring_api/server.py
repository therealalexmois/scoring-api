#!/usr/bin/env python

"""Скоринговый API-сервер

Этот модуль предоставляет функциональность для запуска и работы HTTP-сервера для скорингового API.
Он обрабатывает аргументы командной строки, настраивает ведение журнала и запускает службу API.

Использование:
    Запустите сервер с настройками по умолчанию:
        $ python -m scoring_api.server

    Укажите порт и файл журнала:
        $ python -m scoring_api.server --port 8081 --log server.log
"""

import logging
from http.server import HTTPServer

from scoring_api.api import APIHandler
from scoring_api.cli import parse_arguments, ServerConfig
from scoring_api.logger import configure_logger


def run_server(config: ServerConfig) -> None:
    """Запускает сервер API скоринга.

    Args:
        config: Конфигурация, содержащая порт и файл журнала.
    """
    configure_logger(config.log_file)

    server = HTTPServer(('localhost', config.port), APIHandler)
    logging.info(f'Starting server at port {config.port}')

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info('Shutting down server...')
    finally:
        server.server_close()
        logging.info('Server stopped.')


if __name__ == '__main__':
    config = parse_arguments()

    run_server(config)
