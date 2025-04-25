from pydantic import BaseModel, Field, AliasChoices
from typing import Optional, Literal
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, _):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
         field_schema.update(type="string")


class TaskBaseSchema(BaseModel):
    """Base schema with common fields"""
    title: str = Field(..., min_length=3, example="Comprar leche")
    description: Optional[str] = Field(None, example="2 litros")
    # Renamed to 'status' to match Swagger and frontend, using Literal
    status: Literal["pending", "in_progress", "completed"] = Field("pending", example="pending")

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class TaskCreateSchema(TaskBaseSchema):
    """Schema for creating a task (inherits from Base)"""
    pass


class TaskUpdateSchema(BaseModel):
    """Schema for updating a task (optional fields)"""
    title: Optional[str] = Field(None, min_length=3, example="Comprar pan integral")
    description: Optional[str] = Field(None, example="En la panadería de la esquina")
    status: Optional[Literal["pending", "in_progress", "completed"]] = Field(None, example="in_progress")

    class Config:
        extra = 'ignore'
        json_encoders = {ObjectId: str}


class TaskResponseSchema(TaskBaseSchema):
    """Schema for task response (includes ID)"""
    id: str = Field(..., validation_alias=AliasChoices('_id', 'id'), serialization_alias='id', example="60d5ecf3a3b4b5b6c7d8e9f0")