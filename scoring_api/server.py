#!/usr/bin/env python

"""Скоринговый API-сервер

Этот модуль предоставляет функциональность для запуска и работы HTTP-сервера для скорингового API.
Он обрабатывает аргументы командной строки, настраивает ведение журнала и запускает службу API.

Использование:
    Запуск сервера с настройками по умолчанию:
        $ python -m scoring_api.server

    Запуск с указание порта и файл журнала:
        $ python -m scoring_api.server --port 8081 --log server.log
"""

import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import TYPE_CHECKING

from scoring_api.api import APIHandler
from scoring_api.cli import parse_arguments, ServerConfig
from scoring_api.logger import configure_logger
from scoring_api.storage.memcached import MemcacheStorage

if TYPE_CHECKING:
    from typing import Any

    from scoring_api.storage.interface import StorageInterface


def run_server(config: ServerConfig, storage: 'StorageInterface') -> None:
    """Запускает сервер API скоринга.

    Args:
        config: Конфигурация, содержащая порт и файл журнала.
        storage: Экземпляр хранилища.
    """
    configure_logger(config.log_file)

    def handler_factory(*args: 'Any', **kwargs: 'Any') -> BaseHTTPRequestHandler:
        """Фабрика обработчиков для HTTP-сервера.

        Args:
            *args: Позиционные аргументы для APIHandler.
            **kwargs: Именованные аргументы для APIHandler.

        Returns:
            Экземпляр APIHandler.
        """
        return APIHandler(*args, storage=storage, **kwargs)

    server = HTTPServer(('localhost', config.port), handler_factory)
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
    storage = MemcacheStorage()

    run_server(config, storage)
