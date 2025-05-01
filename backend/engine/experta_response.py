class ExpertaResponse:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ExpertaResponse, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.engine_response = ''

    def get_engine_response(self):
        return self.engine_response

    def set_engine_response(self, engine_response):
        self.engine_response = engine_response
        # print('changed',self.engine_response)