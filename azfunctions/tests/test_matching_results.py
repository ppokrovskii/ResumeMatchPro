import json
import base64
from unittest import mock
import azure.functions as func
from azure.cosmos import CosmosClient
import os
from pathlib import Path
import pytest
from uuid import uuid4
from matching_results.models import MatchingResultModel, FileModel, JD_Requirements, Candidate_Capabilities, CV_Match

# add project root to sys.path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from matching_results.matching_results import get_matching_results
from matching_results.models import MatchingResultsRequest, MatchingResultsResponse
from shared.matching_results_repository import MatchingResultsRepository

# Set up environment variables for Cosmos DB emulator
os.environ["COSMOS_URL"] = "https://localhost:8081"
os.environ["COSMOS_KEY"] = "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
os.environ["COSMOS_DB_NAME"] = "resumematchpro_test"

@pytest.fixture
def repository():
    # Create a Cosmos DB client and initialize the repository
    client = CosmosClient(
        url="https://localhost:8081",
        credential="C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
        connection_verify=False  # Skip SSL verification for emulator
    )
    
    # Create database if it doesn't exist
    database = client.create_database_if_not_exists("resumematchpro_test")
    return MatchingResultsRepository(database)

@pytest.fixture(autouse=True)
def cleanup(repository):
    # Clean up before test
    repository.delete_all()
    yield
    # Clean up after test
    repository.delete_all()

@pytest.fixture
def create_matching_result():
    def _create_matching_result():
        user_id = "test_user_123"
        cv_id = uuid4()
        jd_id = uuid4()
        return MatchingResultModel(
            user_id=user_id,
            cv=FileModel(id=cv_id, filename="file1.txt", type="CV", url="https://file1.txt", text=""),
            jd=FileModel(id=jd_id, filename="file2.txt", type="JD", url="https://file2.txt", text=""),
            jd_requirements=JD_Requirements(skills=["skill1", "skill2"], experience=["exp1", "exp2"], education=["edu1", "edu2"]),
            candidate_capabilities=Candidate_Capabilities(skills=["skill1", "skill2"], experience=["exp1", "exp2"], education=["edu1", "edu2"]),
            cv_match=CV_Match(skills_match=["skill1", "skill2"], experience_match=["exp1", "exp2"], education_match=["edu1", "edu2"], gaps=["gap1", "gap2"]),
            overall_match_percentage=0.5
        )
    return _create_matching_result

def test_get_matching_results(repository, create_matching_result):
    # Create test data using the fixture
    sample_matching_result = create_matching_result()
    matching_result = sample_matching_result.model_dump(mode="json")
    repository.upsert_result(matching_result)

    # Create mock B2C claims using the user id from the sample
    mock_claims = {
        "claims": [
            {
                "typ": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier",
                "val": "test_user_123"  # This should match the user_id in create_matching_result fixture
            }
        ]
    }
    encoded_claims = base64.b64encode(json.dumps(mock_claims).encode()).decode()

    # Create request with B2C claims header, using the sample CV id as file_id
    req = func.HttpRequest(
        method='GET',
        body=None,
        url='/api/results',
        params={'file_id': str(sample_matching_result.cv.id), 'file_type': 'CV'},
        headers={'X-MS-CLIENT-PRINCIPAL': encoded_claims}
    )

    # Call the function
    func_call = get_matching_results.build().get_user_function()
    response = func_call(req)

    # Assert the expected behavior
    assert response.status_code == 200
    assert response.mimetype == "application/json"

    result = json.loads(response.get_body().decode("utf-8"))
    for r in result["results"]:
        r.pop("id")
        r["cv"].pop("id")
        r["jd"].pop("id")
        r["jd_requirements"].pop("id", None)
        r["candidate_capabilities"].pop("id", None)
        r["cv_match"].pop("id", None)
        r.pop("user_id", None)
        r["cv"].pop("user_id", None)
        r["jd"].pop("user_id", None)

    assert result == {'results':
        [
            {
                'cv':
                    {
                        'filename': 'file1.txt',
                        'type': 'CV',
                        'url': 'https://file1.txt'
                    },
                'jd':
                    {
                        'filename': 'file2.txt',
                        'type': 'JD',
                        'url': 'https://file2.txt'
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



