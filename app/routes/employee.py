from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from app.database import SessionLocal
from app.models.employee import Employee
from app.schemas.EmployeeUpdate import EmployeeUpdate
from app.schemas.employee import EmployeeCreate
from app.services.employee_service import (
    create_employee,
    async_get_employee_by_emp_code,
    async_update_employee,
    async_delete_employee,
    async_get_all_employees
)

router = APIRouter()
print("✅ employee router file loaded")

# Dependency to get DB session
def get_db():
    print("📦 Opening DB session...")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        print("🧹 DB session closed.")

@router.post("/employee")
def create(emp: EmployeeCreate, db: Session = Depends(get_db)):
    result = create_employee(db, emp)
    if result["response_code"] != 201:
        raise HTTPException(status_code=result["response_code"], detail=result["response_description"])
    return result


# Get employee by emp_code
@router.get("/employee/{emp_code}",response_model=EmployeeCreate)
async def get_employee(emp_code: str, db: Session = Depends(get_db)):
    try:
        db_emp = await async_get_employee_by_emp_code(db, emp_code)
        if db_emp:
            return db_emp
        else:
            raise HTTPException(status_code=404, detail="Employee not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

# Get all employees
@router.get("/employees", response_model=List[EmployeeCreate])
def get_employees(db: Session = Depends(get_db)):
    print("inside router")
    try:
        return async_get_all_employees(db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

# Update employee by emp_code
@router.put("/employee/{emp_code}")
async def update_employee(emp_code: str, emp: EmployeeUpdate, db: Session = Depends(get_db)):
    try:
        return await async_update_employee(db, emp_code, emp)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

# Delete employee by emp_code
@router.delete("/employee/{emp_code}")
async def delete_employee(emp_code: str, db: Session = Depends(get_db)):
    try:
        return await async_delete_employee(db, emp_code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
