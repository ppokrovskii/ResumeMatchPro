
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class ContactDetailsDbModelBase(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    email: str
    phone: Optional[str] = None
    first_name: str
    last_name: str
    company: Optional[str] = None
    
    
class ContactDetailsDbModelCreate(ContactDetailsDbModelBase):
    pass

class ContactDetailsDbModelResponse(ContactDetailsDbModelBase):
    pass