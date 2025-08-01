from typing import TypedDict

class AuthLogin(TypedDict):
    email: str
    password: str

class AuthSignup(TypedDict):
    username: str
    email: str
    password: str
    
class AuthJWTPayload(TypedDict):
    id: str
    iat: int

class AuthSessionInfo(TypedDict):
    id: str
    username: str

class HashableAuthSessionInfo():
    id: str
    sid: str
    username: str
    full: AuthSessionInfo
    
    def __init__(self, user: AuthSessionInfo):
        self.id = user['id']
        self.username = user['username']
        self.full = user

    def __eq__(self, value):
        if not isinstance(value, HashableAuthSessionInfo):
            return False
        return self.id == value.id
    
    def  __hash__(self):
        return hash(self.id)