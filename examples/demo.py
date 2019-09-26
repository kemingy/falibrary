import falcon
from wsgiref import simple_server
from pydantic import BaseModel, Schema
from random import random

from falibrary import Falibrary


api = Falibrary(
    title='Demo Service',
    version='0.1.2',
)


class Query(BaseModel):
    text: str


class Response(BaseModel):
    label: int
    score: float = Schema(
        ...,
        gt=0,
        lt=1,
    )


class Data(BaseModel):
    uid: str
    limit: int
    vip: bool


class Classification():
    @api.validate(query=Query, data=Data, resp=Response, x=[falcon.HTTP_403])
    def on_post(self, req, resp, source, target):
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
