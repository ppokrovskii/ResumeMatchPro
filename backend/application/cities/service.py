from sqlmodel import select

from application.cities.models import City
from application.database import database


async def get_all_cities(skip: int = 0, limit: int = 10):
    query = select(City).offset(skip).limit(limit)
    result = await database.fetch_all(query=query)
    return result
