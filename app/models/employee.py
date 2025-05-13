# models/employee.py
from oci_cli.cli_session import export
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
# Define base for models
# from app.database import Base

Base = declarative_base()

# Employee model definition
class Employee(Base):
    __tablename__ = 'employees_fastapi'
    __table_args__ = {'schema': 'dbo'}  # Optional schema if needed

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    emp_code = Column(String(50), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255))
    # Relationship with Address model
    addresses = relationship("Address", back_populates="employee")
    def __repr__(self):
        return f"<Employee(id={self.id}, emp_code={self.emp_code}, first_name={self.first_name}, last_name={self.last_name}, email={self.email})>"
