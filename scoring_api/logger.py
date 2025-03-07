"""Модуль настройки ведения журнала.

Этот модуль предоставляет функцию для настройки параметров ведения журнала для приложения.
"""

import logging


def configure_logger(log_file: str | None) -> None:
    """Настраивает параметры ведения журнала в приложении.

    Args:
        log_file: Путь к файлу журнала. Если нет, то журнал выводится в stdout.
    """
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y.%m.%d %H:%M:%S',
    )
