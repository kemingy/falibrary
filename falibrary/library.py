import re
from functools import wraps, partial
from pydantic import ValidationError, BaseModel
import falcon

from falibrary.config import Config
from falibrary.route import OpenAPI, RedocPage
from falibrary.utils import find_routes, parse_path


class Falibrary:
    """
    :param app: Falcon instance [optional](you can register it later)
    :param kwargs: key-value for config, see :class:`falibrary.config.Config`
    """

    def __init__(self, app=None, **kwargs):
        self.app = app
        self.models = {}
        self.config = Config()
        for key, value in kwargs.items():
            setattr(self.config, key.upper(), value)

        self.STATUS = re.compile(r'(?P<code>^\d{3}) (?P<msg>[\w ]+$)')
        if self.app:
            assert isinstance(app, falcon.API)
            self._register_route()

    def register(self, app):
        """
        :param app: Falcon instance

        register this library to Falcon application to get routes
        """
        assert isinstance(app, falcon.API)
        self.app = app
        self._register_route()

    def update_config(self, **kwargs):
        """
        update config

        this can be done before generate the APIspecs
        """
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

        .. code-block:: python

            from falibrary imoprt Falibrary
            from wsgiref import simple_server
            from pydantic import BaseModel, Schema

            class Query(BaseModel):
                text: str
                limit: int

            api = Falibrary(title='demo', version='0.1')

            class Demo:
                @api.vaildate(query=Query, x=[falcon.HTTP_422])
                def on_post(self, req, resp):
                    print(req.content.query)
                    raise falcon.HTTPUnprocessableEntity()

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

            if code_msg:
                validation.x = code_msg

            # register decorator
            validation._decorator = self

            return validation
        return decorator_validation

    def _register_route(self):
        """
        register doc page and OpenAPI spec file
        """
        self.config.SPEC_URL = f'/{self.config.PATH}/{self.config.FILENAME}'
        self.app.add_route(
            f'/{self.config.PATH}',
            RedocPage(self.config)
        )
        self.app.add_route(
            self.config.SPEC_URL,
            OpenAPI(self)
        )

    @property
    def spec(self):
        """
        get the spec of API document
        """
        if not hasattr(self, '_spec'):
            self._generate_spec()
        return self._spec

    def bypass(self, func):
        if self.config.MODE == 'greedy':
            return False
        elif self.config.MODE == 'strict':
            if getattr(func, '_decorator', None) == self:
                return False
            return True
        else:
            decorator = getattr(func, '_decorator', None)
            if decorator and decorator != self:
                return True
            return False

    def _generate_spec(self):
        routes = {}
        assert self.config.MODE in self.config._SUPPORT_MODE
        for route in find_routes(self.app._router._roots):
            path, parameters = parse_path(route.uri_template)
            routes[path] = {}
            for method, func in route.method_map.items():
                if isinstance(func, partial):
                    # ignore exception handlers
                    continue

                if self.bypass(func):
                    continue

                name = route.resource.__class__.__name__
                spec = {
                    'summary': f'{name} <{method}>',
                    'operationID': f'{name}__{method.lower()}',
                }

                if hasattr(func, 'data'):
                    spec['requestBody'] = {
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': f'#/components/schemas/{func.data}'
                                }
                            }
                        }
                    }

                if hasattr(func, 'query'):
                    parameters.append({
                        'name': func.query,
                        'in': 'query',
                        'required': True,
                        'schema': {
                            '$ref': f'#/components/schemas/{func.query}',
                        }
                    })
                spec['parameters'] = parameters

                if hasattr(func, 'resp'):
                    spec['responses'] = {
                        '200': {
                            'description': 'Successful Response',
                            'content': {
                                'application/json': {
                                    'schema': {
                                        '$ref': f'#/components/schemas/{func.resp}'
                                    }
                                }
                            }
                        }
                    }
                else:
                    spec['responses'] = {
                        '200': {
                            'description': 'Successful Response',
                        }
                    }

                if any([hasattr(func, schema)
                        for schema in ('query', 'data', 'resp')]):
                    spec['responses']['422'] = {
                        'description': 'Validation Error',
                    }

                if hasattr(func, 'x'):
                    for code, msg in func.x.items():
                        spec['responses'][str(code)] = {
                            'description': msg,
                        }

                routes[path][method.lower()] = spec

        definitions = {}
        for _, schema in self.models.items():
            if 'definitions' in schema:
                for key, value in schema['definitions'].items():
                    definitions[key] = value
                del schema['definitions']

        data = {
            'openapi': self.config.OPENAPI_VERSION,
            'info': {
                'title': self.config.TITLE,
                'version': self.config.VERSION,
            },
            'paths': {
                **routes
            },
            'components': {
                'schemas': {
                    name: schema for name, schema in self.models.items()
                },
            },
            'definitions': definitions
        }
        self._spec = data
