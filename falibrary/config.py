class Config:
    """
    :ivar MODE: mode for route. **normal** includes undecorated routes and
        routes decorated by this instance. **strict** only includes routes
        decorated by this instance. **greedy** includes all the routes.
    :ivar PATH: path for API document page
    :ivar UI: UI for API document, 'redoc' or 'swagger'
    :ivar OPENAPI_VERSION: OpenAPI version
    :ivar TITLE: service name
    :ivar VERSION: service version
    :ivar DOMAIN: service host domain
    """

    def __init__(self):
        self.PATH = 'apidoc'
        self.TEMPLATE_FOLDER = 'templates'
        self.FILENAME = 'openapi.json'
        self.OPENAPI_VERSION = '3.0.2'
        self.UI = 'redoc'
        self._SUPPORT_UI = {'redoc', 'swagger'}
        self.MODE = 'normal'
        self._SUPPORT_MODE = {'normal', 'strict', 'greedy'}

        self.TITLE = 'Service API Document'
        self.VERSION = '0.1'
        self.DOMAIN = None
