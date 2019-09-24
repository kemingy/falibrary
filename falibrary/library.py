import re
from functools import wraps
from pydantic import ValidationError, BaseModel
import falcon

from falibrary.config import default_config
from falibrary.route import OpenAPI, RedocPage


class Falibrary:
    """
    :param app: Falcon instance
    :param kwargs: key-value for config
    """

    def __init__(self, app, **kwargs):
        self.app = app
        self.models = {}
        self.config = default_config
        for key, value in kwargs.items():
            setattr(self.config, key.upper(), value)

        self.STATUS = re.compile(r'(?P<code>^\d{3}) (?P<msg>[\w ]+$)')
        self._register_route()

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
                match = self.STATUS.match(exception)
                assert match
                code_msg[match.group('code')] = match.group('msg')

            return validation
        return decorator_validation

    def _register_route(self):
        """
        register doc page and OpenAPI spec file
        """
        self.app.add_route(
            f'/{self.config.PATH}',
            RedocPage(self.config)
        )
        self.app.add_route(
            f'/{self.config.PATH}/{self.config.FILENAME}',
            OpenAPI(self)
        )

    @property
    def spec(self):
        if not hasattr(self, '_spec'):
            self._generate_spec()
        return self._spec

    def _generate_spec(self):
        self._spec = None
