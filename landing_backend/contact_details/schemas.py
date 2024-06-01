from typing import List, Optional
from pydantic import BaseModel, Field

class ContactDetailsBase(BaseModel):
    email: str
    phone: Optional[str] = None
    first_name: str
    last_name: str
    company: Optional[str] = None
    
    
class ContactDetailsCreate(ContactDetailsBase):
    pass

class ContactDetailsResponse(ContactDetailsBase):
    id: str
    
class ManyContactDetailsResponse(BaseModel):
    contact_details: list[ContactDetailsResponse]
    
    @classmethod
    def from_list_of_models(cls, list_of_models):
        items = list_of_models
        return cls(items=items)