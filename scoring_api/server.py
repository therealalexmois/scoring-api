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
from argparse import ArgumentParser
from collections import namedtuple
from http.server import HTTPServer

from scoring_api.api import APIHandler
from scoring_api.logger import configure_logger

ServerConfig = namedtuple('ServerConfig', ['port', 'log_file'])


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


def parse_arguments() -> ServerConfig:
    """Разбор аргументов командной строки.

    Returns:
        Разобранный порт и файл журнала.
    """
    parser = ArgumentParser(description='Scoring API Server')
    parser.add_argument('-p', '--port', type=int, default=8080, help='Port to run the server on (default: 8080)')
    parser.add_argument('-l', '--log', type=str, default=None, help='Path to the log file (default: stdout)')

    args = parser.parse_args()

    return ServerConfig(args.port, args.log)


if __name__ == '__main__':
    config = parse_arguments()

    run_server(config)
