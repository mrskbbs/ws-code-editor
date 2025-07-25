from app.exceptions.base import HTTPBaseException


class InvalidToken(HTTPBaseException):
    def __init__(self, *args):
        super().__init__(*args)
        self.message = "Token is non existent or invalid"
        self.status_code = 403

class InvalidCredentials(HTTPBaseException):
    def __init__(self, *args):
        super().__init__(*args)
        self.message = "Credentials are invalid"
        self.status_code = 400

class LogoutRequired(HTTPBaseException):
    def __init__(self, *args):
        super().__init__(*args)
        self.message = "You need to log out first"
        self.status_code = 400

class InvalidSyntaxCreds(HTTPBaseException):
    def __init__(self, *args):
        super().__init__(*args)
        self.message = "Credentials that were provided have incorrect syntax"
        self.status_code = 400