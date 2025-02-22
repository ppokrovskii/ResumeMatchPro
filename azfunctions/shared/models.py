from enum import Enum
from typing import Optional, List, Dict
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

class FileType(str, Enum):
    CV = "CV"
    JD = "JD"

class DocumentPage(BaseModel):
    page_number: int
    content: str
    lines: List[str]
    tables: List[List[List[str]]]  # 3D array: tables -> rows -> cells

class DocumentStyle(BaseModel):
    name: str  # e.g., "Heading 1", "Normal", etc.
    font_name: Optional[str] = None
    font_size: Optional[float] = None
    is_bold: Optional[bool] = None
    is_italic: Optional[bool] = None
    is_underline: Optional[bool] = None

class FileMetadataDb(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    filename: str
    type: FileType
    user_id: str
    url: str
    text: Optional[str] = None
    
    # Structured document information
    pages: Optional[List[DocumentPage]] = None
    paragraphs: Optional[List[str]] = None
    tables: Optional[List[List[List[str]]]] = None  # 3D array: tables -> rows -> cells
    styles: Optional[Dict[str, DocumentStyle]] = None
    sections: Optional[List[str]] = None
    headers: Optional[List[str]] = None
    footers: Optional[List[str]] = None
    
    # do not serialize None values
    class Config:
        json_encoders = {
            UUID: str
        }
        exclude_none = True
    
    