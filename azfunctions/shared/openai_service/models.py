import json
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator, root_validator


class PersonalDetail(BaseModel):
    type: str
    text: str


class ExperienceBlock(BaseModel):
    title: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    lines: List[str]


class EducationBlock(BaseModel):
    title: str
    start_date: str
    end_date: Optional[str] = None
    degree: Optional[str] = None
    details: Optional[str] = None
    city: Optional[str] = None


class CompanyDetail(BaseModel):
    type: str
    text: str


# Strict model for LLM validation
class CVStructure(BaseModel):
    personal_details: List[PersonalDetail]
    professional_summary: str
    skills: List[str]
    experience: List[ExperienceBlock]
    education: List[EducationBlock]
    job_title: Optional[str] = None
    additional_information: Optional[List[str]] = Field(
        default=None,
        description="List of strings containing additional information. Each string should be in the format 'Type: Value', e.g. 'Location: Dubai, United Arab Emirates' or 'Languages: English, Russian'",
    )


# Loose model for internal use
class CVStructureLoose(BaseModel):
    personal_details: Optional[List[PersonalDetail]] = []
    professional_summary: Optional[str] = ""
    skills: Optional[List[str]] = []
    experience: Optional[List[ExperienceBlock]] = []
    education: Optional[List[EducationBlock]] = []
    job_title: Optional[str] = None
    additional_information: Optional[List[str]] = None


# Strict model for LLM validation
class JDStructure(BaseModel):
    company_details: List[CompanyDetail]
    role_summary: str
    required_skills: List[str]
    experience_requirements: List[str]
    job_title: Optional[str] = None
    education_requirements: Optional[List[str]] = None
    additional_information: Optional[List[str]] = None


# Loose model for internal use
class JDStructureLoose(BaseModel):
    company_details: Optional[List[CompanyDetail]] = []
    role_summary: Optional[str] = ""
    required_skills: Optional[List[str]] = []
    experience_requirements: Optional[List[str]] = []
    job_title: Optional[str] = None
    education_requirements: Optional[List[str]] = None
    additional_information: Optional[List[str]] = None


# DocumentStructure that supports both CV and JD fields
class DocumentStructure(BaseModel):
    # CV fields
    personal_details: Optional[List[Dict[str, str]]] = None
    professional_summary: Optional[str] = None
    skills: Optional[List[str]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    education: Optional[List[Dict[str, Any]]] = None

    # JD fields
    company_details: Optional[List[Dict[str, str]]] = None
    role_summary: Optional[str] = None
    required_skills: Optional[List[str]] = None
    experience_requirements: Optional[List[str]] = None
    education_requirements: Optional[List[str]] = None

    # Common fields
    job_title: Optional[str] = None
    additional_information: Optional[List[str]] = None

    # Allow arbitrary fields
    model_config = {"extra": "allow"}


class DocumentType(Enum):
    CV = "CV"
    JD = "JD"


class DocumentAnalysis(BaseModel):
    document_type: DocumentType
    structure: CVStructureLoose | JDStructureLoose


class JDRequirements(BaseModel):
    skills: List[str]
    experience: List[str]
    education: List[str]


class CandidateCapabilities(BaseModel):
    skills: List[str]
    experience: List[str]
    education: List[str]


class CVMatch(BaseModel):
    skills_match: List[str]
    experience_match: List[str]
    education_match: List[str]
    gaps: List[str]


class MatchingResultModel(BaseModel):
    jd_requirements: JDRequirements
    candidate_capabilities: CandidateCapabilities
    cv_match: CVMatch
    overall_match_percentage: float

    @classmethod
    def from_json(cls, json_data):
        if isinstance(json_data, str):
            json_data = (
                json_data.replace("\n", " ")
                .replace("\t", " ")
                .replace("\r", " ")
                .replace("'", "'")
            )
            json_data = json.loads(json_data)
        return cls(
            jd_requirements=JDRequirements(**json_data["jd_requirements"]),
            candidate_capabilities=CandidateCapabilities(
                **json_data["candidate_capabilities"]
            ),
            cv_match=CVMatch(**json_data["cv_match"]),
            overall_match_percentage=json_data["overall_match_percentage"],
        )
