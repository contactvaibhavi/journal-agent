from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db import Base, engine, SessionLocal

try:
    with engine.connect() as connection:
        print("Connected to the database successfully!")
        session = SessionLocal()
        print("Session created successfully!")
except Exception as e:
    print(f"Error connecting to the database: {e}")
