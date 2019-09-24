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

    def validate(self, query=None, data=None, resp=None, x=[]):
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
            def validation(self, _req, _resp, *args, **kwargs):
                try:
                    if query:
                        setattr(_req.context, 'query', query(**_req.params))
                    if data:
                        setattr(_req.context, 'data', data(**_req.media))
                except ValidationError as err:
                    raise falcon.HTTPUnprocessableEntity(
                        'Schema failed validation',
                        description=str(err),
                    )
                except Exception:
                    raise

                response = func(self, _req, _resp, *args, **kwargs)
                if resp:
                    _resp.media = response.dict()

                return response

            # register ``pydantic.BaseModel``
            for name, model in zip(
                ('query', 'data', 'resp'), (query, data, resp)
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
