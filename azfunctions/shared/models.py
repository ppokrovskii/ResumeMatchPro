from enum import Enum
from typing import Optional, List, Dict
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

from shared.openai_service.models import DocumentAnalysis

class FileType(str, Enum):
    CV = "CV"
    JD = "JD"

class Line(BaseModel):
    content: str

class TableCell(BaseModel):
    text: str

class DocumentPage(BaseModel):
    page_number: int
    content: str
    lines: List[Line]
    tables: Optional[List[List[List[TableCell]]]] = None

class DocumentStyle(BaseModel):
    name: str
    font_name: Optional[str] = None
    font_size: Optional[float] = None
    is_bold: Optional[bool] = None
    is_italic: Optional[bool] = None
    is_underline: Optional[bool] = None

class DocumentStructure(BaseModel):
    personal_details: List[dict]  # type and text
    professional_summary: str
    skills: List[str]
    experience: List[dict]  # title, start_date, end_date, lines
    education: List[dict]  # title, start_date, end_date, degree, details, city
    additional_information: Optional[List[str]] = None

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
    tables: Optional[List[List[List[TableCell]]]] = None
    styles: Optional[Dict[str, DocumentStyle]] = None
    sections: Optional[List[str]] = None
    headers: Optional[List[str]] = None
    footers: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    
    # Document analysis results
    document_analysis: Optional[DocumentAnalysis] = None
    
    class Config:
        json_encoders = {UUID: str}
        exclude_none = True
    
    