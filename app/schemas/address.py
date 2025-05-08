from pydantic import BaseModel

class AddressCreate(BaseModel):
    add1: str
    add2: str
    phone_no: str
    zip_code: str
    country: str

    class Config:
        orm_mode = True
        from_attributes = True  # ✅ Required for Pydantic v2
