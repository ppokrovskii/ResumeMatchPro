from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
import json

class MatchingBaseModel(BaseModel):
    pass

class JD_Requirements(MatchingBaseModel):
    id: UUID = Field(default_factory=uuid4)
    skills: Optional[List[str]] = []
    experience: Optional[List[str]] = []
    education: Optional[List[str]] = []
    
    
class Candidate_Capabilities(MatchingBaseModel):
    id: UUID = Field(default_factory=uuid4)
    skills: Optional[List[str]] = []
    experience: Optional[List[str]] = []
    education: Optional[List[str]] = []
    
    
class CV_Match(MatchingBaseModel):
    id: UUID = Field(default_factory=uuid4)
    skills_match: List[str]
    experience_match: List[str]
    education_match: List[str]
    gaps: List[str]
    
class MatchingResultModel(MatchingBaseModel):
    id: UUID = Field(default_factory=uuid4)
    jd_requirements: JD_Requirements
    candidate_capabilities: Candidate_Capabilities
    cv_match: CV_Match
    overall_match_percentage: float
    
    # function to create model from json by creating nested models first
    @classmethod
    def from_json(cls, json_data):
        if isinstance(json_data, str):
            json_data = json_data.replace("\n", " ").replace("\t", " ").replace("\r", " ").replace("\'", "'")
            json_data = json.loads(json_data)
        jd_requirements = JD_Requirements(**json_data['jd_requirements'])
        candidate_capabilities = Candidate_Capabilities(**json_data['candidate_capabilities'])
        cv_match = CV_Match(**json_data['cv_match'])
        overall_match_percentage = json_data['overall_match_percentage']
        return cls(jd_requirements=jd_requirements, candidate_capabilities=candidate_capabilities, cv_match=cv_match, overall_match_percentage=overall_match_percentage)
