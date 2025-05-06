from typing import List

from pydantic import BaseModel

from app.schemas.address import AddressCreate


class EmployeeUpdate(BaseModel):
    first_name: str
    last_name: str
    email: str
    addresses: List[AddressCreate]
