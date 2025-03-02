from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class FileType(str, Enum):
    CV = "CV"
    JD = "JD"
    
class FileUploadBase(BaseModel):
    filename: str
    type: FileType
    user_id: str

class FileUploadRequest(FileUploadBase):
    content: bytes

class FileUploadResponse(FileUploadBase):
    id: UUID = Field(default_factory=uuid4)
    url: str
    
    # class Config:
    #     from_attributes = True
        
        
class FileUploadResponses(BaseModel):
    files: list[FileUploadResponse] = []
        
class FileUploadOutputQueueMessage(FileUploadResponse):
    pass
