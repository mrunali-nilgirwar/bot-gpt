from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# This is the database file that will be created on your computer

SQLALCHEMY_DATABASE_URL= "sqlite:///./bot.db"

#This creates the connection to the database
engine=create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

#This is like a factory that creates database sessions
SessionLocal= sessionmaker(autocommit=False, autoflush=False, bind=engine)

#This is the base class all our tables will inherit from
Base = declarative_base()

#This function gives us  a database session whenever we need one
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
	