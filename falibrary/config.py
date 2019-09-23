class Config:
    def __init__(self):
        self.PATH = 'apidoc'  #: path for API document page
        self.TEMPLATE_FOLDER = 'templates'
        self.FILENAME = 'openapi.json'
        self.OPENAPI_VERSION = '3.0.2'  #: OpenAPI version

        self.TITLE = 'Service API Document'  #: service name
        self.VERSION = '0.1'  #: service version
        self.DOMAIN = None  #: service host domain


default_config = Config()
