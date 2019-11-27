import falcon
from wsgiref import simple_server
from pydantic import BaseModel

from falibrary import Falibrary


class Query(BaseModel):
    text: str


api = Falibrary(mode='greedy')
another = Falibrary(ui='swagger', mode='strict')


class Ping:
    def on_get(self, req, resp):
        resp.media = {'msg': 'pong'}


class Classify:
    @api.validate()
    def on_post(self, req, resp):
        resp.media = {'label': 0}


class Recommend:
    @another.validate(x=[falcon.HTTP_201])
    def on_post(self, req, resp):
        resp.media = {'result': []}
        resp.status = falcon.HTTP_201


if __name__ == "__main__":
    app = falcon.API()
    app.add_route('/ping', Ping())
    app.add_route('/api/classify', Classify())
    app.add_route('/api/recommend', Recommend())

    api.register(app)
    # another.register(app)
    httpd = simple_server.make_server('localhost', 8000, app)
    httpd.serve_forever()
