from pydantic import BaseModel

class UserCreds(BaseModel):
    username: str
    password: str

class UserSchema(BaseModel):
    id: int
    username: str
