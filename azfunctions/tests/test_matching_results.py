import json
from unittest import mock
import azure.functions as func



# add project root to sys.path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from matching_results.matching_results import get_matching_results
from matching_results.models import MatchingResultsRequest, MatchingResultsResponse

@mock.patch("matching_results.matching_results.get_cosmos_db_client")
@mock.patch("matching_results.matching_results.MatchingResultsRepository")
def test_get_matching_results(mock_matching_results_repository, mock_get_cosmos_db_client):
    # Mock the necessary dependencies
    mock_matching_results = [
        {
            "user_id": "123",
            "cv": {
                "filename": "file1.txt",
                "type": "CV",
                "user_id": "123",
                "url": "https://file1.txt",
                "text": None
            },
            "jd": {
                "filename": "file2.txt",
                "type": "JD",
                "user_id": "123",
                "url": "https://file2.txt",
                "text": None
            },
            "jd_requirements": {
                "skills": ["skill1", "skill2"],
                "experience": ["exp1", "exp2"],
                "education": ["edu1", "edu2"]
            },
            "candidate_capabilities": {
                "skills": ["skill1", "skill2"],
                "experience": ["exp1", "exp2"],
                "education": ["edu1", "edu2"]
            },
            "cv_match": {
                "skills_match": ["skill1", "skill2"],
                "experience_match": ["exp1", "exp2"],
                "education_match": ["edu1", "edu2"],
                "gaps": ["gap1", "gap2"]
            },
            "overall_match_percentage": 0.5
        }
    ]
    mock_matching_results_repository.return_value.get_results_by_file_type_and_id.return_value = mock_matching_results
    mock_get_cosmos_db_client.return_value = "mock_cosmos_db_client"

    req = func.HttpRequest(method='GET',
                           body=None,
                           url='/api/results',
                           params={'user_id': '123', 'file_id': 'cba283f1-552e-4e75-9629-659cb42f8b20', 'file_type': 'CV'})
    # Call the function.
    func_call = get_matching_results.build().get_user_function()
    response = func_call(req)


    # Assert the expected behavior
    assert response.status_code == 200
    assert response.mimetype == "application/json"
    # assert expected response will be like '{"results":[{"id":"cba283f1-552e-4e75-9629-659cb42f8b20","user_id":"123","cv":{"filename":"file1.txt","type":"CV","user_id":"123","url":"https://file1.txt","text":null},"jd":{"filename":"file2.txt","type":"JD","user_id":"123","url":"https://file2.txt","text":null},"jd_requirements":{"skills":["skill1","skill2"],"experience":["exp1","exp2"],"education":["edu1","edu2"]},"candidate_capabilities":{"skills":["skill1","skill2"],"experience":["exp1","exp2"],"education":["edu1","edu2"]},"cv_match":{"skills_match":["skill1","skill2"],"experience_match":["exp1","exp2"],"education_match":["edu1","edu2"],"gaps":["gap1","gap2"]},"overall_match_percentage":0.5}]}'
    # don't asser id because it's generated randomly
    result = json.loads(response.get_body().decode("utf-8"))
    for r in result["results"]:
        r.pop("id")
        r["cv"].pop("id")
        r["jd"].pop("id")
        r["jd_requirements"].pop("id")
        r["candidate_capabilities"].pop("id")
        r["cv_match"].pop("id")
        
    assert result == {'results': 
        [
            {
            'user_id': '123', 
            'cv': 
                {
                    'filename': 'file1.txt', 
                    'type': 'CV', 
                    'user_id': '123', 
                    'url': 'https://file1.txt'
                    }, 
                'jd': 
                    {
                        'filename': 'file2.txt', 
                        'type': 'JD', 
                        'user_id': '123', 'url': 'https://file2.txt'
                    }, 
                'jd_requirements': 
                    {
                        'skills': ['skill1', 'skill2'], 
                        'experience': ['exp1', 'exp2'], 
                        'education': ['edu1', 'edu2']
                    }, 
                'candidate_capabilities': 
                    {
                        'skills': ['skill1', 'skill2'], 
                        'experience': ['exp1', 'exp2'], 
                        'education': ['edu1', 'edu2']
                    }, 
                'cv_match': 
                    {
                        'skills_match': ['skill1', 'skill2'], 
                        'experience_match': ['exp1', 'exp2'], 
                        'education_match': ['edu1', 'edu2'], 
                        'gaps': ['gap1', 'gap2']
                    }, 
                'overall_match_percentage': 0.5
            }
         ]
        }
    assert mock_matching_results_repository.return_value.get_results_by_file_type_and_id.call_args == mock.call("123", "cba283f1-552e-4e75-9629-659cb42f8b20", "CV")
    assert mock_matching_results_repository.return_value.get_results_by_file_type_and_id.call_count == 1
    assert mock_get_cosmos_db_client.call_count == 1
    assert mock_get_cosmos_db_client.call_args == mock.call()
    



