# app/database.py
import os
import urllib
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.models.employee import Base  # Your declarative Base from models
from app.core.config import settings

params = urllib.parse.quote_plus(
            f"DRIVER={settings.db.driver};"
            f"SERVER={settings.db.host},{settings.db.port};"
            f"DATABASE={settings.db.database};"
            f"UID={settings.db.username};"
            f"PWD={settings.db.password};"
            f"Encrypt={'yes' if settings.db.encrypt else 'no'};"
            f"TrustServerCertificate={'yes' if settings.db.trust_server_certificate else 'no'};"
            f"Domain={settings.db.domain};"
        )

DATABASE_URL = f"mssql+aioodbc:///?odbc_connect={params}"


print(f"🔗 DATABASE_URL: {DATABASE_URL}")

engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

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
