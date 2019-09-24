"""
route for API document page and OpenAPI spec
"""
import os


class RedocPage:
    def __init__(self, config):
        self.config = config

    def on_get(self, req, resp):
        resp.content_type = 'text/html; charset=utf-8'
        with open(os.path.join(os.getcwd(),
                               'falibrary',
                               self.config.TEMPLATE_FOLDER,
                               'redoc.html'), 'r', encoding='utf-8') as f:
            resp.body = f.read()


class OpenAPI:
    def __init__(self, api):
        self.api = api

    def on_get(self, req, resp):
        resp.media = self.api.spec
