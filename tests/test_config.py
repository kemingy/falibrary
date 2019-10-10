from falibrary.config import Config
from falibrary import Falibrary

default_config = Config()


def test_config():
    test = Falibrary(
        title='Machine Translation',
        version='1.2.0',
        UI='swagger',
        OPENAPI_VERSION='2.0.1'
    )

    assert test.config.UI == 'swagger', 'UI mismatch'
    assert test.config.TITLE == 'Machine Translation', 'Title mismatch'
    assert test.config.VERSION == '1.2.0', 'Version mismatch'
    assert test.config.FILENAME == default_config.FILENAME, 'Filename mismatch'
    assert test.config.OPENAPI_VERSION == '2.0.1', 'API version mismatch'


def test_config_with_multiple_instance():
    x = Falibrary(ui='swagger')
    y = Falibrary(title='demo', version='2.0')

    assert y.config.UI == default_config.UI
    assert x.config.TITLE == default_config.TITLE
    assert x.config.VERSION == default_config.VERSION
    assert x.config.OPENAPI_VERSION == y.config.OPENAPI_VERSION
