from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4
from openai import BaseModel
from pydantic import Field


class FileType(str, Enum):
    CV = "CV"
    JD = "JD"
    
    
class UserFilesRequest(BaseModel):
    user_id: str
    type: Optional[FileType] = None
    
class File(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    filename: str
    type: FileType
    user_id: str
    url: str
    
class UserFilesResponse(BaseModel):
    files: List[File] = []
    