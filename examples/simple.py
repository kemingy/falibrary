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
