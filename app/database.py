# database.py
import os
import urllib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.models.employee import Base
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)
# Create properly encoded connection string
params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={os.getenv('DB_SERVER')},{os.getenv('DB_PORT')};"
    f"DATABASE={os.getenv('DB_NAME')};"
    f"UID={os.getenv('DB_USER')};"
    f"PWD={os.getenv('DB_PASSWORD')};"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
    "Domain=TNSSINC;"
)

connection_string = f"mssql+pyodbc:///?odbc_connect={params}"
print("🔧 [DB] Final connection string:", connection_string)

# Create the engine
engine = create_engine(connection_string, echo=True)

# Create a session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to create tables
def create_db_tables():
    try:
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully.")
    except SQLAlchemyError as e:
        print("❌ Failed to create tables:", e)
