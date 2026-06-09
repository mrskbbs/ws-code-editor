from pydantic import BaseModel

class UserCreds(BaseModel):
    username: str
    password: str
