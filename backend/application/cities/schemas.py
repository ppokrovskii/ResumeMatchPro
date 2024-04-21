from application.schemas import RMPBaseModel


class CityBase(RMPBaseModel):
    name: str


class CityCreate(CityBase):
    pass


class City(CityBase):
    id: int
    country_id: int

    # class Config:
    #     orm_mode = True
