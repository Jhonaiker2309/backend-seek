from pydantic import BaseModel, Field, AliasChoices
from typing import Optional, Literal
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

class TaskBaseSchema(BaseModel):
    """Base schema with common task fields."""
    title: str = Field(..., min_length=3, example="Comprar leche")
    description: Optional[str] = Field(None, example="2 litros, desnatada")
    status: Literal["pending", "in_progress", "completed"] = Field(default="pending", example="pending")

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class TaskCreateSchema(TaskBaseSchema):
    """Schema for creating a new task (inherits from Base)."""
    pass


class TaskUpdateSchema(BaseModel):
    """Schema for updating an existing task (all fields optional)."""
    title: Optional[str] = Field(None, min_length=3, example="Comprar pan integral")
    description: Optional[str] = Field(None, example="En la panadería de la esquina")
    status: Optional[Literal["pending", "in_progress", "completed"]] = Field(None, example="in_progress")

    class Config:
        extra = 'ignore'
        json_encoders = {ObjectId: str}


class TaskResponseSchema(TaskBaseSchema):
    """Schema for the response when returning a single task."""
    id: PyObjectId = Field(..., validation_alias=AliasChoices('_id', 'id'), serialization_alias='id')

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class ErrorDetailSchema(BaseModel):
    detail: str = Field(..., example="Task not found")
