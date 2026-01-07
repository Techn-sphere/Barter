import uuid
from typing import Annotated

from pydantic import BaseModel, EmailStr, StringConstraints, PastDate


class GetUserByID(BaseModel):
    id: uuid.UUID | str


class GetUserByEmail(BaseModel):
    email: EmailStr


class RegisterUser(GetUserByEmail):
    username: Annotated[str, StringConstraints(max_length=128)]
    name: Annotated[str, StringConstraints(max_length=128)]
    surname: Annotated[str, StringConstraints(max_length=128)]
    father_name: Annotated[str, StringConstraints(max_length=128)]
    birthday: PastDate
    password: Annotated[str, StringConstraints(min_length=8, max_length=128)]


class LoginUser(GetUserByEmail):
    password: Annotated[str, StringConstraints(min_length=8, max_length=128)]


class CreateUser(GetUserByEmail):
    username: Annotated[str, StringConstraints(max_length=128)]
    name: Annotated[str, StringConstraints(max_length=128)]
    surname: Annotated[str, StringConstraints(max_length=128)]
    father_name: Annotated[str, StringConstraints(max_length=128)]
    birthday: PastDate
    hashed_password: str
