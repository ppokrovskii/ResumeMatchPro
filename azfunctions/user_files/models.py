from enum import Enum
from typing import Any, List, Optional

from openai import BaseModel


class FileType(str, Enum):
    CV = "CV"
    JD = "JD"


class UserFilesRequest(BaseModel):
    user_id: str
    type: Optional[FileType] = None


class TableCell(BaseModel):
    text: str


class Line(BaseModel):
    content: str


class Table(BaseModel):
    cells: List[List[TableCell]]


class Page(BaseModel):
    page_number: int
    content: str
    lines: List[Line]
    tables: List[List[List[TableCell]]]


class PersonalDetail(BaseModel):
    type: str
    text: str


class ExperienceEntry(BaseModel):
    title: str
    start_date: str
    end_date: str
    lines: List[str]


class ResumeStructure(BaseModel):
    personal_details: List[PersonalDetail]
    professional_summary: str
    skills: List[str]
    experience: List[ExperienceEntry]
    education: List[Any]
    additional_information: Optional[List[str]] = None


class File(BaseModel):
    id: str
    filename: str
    type: Optional[str] = None
    user_id: str
    url: str
    structure: Optional[ResumeStructure] = None
    status: Optional[str] = None
    status_message: Optional[str] = None
    name: Optional[str] = None
    job_title: Optional[str] = None


class UserFilesResponse(BaseModel):
    files: List[File] = []
