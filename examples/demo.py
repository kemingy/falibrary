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
