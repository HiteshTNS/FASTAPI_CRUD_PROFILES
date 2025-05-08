# app/main.py
from logging import exception
from urllib.request import Request

from fastapi import FastAPI
from app.database import engine
from app.routes.employee import router as employee_router

from app.models import employee, address
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

app = FastAPI(
    title="Employee Management API",
    description="This is a test project for async FastAPI with MSSQL",
    version="1.0.0"
)

# Create tables on startup
@app.on_event("startup")
async def startup():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(employee.Base.metadata.create_all)
            await conn.run_sync(address.Base.metadata.create_all)
        print("✅ Database tables created successfully.")
    except Exception as e:
        print(f"❌ Failed to create tables: {str(e)}")

# ✅ Health check / test endpoint
@app.get("/ping", tags=["Test"])
async def ping():
    return {"message": "🏓 Pong! FastAPI is running."}

app.include_router(employee_router, prefix="/api", tags=["Employee"])


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        loc = " -> ".join(str(l) for l in error["loc"][1:])
        msg = error["msg"].replace("Value error,", "").strip()
        errors.append(f"{loc.capitalize()} {msg}")

    return JSONResponse(
        status_code=422,
        content={"detail": errors},
    )

