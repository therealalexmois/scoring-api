import pytest

from scoring_api.cli import parse_arguments, ServerConfig


@pytest.mark.parametrize(
    'args, expected',
    [
        ([], ServerConfig(8080, None)),
        (['--port', '9090'], ServerConfig(9090, None)),
        (['--log', 'server.log'], ServerConfig(8080, 'server.log')),
        (['--port', '9090', '--log', 'app.log'], ServerConfig(9090, 'app.log')),
    ],
    ids=[
        'test_parse_arguments__default_values',
        'test_parse_arguments__custom_port',
        'test_parse_arguments__custom_log_file',
        'test_parse_arguments__custom_all',
    ],
)
def test_parse_arguments__ok(monkeypatch: pytest.MonkeyPatch, args: list[str], expected: ServerConfig) -> None:
    """Тестирует разбор аргументов командной строки с корректными значениями.

    Args:
        monkeypatch: Фикстура для замены `sys.argv`.
        args: Список аргументов командной строки.
        expected: Ожидаемый результат.
    """
    monkeypatch.setattr('sys.argv', ['scoring_api'] + args)
    assert parse_arguments() == expected
