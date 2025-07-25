class HTTPBaseException(Exception):
    message: str
    status_code: int
    def __init__(self, *args):
        super().__init__(*args)