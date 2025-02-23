from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
import json

class PersonalDetail(BaseModel):
    type: str
    text: str

class ExperienceBlock(BaseModel):
    title: str
    start_date: str
    end_date: Optional[str] = None
    lines: List[str]

class EducationBlock(BaseModel):
    title: str
    start_date: str
    end_date: Optional[str] = None
    degree: Optional[str] = None
    details: Optional[str] = None
    city: Optional[str] = None

class DocumentStructure(BaseModel):
    personal_details: List[PersonalDetail]
    professional_summary: str
    skills: List[str]
    experience: List[ExperienceBlock]
    education: List[EducationBlock]
    additional_information: Optional[List[str]] = None

class DocumentAnalysis(BaseModel):
    document_type: str  # "CV" or "JD"
    structure: DocumentStructure

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
            json_data = json_data.replace("\n", " ").replace("\t", " ").replace("\r", " ").replace("\'", "'")
            json_data = json.loads(json_data)
        return cls(
            jd_requirements=JDRequirements(**json_data['jd_requirements']),
            candidate_capabilities=CandidateCapabilities(**json_data['candidate_capabilities']),
            cv_match=CVMatch(**json_data['cv_match']),
            overall_match_percentage=json_data['overall_match_percentage']
        )
