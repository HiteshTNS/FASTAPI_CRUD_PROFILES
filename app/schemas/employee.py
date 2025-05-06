from pydantic import BaseModel, EmailStr
from typing import List
from app.schemas.address import AddressCreate

class EmployeeCreate(BaseModel):
    # id: int
    emp_code: str
    first_name: str
    last_name: str
    email: str
    addresses: List[AddressCreate] = []

    class Config:
        orm_mode = True
