from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from typing import Optional

class FileType(str, Enum):
    CV = "CV"
    JD = "JD"
    

class FileProcessingBase(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    filename: str
    type: FileType
    user_id: str
    url: str

class FileProcessingRequest(FileProcessingBase):
    pass
    
    
class FileProcessingOutputQueueMessage(BaseModel):
    file_id: UUID
    user_id: str
    type: FileType
    filename: Optional[str] = None
    url: Optional[str] = None