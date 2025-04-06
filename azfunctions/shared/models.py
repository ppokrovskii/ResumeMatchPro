from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from shared.openai_service.models import DocumentAnalysis


class FileType(str, Enum):
    CV = "CV"
    JD = "JD"


class FileStatus(str, Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    EXTRACTING_TEXT = "EXTRACTING_TEXT"
    ANALYZING = "ANALYZING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class FontStyle(BaseModel):
    name: Optional[str] = None
    size: Optional[float] = None
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    underline: Optional[bool] = None


class DocumentStyle(BaseModel):
    name: str
    font: Optional[FontStyle] = None


class Line(BaseModel):
    content: str


class TableCell(BaseModel):
    text: str


class DocumentPage(BaseModel):
    page_number: int
    content: str
    lines: List[Line]
    tables: List[List[List[TableCell]]]


class DocumentStructure(BaseModel):
    text: str
    pages: List[DocumentPage]
    paragraphs: List[str]
    tables: List[List[List[TableCell]]]
    styles: dict[str, DocumentStyle]
    headers: List[str]
    footers: List[str]


class FileMetadataDb(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    filename: str
    type: Optional[FileType] = None
    user_id: str
    url: str
    text: Optional[str] = None
    content_type: Optional[str] = None
    status: FileStatus = FileStatus.UPLOADED
    status_message: Optional[str] = None

    # Structured document information
    pages: Optional[List[DocumentPage]] = None
    paragraphs: Optional[List[str]] = None
    tables: Optional[List[List[List[TableCell]]]] = None
    styles: Optional[Dict[str, DocumentStyle]] = None
    sections: Optional[List[str]] = None
    headers: Optional[List[str]] = None
    footers: Optional[List[str]] = None
    languages: Optional[List[str]] = None

    # Extracted document type and structure
    document_type: Optional[Any] = None
    structure: Optional[Dict[str, Any]] = None

    class Config:
        json_encoders = {UUID: str}
        exclude_none = True
