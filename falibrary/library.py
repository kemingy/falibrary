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
            setattr(self.config, key.upper(), value)

    def validate(self, query=None, data=None, response=None, x=[]):
        """
        validate query, JSON data, and response according to
        ``pydantic.BaseModel``

        :param query: Schema for query args
        :param data: Schema for JSON data
        :param response: Schema for JSON response
        :param x: List of :class:`falcon.status_codes`
        """
        def decorator_validation(func):
            @wraps(func)
            def validation(self, req, resp, *args, **kwargs):
                try:
                    if query:
                        setattr(req.context, 'query', query(**req.params))
                    if data:
                        setattr(req.context, 'data', data(**req.media))
                except ValidationError as err:
                    raise falcon.HTTPUnprocessableEntity(
                        'Schema failed validation',
                        description=str(err),
                    )
                except Exception:
                    raise

                result = func(self, req, resp, *args, **kwargs)
                if response:
                    resp.media = result.dict()

                return result

            # register ``pydantic.BaseModel``
            for name, model in zip(
                ('query', 'data', 'response'), (query, data, response)
            ):
                if model:
                    assert issubclass(model, BaseModel)
                    self.models[model.__name__] = model.schema()
                    setattr(validation, name, model.__name__)

            # handle exceptions
            code_msg = {}
            for exception in x:
                # assert getattr(falcon.status_codes, exception), 'Unknown HTTP Status'
                code, msg = exception.split(' ', 1)
                code_msg[code] = msg

            return validation
        return decorator_validation
