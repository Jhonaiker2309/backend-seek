from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, _):
        if v is None:
            return v
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId format")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        json_schema = handler(core_schema)
        json_schema.update(type="string", format="objectid", example="60d5ecf3a3b4b5b6c7d8e9f0")
        return json_schema

    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler):
        from pydantic_core import core_schema
        return core_schema.json_or_python_schema(
            python_schema=core_schema.with_info_plain_validator_function(cls.validate),
            json_schema=core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda v: str(v) if v is not None else None)
        )

class UserRegisterSchema(BaseModel):
    """Schema for user registration request body."""
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., min_length=6, example="SecurePass123")

class UserLoginSchema(BaseModel):
    """Schema for user login request body."""
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., example="SecurePass123")

class AuthResponseSchema(BaseModel):
    """Schema for the response after successful login or registration."""
    email: EmailStr = Field(..., example="user@example.com")
    token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class ErrorDetailSchema(BaseModel):
    detail: str = Field(..., example="Authentication failed")
