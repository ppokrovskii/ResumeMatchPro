import os

from sqlmodel import SQLModel, create_engine
from databases import Database

DATABASE_URL = os.environ["APP_DATABASE_URL"]
# print(f"DATABASE_URL: {DATABASE_URL}")

# For SQLModel to use the async engine from databases package
engine = create_engine(DATABASE_URL, echo=True, future=True)

# Creating an instance of the Database class for async operations
database = Database(DATABASE_URL)
