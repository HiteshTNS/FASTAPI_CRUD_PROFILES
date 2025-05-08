from pydantic import BaseModel, EmailStr
from typing import List
from app.schemas.address import AddressCreate
class EmployeeResponse(BaseModel):
    emp_code: str
    first_name: str
    last_name: str
    email: EmailStr
    addresses: List[AddressCreate]

    class Config:
        orm_mode = True
        from_attributes = True
