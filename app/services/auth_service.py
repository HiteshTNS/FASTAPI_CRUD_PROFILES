# app/services/auth_service.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
# from app.utils.jwt import decode_access_token
from app.models.employee import Employee
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.jwt import create_access_token
from app.utils.security import verify_password
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# Dependency to verify credentials and generate a token
async def login_user(emp_code: str, password: str, db: AsyncSession):
    # Fetch the employee from the database
    result = await db.execute(select(Employee).filter(Employee.emp_code == emp_code))
    user = result.scalar_one_or_none()

    # Validate the employee and password
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT Token if credentials are correct
    access_token = create_access_token(data={"sub": user.emp_code})  # ✅ Use 'sub' as the JWT subject
    return {"access_token": access_token, "token_type": "bearer"}

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        # Decode the token using the secret key and algorithm from your config
        payload = jwt.decode(token, settings.db.secret_key, algorithms=[settings.db.jwt_algorithm])

        # Extract 'sub' (subject) which contains the emp_code
        emp_code: str = payload.get("sub")
        if emp_code is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        print("✅ Valid token for emp_code:", emp_code)
        return emp_code

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )