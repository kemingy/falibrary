# Falibrary

[![GitHub Actions](https://github.com/kemingy/falibrary/workflows/Python%20package/badge.svg)](https://github.com/kemingy/falibrary/actions)
![GitHub](https://img.shields.io/github/license/kemingy/falibrary)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/falibrary)

Falcon add-on for API specification and validation.

Provide OpenAPI document and validation for flask service.

Mainly built for Machine Learning Model services.

If you're using Flask, check my another Python library [Flaskerk](https://github.com/kemingy/flaskerk).

## Features

* Generate API document with [Redoc UI](https://github.com/Redocly/redoc) or [Swagger UI](https://github.com/swagger-api/swagger-ui) :yum:
* Less boilerplate code, annotations are really easy-to-use :sparkles:
* Validate query, JSON data, response data with [pydantic](https://github.com/samuelcolvin/pydantic/) :wink:
* Better HTTP exceptions for API services (default & customized) (JSON instead of HTML) :grimacing:

## Quick Start

Install with `pip install falibrary` (Python 3.6+)

### Basic example

```py
import falcon
from wsgiref import simple_server
from pydantic import BaseModel

from falibrary import Falibrary

api = Falibrary(
    title='Demo Service',
    version='0.1.2',
)

class Query(BaseModel):
    text: str

class Demo():
    @api.validate(query=Query)
    def on_post(self, req, resp):
        print(req.context.query)
        pass

if __name__ == '__main__':
    app = falcon.API()
    app.add_route('/api/demo', Demo())
    api.register(app)

    httpd = simple_server.make_server('localhost', 8000, app)
    httpd.serve_forever()
```

Changes you need to make:

* create model with [pydantic](https://github.com/samuelcolvin/pydantic/)
* decorate the route function with `Falibrary.validate()`
* specify which part you need in `validate`
  * `query` (args in url)
    * [builtin converters](https://falcon.readthedocs.io/en/stable/api/routing.html#built-in-converters) (int, uuid, dt)
  * `data` (JSON data from request)
  * `resp` (response) this will be transformed to JSON data after validation
  * `x` (HTTP Exceptions list)
  * `tags` (tags for this route)
* register to Falcon application

After that, this library will help you validate the incoming request and provide API document in `/apidoc`.

| Parameters in `Falibrary.validate` | Corresponding parameters in `falcon` |
| ------------- | ------------- |
| `query` | `req.context.query` |
| `data` | `req.context.data` |
| `resp` | \ |
| `x` | \ |
| `tags` | \ |

For more details, check the [document](https://falibrary.readthedocs.io/en/latest/).

### More features

```py
import falcon
from wsgiref import simple_server
from pydantic import BaseModel, Field
from random import random

from falibrary import Falibrary


api = Falibrary(
    title='Demo Service',
    version='0.1.2',
)


class Query(BaseModel):
    text: str = Field(
        ...,
        max_length=100,
    )


class Response(BaseModel):
    label: int = Field(
        ...,
        ge=0,
        le=9,
    )
    score: float = Field(
        ...,
        gt=0,
        lt=1,
    )


class Data(BaseModel):
    uid: str
    limit: int
    vip: bool


class Classification():
    """
    classification demo
    """
    @api.validate(tags=['demo'])
    def on_get(self, req, resp, source, target):
        """
        API summary

        description here: test information with `source` and `target`
        """
        resp.media = {'msg': f'hello from {source} to {target}'}

    @api.validate(query=Query, data=Data, resp=Response, x=[falcon.HTTP_403])
    def on_post(self, req, resp, source, target):
        """
        post demo

        demo for `query`, `data`, `resp`, `x`
        """
        print(f'{source} => {target}')
        print(req.context.query)
        print(req.context.data)
        if random() < 0.5:
            raise falcon.HTTPForbidden("Bad luck. You're fobidden.")
        return Response(label=int(10 * random()), score=random())


if __name__ == '__main__':
    app = falcon.API()
    app.add_route('/api/{source}/{target}', Classification())
    api.register(app)

    httpd = simple_server.make_server('localhost', 8000, app)
    httpd.serve_forever()
```

Try it with `http POST ':8000/api/zh/en?text=hello' uid=0b01001001 limit=5 vip=true`.

Open the docs in http://127.0.0.1:8000/apidoc .

For more examples, check [examples](/examples).
