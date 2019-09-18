from functools import wraps
from pydantic import ValidationError, BaseModel
import falcon

from falibrary.config import default_config


class Falibrary:
    """
    :param app: Falcon instance
    :param \*\*kwargs: key-value for config
    """
    def __init__(self, app, **kwargs):
        self.app = app
        self.models = {}
        self.config = default_config
        for key, value in kwargs.items():
            setattr(self.config, key, value)

    def validate(self, query=None, data=None, resp=None, x=[]):
        """
        validate query, JSON data, and response according to
        ``pydantic.BaseModel``

        :param resp:
        :param data:
        :param resp:
        :param x: List of :class:`falcon.HTTPStatus`
        """
        def decorator_validation(func):
            @wraps(func)
            def validation(*args, **kwargs):
                pass

            # register ``pydantic.BaseModel``
            pass

            # handle exceptions
            pass

            return validation
        return decorator_validation
