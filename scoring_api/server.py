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

ServerConfig = namedtuple('ServerConfig', ['port', 'log_file'])


def run_server(port: int, log_file: str | None) -> None:
    """Запускает сервер API скоринга.

    Args:
        port: Номер порта, на котором будет работать сервер.
        log_file: Путь к файлу журнала (или None, чтобы вести журнал в stdout).
    """
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y.%m.%d %H:%M:%S',
    )

    server = HTTPServer(('localhost', port), APIHandler)
    logging.info(f'Starting server at port {port}')

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info('Shutting down server...')
    finally:
        server.server_close()
        logging.info('Server stopped.')


def parse_arguments() -> tuple[int, str | None]:
    """Разбор аргументов командной строки.

    Returns:
        Разобранный порт и файл журнала.
    """
    parser = ArgumentParser(description='Scoring API Server')

    parser.add_argument(
        '-p', '--port', type=int, action='store', default=8080, help='Port to run the server on (default: 8080)'
    )
    parser.add_argument(
        '-l', '--log', type=str, action='store', default=None, help='Path to the log file (default: stdout)'
    )

    args = parser.parse_args()

    return args.port, args.log


if __name__ == '__main__':
    port, log_file = parse_arguments()

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y.%m.%d %H:%M:%S',
    )

    run_server(port, log_file)
