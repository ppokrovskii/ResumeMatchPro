from typing import List

from fastapi import APIRouter

from application.cities.schemas import City
from application.cities.service import get_all_cities

router = APIRouter()


@router.get("/", response_model=List[City])
async def get_cities():
    cities = await get_all_cities()
    return cities
