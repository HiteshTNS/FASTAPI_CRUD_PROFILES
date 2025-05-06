import asyncio

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from app.models.employee import Employee
from app.models.address import Address
from app.schemas.EmployeeUpdate import EmployeeUpdate
from app.schemas.employee import EmployeeCreate
from app.schemas.address import AddressCreate
from concurrent.futures import ThreadPoolExecutor
from typing import List


# A function to handle creating an employee asynchronously.
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.employee import Employee
from app.models.address import Address
from app.schemas.employee import EmployeeCreate


def create_employee(db: Session, employee_data: EmployeeCreate):
    try:
        # Create employee
        employee = Employee(
            emp_code=employee_data.emp_code,
            first_name=employee_data.first_name,
            last_name=employee_data.last_name,
            email=employee_data.email
        )
        db.add(employee)
        db.flush()  # Ensure emp_code is available

        # Add addresses
        for addr in employee_data.addresses:
            address = Address(
                emp_code=employee.emp_code,
                add1=addr.add1,
                add2=addr.add2,
                phone_no=addr.phone_no,
                zip_code=addr.zip_code,
                country=addr.country
            )
            db.add(address)

        db.commit()

        return {
            "response_code": 201,
            "response_description": "Employee created successfully",
            "data": {"emp_code": employee.emp_code}
        }

    except Exception as e:
        db.rollback()
        return {
            "response_code": 500,
            "response_description": f"Failed to create employee: {str(e)}",
            "data": None
        }


# Helper function to create address (to be used in multithreading)
def create_address(db: Session, addr: AddressCreate, emp_code: str):
    db_addr = Address(
        add1=addr.add1,
        add2=addr.add2,
        phone_no=addr.phone_no,
        zip_code=addr.zip_code,
        country=addr.country,
        emp_code=emp_code
    )
    db.add(db_addr)

# Async function to get employee by emp_code
async def async_get_employee_by_emp_code(db: Session, emp_code: str):
    db_emp = db.query(Employee).options(joinedload(Employee.addresses)).filter(Employee.emp_code == emp_code).first()
    return db_emp

# Async function to update an employee's details
async def async_update_employee(db: Session, emp_code: str, employee: EmployeeUpdate):
    db_emp = db.query(Employee).filter(Employee.emp_code == emp_code).first()
    if not db_emp:
        raise Exception("Employee not found")

    # Update employee fields
    db_emp.first_name = employee.first_name
    db_emp.last_name = employee.last_name
    db_emp.email = employee.email

    # Delete old addresses
    db.query(Address).filter(Address.emp_code == emp_code).delete()

    # Insert new addresses
    for addr in employee.addresses:
        new_address = Address(
            emp_code=emp_code,
            add1=addr.add1,
            add2=addr.add2,
            phone_no=addr.phone_no,
            zip_code=addr.zip_code,
            country=addr.country
        )
        db.add(new_address)

    db.commit()

    return {"message": "Employee and address updated successfully"}


# Async function to delete an employee by emp_code
async def async_delete_employee(db: Session, emp_code: str):
    db_emp = db.query(Employee).filter(Employee.emp_code == emp_code).first()
    if db_emp:
        db.delete(db_emp)
        db.commit()
        return {"message": "Employee deleted successfully"}
    else:
        raise Exception("Employee not found")

# Async function to get all employees
def async_get_all_employees(db: Session):
    print("Inside get employee")
    employees = db.query(Employee).all()
    return employees
