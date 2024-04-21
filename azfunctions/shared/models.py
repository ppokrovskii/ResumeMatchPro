from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

class FileType(str, Enum):
    CV = "CV"
    JD = "JD"

class FileMetadataDb(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    filename: str
    type: FileType
    user_id: str
    url: str
    text: Optional[str] = None
    
    # do not serialize None values
    
    