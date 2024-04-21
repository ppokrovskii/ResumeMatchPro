
# add project root to sys.path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))


from shared.openai_service.models import MatchingResultModel


def test_str_to_matching_result_model():
    json_str = '{\n  "jd_requirements": {\n    "skills": [\n      "Python",\n      "SQL",\n      "MS Office",\n      "CSV",\n      "JSON",\n      "XML",\n      "XSD",\n      "XPATH"\n    ],\n    "experience": [],\n    "education": []\n  },\n  "candidate_capabilities": {\n    "skills": [\n      "Python",\n      "MS Office",\n      "Git",\n      "JIRA",\n      "SQL",\n      "HTML & CSS",\n      "JavaScript",\n      "Data Analysis"\n    ],\n    "experience": [\n      "15+ years of experience as a technical manager",\n      "Managed multiple distributed Scrum Teams",\n      "Product Management",\n      "People Management",\n      "Agile",\n      "Effective Time Management",\n      "Teamwork",\n      "Ability to Work Under Pressure",\n      "Communication"\n    ],\n    "education": [\n      "Master\'s degree in Moscow State University of Railway Engineering"\n    ]\n  },\n  "cv_match": {\n    "skills_match": [\n      "Python",\n      "SQL",\n      "MS Office"\n    ],\n    "experience_match": [\n      "Product Management",\n      "People Management",\n      "Agile",\n      "Effective Time Management",\n      "Teamwork",\n      "Ability to Work Under Pressure",\n      "Communication"\n    ],\n    "education_match": [\n      "Master\'s degree in Moscow State University of Railway Engineering"\n    ],\n    "gaps": [\n      "CSV",\n      "JSON",\n      "XML",\n      "XSD",\n      "XPATH"\n    ]\n  },\n  "overall_match_percentage": 68\n}'
    result = MatchingResultModel.from_json(json_str)
    assert isinstance(result, MatchingResultModel)
    assert result.overall_match_percentage == 68
    assert result.cv_match.skills_match == ["Python", "SQL", "MS Office"]
    assert result.cv_match.gaps == ["CSV", "JSON", "XML", "XSD", "XPATH"]
    assert result.jd_requirements.skills == ["Python", "SQL", "MS Office", "CSV", "JSON", "XML", "XSD", "XPATH"]
    assert result.jd_requirements.experience == []
    assert result.jd_requirements.education == []
    assert result.candidate_capabilities.skills == ["Python", "MS Office", "Git", "JIRA", "SQL", "HTML & CSS", "JavaScript", "Data Analysis"]
    assert result.candidate_capabilities.experience == ["15+ years of experience as a technical manager", "Managed multiple distributed Scrum Teams", "Product Management", "People Management", "Agile", "Effective Time Management", "Teamwork", "Ability to Work Under Pressure", "Communication"]
    assert result.candidate_capabilities.education == ["Master's degree in Moscow State University of Railway Engineering"]
    