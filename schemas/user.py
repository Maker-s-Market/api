from pydantic import BaseModel, Field


class CreateUser(BaseModel):
    name: str
    username: str
    email: str
    password: str
    city: str
    region: str
    photo: str
    # role: str


class UserLogin(BaseModel):
    username: str
    password: str
