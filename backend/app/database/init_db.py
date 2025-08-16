
"""Init Db module for the application.

This module provides functionality related to init db.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..database.db import Base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Create all tables in the database
def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database tables created.")
