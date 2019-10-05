from falibrary.config import default_config
from falibrary import Falibrary

def test_config():

    #Temporary Unit test. Will spruce this up later.
    # {k: val for k, val in self.__dict__.items() if not str(hex(id(val))) in str(val)}

    test = Falibrary(
        title='Machine Translation',
        version='1.2.0',
        UI = 'swagger',
        OPENAPI_VERSION = '2.0.1'
    )

    assert test.config.UI == 'swagger' , 'UI mismatch'
    assert test.config.TITLE == 'Machine Translation' , 'Title mismatch'
    assert test.config.VERSION == '1.2.0' , 'Version mismatch'
    assert test.config.FILENAME == default_config.FILENAME , 'Filename mismatch'
    assert test.config.OPENAPI_VERSION == '2.0.1' , 'API version mismatch'