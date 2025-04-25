from pydantic import BaseModel, EmailStr, Field

class UserRegisterSchema(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., min_length=6, example="SecurePass123")

class UserLoginSchema(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., example="SecurePass123")
    
class AuthResponseSchema(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")