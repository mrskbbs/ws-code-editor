from flask import Request


class UserModel():
    def __init__(self, request: Request):
        if request.sid == None:
            raise ValueError("SID is NULL")
        
        if request.cookies.get("auth") == None:
            raise ValueError("User token is NULL")
        
        self.sid = request.sid
        self.user_token = request.cookies.get("auth")

    def __str__(self):
        return self.user_token+"@"+self.sid
    
    def __repr__(self):
        return f"TOKEN[{self.user_token}]@SID[{self.sid}]"

    def __eq__(self, other):
        if not isinstance(other, UserModel):
            return False
        
        return self.user_token == other.user_token and self.sid == other.sid

    def __hash__(self):
        return hash(self.user_token + self.sid)