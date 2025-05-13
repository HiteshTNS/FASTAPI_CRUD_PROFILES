import asyncio

from fastapi import HTTPException, Depends
import logging

from sqlalchemy import delete
from sqlalchemy.orm import Session, joinedload, selectinload
from app.models.employee import Employee
from app.models.address import Address
from app.schemas.EmployeeUpdate import EmployeeUpdate
from app.schemas.empupdate import EmployeeResponse
from app.schemas.employee import EmployeeCreate
from app.schemas.address import AddressCreate
from concurrent.futures import ThreadPoolExecutor
from typing import List
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.utils.jwt import create_access_token
from app.utils.security import verify_password

# from app.services.auth_service import get_current_user

from app.utils.security import hash_password

# Set up logging using Python's standard logging module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
async def create_employee(db: AsyncSession, employee_data: EmployeeCreate):
    try:
        # Check if emp_code already exists
        existing_emp = await db.execute(select(Employee).filter(Employee.emp_code == employee_data.emp_code))
        if existing_emp.scalar(): #first row first column
            logger.warning(f"Employee with emp_code '{employee_data.emp_code}' already exists.")
            return {
                "response_code": 409,
                "response_description": f"Employee with emp_code '{employee_data.emp_code}' already exists.",
                "data": None
            }

        # Check if email already exists
        existing_email = await db.execute(select(Employee).filter(Employee.email == employee_data.email))
        if existing_email.scalar():
            logger.warning(f"Employee with email '{employee_data.email}' already exists.")
            return {
                "response_code": 409,
                "response_description": f"Employee with email '{employee_data.email}' already exists.",
                "data": None
            }

        # Create employee
        hashed_password = hash_password(employee_data.password)
        new_employee = Employee(
            emp_code=employee_data.emp_code,
            first_name=employee_data.first_name,
            last_name=employee_data.last_name,
            email=employee_data.email,
            password=hashed_password
        )
        db.add(new_employee)
        await db.flush()  # Ensure emp_code is available

        # Batch insert addresses
        addresses = [
            Address(
                emp_code=new_employee.emp_code,
                add1=addr.add1,
                add2=addr.add2,
                phone_no=addr.phone_no,
                zip_code=addr.zip_code,
                country=addr.country
            )
            for addr in employee_data.addresses
        ]
        db.add_all(addresses)

        await db.commit()

        logger.info(f"Employee '{new_employee.emp_code}' created successfully.")
        return {
            "response_code": 201,
            "response_description": "Employee created successfully",
            "data": {
                "emp_code": new_employee.emp_code,
                "first_name": new_employee.first_name,
                "last_name": new_employee.last_name,
                "email": new_employee.email
            }
        }

    except IntegrityError as e:
        await db.rollback()
        logger.error(f"IntegrityError while creating employee: {str(e)}")
        return {
            "response_code": 409,
            "response_description": f"Failed to create employee: {str(e)}",
            "data": None
        }

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"SQLAlchemyError while creating employee: {str(e)}")
        return {
            "response_code": 500,
            "response_description": f"Failed to create employee: {str(e)}",
            "data": None
        }

    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error while creating employee: {str(e)}")
        return {
            "response_code": 500,
            "response_description": f"Unexpected error: {str(e)}",
            "data": None
        }

# Async function to get employee by emp_code
async def get_employee_by_emp_code(db: AsyncSession, emp_code: str):
    try:
        # Use `selectinload` to eagerly load addresses without blocking the main thread
        stmt = select(Employee).options(selectinload(Employee.addresses)).filter(Employee.emp_code == emp_code) ##selection load is like join to loca address based on the link we defined
        result = await db.execute(stmt)
        db_emp = result.scalar_one_or_none()  ##if multiple records come will throw error. one or none
        return db_emp
    except Exception as e:
        print(f"❌ Error fetching employee: {e}")
        raise e

# Ayunc function to get all employees
async def get_all_employees(db: AsyncSession) -> List[EmployeeCreate]:  ##->List[EmployeeCreate] this is the return type of the function
    try:
        # Fetch all employees with their addresses using selectinload
        result = await db.execute(select(Employee).options(selectinload(Employee.addresses)))
        employees = result.scalars().all() ## will fetch all rows

        # Check if employees are returned
        if not employees:
            print("No employees found.")
            return []

        # Convert Employee models to EmployeeCreate Pydantic models
        return [EmployeeCreate.from_orm(emp) for emp in employees]

    except Exception as e:
        print(f"❌ Failed to fetch employees: {e}")
        return []

# Async function to update an employee's details
async def update_employee(db: AsyncSession, emp_code: str, employee_data: EmployeeUpdate):
    try:
        # Fetch the existing employee
        result = await db.execute(
            select(Employee).filter(Employee.emp_code == emp_code).options(selectinload(Employee.addresses)))
        db_emp = result.scalar_one_or_none()

        if not db_emp:
            raise HTTPException(status_code=404, detail=f"Employee with emp_code '{emp_code}' not found.")

        # Update employee details
        db_emp.first_name = employee_data.first_name
        db_emp.last_name = employee_data.last_name
        db_emp.email = employee_data.email

        # Delete existing addresses and add new ones
        await db.execute(Address.__table__.delete().where(Address.emp_code == emp_code))

        db.add_all([
            Address(
                emp_code=emp_code,
                add1=addr.add1,
                add2=addr.add2,
                phone_no=addr.phone_no,
                zip_code=addr.zip_code,
                country=addr.country
            )
            for addr in employee_data.addresses
        ])

        await db.commit()

        # Return the updated employee as a response
        updated_employee = EmployeeResponse.from_orm(db_emp)  # Convert the Employee object to EmployeeResponse
        return {
            "response_code": 200,
            "response_description": "Employee updated successfully",
            "data": updated_employee.dict()  # Convert the Pydantic model to dictionary
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        await db.rollback()
        print(f"❌ Failed to update employee: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update employee: {e}")


# Async function to delete an employee by emp_code
async def delete_employee(db: AsyncSession, emp_code: str):
    try:
        # Fetch existing employee
        result = await db.execute(select(Employee).filter(Employee.emp_code == emp_code))
        db_emp = result.scalar_one_or_none()

        if not db_emp:
            raise HTTPException(status_code=404, detail=f"Employee with emp_code '{emp_code}' not found.")

        # Delete addresses first (due to foreign key constraint)
        await db.execute(Address.__table__.delete().where(Address.emp_code == emp_code))

        # Delete employee
        await db.delete(db_emp)
        await db.commit()

        return {
            "response_code": 200,
            "response_description": "Employee deleted successfully",
            "data": {
                "emp_code": emp_code
            }
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        await db.rollback()
        print(f"❌ Failed to delete employee: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete employee: {e}")


