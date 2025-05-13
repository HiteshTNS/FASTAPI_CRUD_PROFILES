from pydantic import BaseModel, EmailStr, Field, validator, field_validator
from typing import List
from app.schemas.address import AddressCreate

class EmployeeCreate(BaseModel):
    # id: int
    emp_code: str = Field(..., min_length=1, max_length=20)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr = Field(..., min_length=5, max_length=100)
    password:str =  Field(..., min_length=5, max_length=100)
    addresses: List[AddressCreate]

    @field_validator("emp_code", "first_name", "last_name", "email", mode="before")
    def check_not_empty(cls, value, info):
        if isinstance(value, str) and not value.strip():
            field_name = info.field_name.replace("_", " ").title()
            raise ValueError(f"{field_name} cannot be empty")
        return value

    class Config:
        orm_mode = True
        from_attributes = True  # ✅ Required for Pydantic v2