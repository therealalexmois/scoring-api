from argparse import ArgumentParser
from collections import namedtuple

ServerConfig = namedtuple('ServerConfig', ['port', 'log_file'])


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
