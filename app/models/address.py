# models/address.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.employee import Base


# Address model definition
class Address(Base):
    __tablename__ = 'addresses_fastapi'
    __table_args__ = {'schema': 'dbo'}  # Optional schema if needed

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    emp_code = Column(String(50), ForeignKey('dbo.employees_fastapi.emp_code'), nullable=False)
    add1 = Column(String(50), nullable=False)
    add2 = Column(String(50), nullable=False)
    phone_no = Column(String(10), nullable=False)
    zip_code = Column(String(10), nullable=False)
    country = Column(String(20), nullable=False)

    # Relationship to Employee
    employee = relationship("Employee", back_populates="addresses")

    def __repr__(self):
        return f"<Address(id={self.id}, emp_code={self.emp_code}, add1={self.add1}, add2={self.add2}, phone_no={self.phone_no}, zip_code={self.zip_code}, country={self.country})>"
