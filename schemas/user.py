from pydantic import BaseModel, Field


class CreateUser(BaseModel):
    name: str
    username: str
    email: str
    password: str
    city: str
    region: str
    photo: str
    role: str = "Client"

class UserUpdate(BaseModel):
    id: str
    name: str
    city: str
    region: str
    photo: str

class UserLogin(BaseModel):
    identifier: str
    password: str


class ActivateUser(BaseModel):
    username: str
    code: str


class UserIdentifier(BaseModel):
    identifier: str


class ChangePassword(BaseModel):
    identifier: str
    password: str
    code: str
