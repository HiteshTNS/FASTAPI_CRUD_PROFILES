from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload
from app.database import async_session,get_db
from app.models.employee import Employee
from app.schemas.EmployeeUpdate import EmployeeUpdate
from app.schemas.employee import EmployeeCreate
from app.services.employee_service import (
    get_all_employees,
    update_employee,
    delete_employee,
    create_employee,
    get_employee_by_emp_code
)

router = APIRouter()
print("employee router file loaded")

# Dependency to get DB session
# def get_db():
#     print("📦 Opening DB session...")
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#         print("🧹 DB session closed.")

@router.post("/employee")
async def create(emp: EmployeeCreate, db: AsyncSession = Depends(get_db)):  #dependency injection
    try:
        result = await create_employee(db, emp)  # ✅ Add await here
        if result["response_code"] != 201:
            raise HTTPException(status_code=result["response_code"], detail=result["response_description"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create employee: {str(e)}")

# Get employee by emp_code
@router.get("/employee/{emp_code}", response_model=EmployeeCreate)
async def get_employee(emp_code: str, db: AsyncSession = Depends(get_db)):
    employee = await get_employee_by_emp_code(db, emp_code)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


# Get all employees
@router.get("/employees", response_model=List[EmployeeCreate])
async def get_employees(db: AsyncSession = Depends(get_db)):
    try:
        return await get_all_employees(db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

# Update employee by emp_code
@router.put("/employees/{emp_code}", response_model=dict)
async def update_employee_endpoint(emp_code: str, employee_data: EmployeeUpdate, db: AsyncSession = Depends(get_db)):
    try:
        # Call the service function to update the employee
        response = await update_employee(db, emp_code, employee_data)
        return response

    except HTTPException as e:
        raise e  # Rethrow HTTPException without modification

    except Exception as e:
        print(f" Unexpected error while updating employee: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

# Delete employee by emp_code
@router.delete("/employee/{emp_code}")
async def delete_employee_route(emp_code: str, db: AsyncSession = Depends(get_db)):
    try:
        return await delete_employee(db, emp_code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
@router.get("/settings")
async def get_settings():
    from app.config.settings import settings
    return settings.dict()
