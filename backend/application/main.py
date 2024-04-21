import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI

# add root folder to pythonpath so I could import application.*
backend_directory = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(os.path.abspath(backend_directory))
# load dotenv
load_dotenv(dotenv_path=os.path.join(backend_directory, '..', '.env'))

from application.database import database
from application.cities.router import router as cities_router

app = FastAPI()

app.include_router(cities_router, prefix="/api/cities")


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
async def root():
    return {"message": "Hello World"}
