import os
import sys

from fastapi import FastAPI
from app.database import  create_db_tables
# from app.routes import employee
from app.routes.employee import router as employee_router

print("🚀 main.py is running")

app = FastAPI()
# Ensure project root is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))



@app.on_event("startup")
def startup():
    try:
        print("Connecting to DB...")
        create_db_tables()
        print("✅ Tables created successfully.")
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")



@app.get("/ping")
def ping():
    return {"message": "pong"}
# Include the employee routes
app.include_router(employee_router, prefix="/api")
