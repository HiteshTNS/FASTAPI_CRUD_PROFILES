# app/database.py
import os
import urllib
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.models.employee import Base  # Your declarative Base from models

# Load env vars
load_dotenv()

# Create connection string
params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={os.getenv('DB_SERVER')},{os.getenv('DB_PORT')};"
    f"DATABASE={os.getenv('DB_NAME')};"
    f"UID={os.getenv('DB_USER')};"
    f"PWD={os.getenv('DB_PASSWORD')};"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
    "Domain=TNSSINC;"
)

DATABASE_URL = f"mssql+aioodbc:///?odbc_connect={params}"

# Create the async engine for db creation
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=10,           # Number of connections in the pool
    max_overflow=20,        # Maximum number of connections that can be created in excess of pool_size
    pool_pre_ping=True,     # Test connections before using them
)

# Create session factory to manage db transactions
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
# async_session
# Dependency
async def get_db():   #called when interating with db and session will be cosed when the trasnaction id over
    async with async_session() as db:  #async with creates the session object
        try:
            yield db
        finally:
            await db.close()
            print("🧹 DB session closed.")

# Async table creation
# async def create_db_tables():
#     try:
#         async with engine.begin() as conn:  #async with is the context manager ensures the connection is properly hand;ed
#             await conn.run_sync(Base.metadata.create_all)
#         print("✅ Tables created successfully.")
#     except SQLAlchemyError as e:
#         print(f"❌ Failed to create tables: {e}")
