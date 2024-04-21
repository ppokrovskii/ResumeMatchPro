from pydantic import BaseModel


class RMPBaseModel(BaseModel):
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
