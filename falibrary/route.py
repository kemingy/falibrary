"""
route for API document page and OpenAPI spec
"""
import os
import re


class RedocPage:
    def __init__(self, config):
        self.config = config

    def on_get(self, req, resp):
        resp.content_type = 'text/html'
        with open(os.path.join(os.getcwd(),
                               'falibrary',
                               self.config.TEMPLATE_FOLDER,
                               'redoc.html'), 'r', encoding='utf-8') as f:
            page = f.read()

        resp.body = re.sub('{{}}', self.config.SPEC_URL, page)


class OpenAPI:
    def __init__(self, api):
        self.api = api

    def on_get(self, req, resp):
        resp.media = self.api.spec


_doc_class_name = [x.__name__ for x in (RedocPage, OpenAPI)]
