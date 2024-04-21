from typing import Optional

from sqlmodel import Field, SQLModel, Relationship


class City(SQLModel, table=True):
    __tablename__ = "cities"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    # population: int
    country_id: Optional[int] = Field(default=None, foreign_key="countries.id")
    country: Optional["Country"] = Relationship(back_populates="cities")


class Country(SQLModel, table=True):
    __tablename__ = "countries"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    cities: list[City] = Relationship(back_populates="country")
