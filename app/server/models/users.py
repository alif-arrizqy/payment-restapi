from uuid import uuid4
from typing import Optional
from pydantic import BaseModel, Field
from datetime import date, datetime


class UsersSchema(BaseModel):
    user_id: str = Field(default_factory=uuid4)
    first_name: str = Field(...)
    last_name: str = Field(...)
    phone_number: str = Field(...)
    address: Optional[str]
    pin: int = Field(...)
    created_date: date = Field(default_factory=datetime.now)

    class Config:
        schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "phone_number": "",
                "address": "No. 1, Ojodu Road, Ojodu, Lagos",
                "pin": 12345,
            }
        }


class UserLoginSchema(BaseModel):
    phone_number: str = Field(...)
    pin: int = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "phone_number": "089123456",
                "pin": 12345
            }
        }

def ResponseModel(data):
    return {
        "status": "SUCCESS",
        "result": data,
    }


def ErrorResponseModel(message):
    return {"message": message}