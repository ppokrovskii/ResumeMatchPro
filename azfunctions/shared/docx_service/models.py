from typing import List, Optional

from pydantic import BaseModel, Field


class FontStyle(BaseModel):
    name: Optional[str] = None
    size: Optional[float] = None
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    underline: Optional[bool] = None


class DocumentStyle(BaseModel):
    name: str
    font: Optional[FontStyle] = None


class TableCell(BaseModel):
    text: str


class Line(BaseModel):
    content: str


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
