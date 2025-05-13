# app/services/employee_service.py
from fastapi import APIRouter, Depends, HTTPException
from app.services.auth_service import login_user
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate
from app.utils.jwt import create_access_token
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()

# Create a Pydantic model for the login request
class LoginRequest(BaseModel):
    emp_code: str
    password: str

@router.post("/login")
async def login(
    login_request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    # Call login_user function to authenticate and generate JWT
    emp_code = login_request.emp_code
    password = login_request.password
    return await login_user(emp_code, password, db)