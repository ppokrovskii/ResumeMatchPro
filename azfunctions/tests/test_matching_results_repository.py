from uuid import UUID, uuid4
import pytest
from azure.cosmos import CosmosClient

# add project root to sys.path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from matching.schemas import CV_Match, Candidate_Capabilities, FileModel, JD_Requirements, MatchingResultModel
from shared.matching_results_repository import MatchingResultsRepository


@pytest.fixture
def repository() -> MatchingResultsRepository:
    # Create a Cosmos DB client and initialize the repository
    client = CosmosClient(url="https://localhost:8081",
                credential=(
                    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
                ),)
    db_client = client.get_database_client("resumematchpro_test")
    return MatchingResultsRepository(db_client)

# add pytest fixture to delete all items from the container before each test
@pytest.fixture(autouse=True)
def run_around_tests(repository):
    repository.delete_all()
        
@pytest.fixture
def sample_matching_result() -> MatchingResultModel:
    jd_id=UUID("5b304304-74f8-49db-8532-84a720052066")
    cv_id=UUID("13152cb7-3290-4fb6-a97d-8d29684ecfc8")
    user_id="123"
    return MatchingResultModel(
        user_id=user_id,
        cv=FileModel(id=cv_id, filename="cv.txt", type="CV", user_id="user_id", url="https://cv.com", text="Python Developer"),
        jd=FileModel(id=jd_id, filename="jd.txt", type="JD", user_id="user_id", url="https://jd.com", text="Python Developer"),
        jd_requirements=JD_Requirements(skills=["Python"], experience=["2 years"], education=["Bachelor"]),
        candidate_capabilities=Candidate_Capabilities(skills=["Python"], experience=["2 years"], education=["Bachelor"]),
        cv_match=CV_Match(skills_match=["Python"], experience_match=["2 years"], education_match=["Bachelor"], gaps=[]),
        overall_match_percentage=0.9
    )

# def test_add_result(repository):
#     # Create a sample matching result
#     matching_result = {
#         "cv": {"id": "cv_id"},
#         "jd": {"id": "jd_id"},
#         "score": 0.8
#     }

#     # Add the result to the repository
#     repository.add_result(matching_result)

#     # Retrieve the result from the repository
#     results = repository.get_results_by_cv_id("cv_id")
#     assert len(results) == 1
#     assert results[0]["score"] == 0.8

def test_upsert_result(repository, sample_matching_result):
    matching_result = sample_matching_result.model_dump(mode="json")
    # Upsert the result to the repository
    repository.upsert_result(matching_result)
    # Retrieve the result from the repository
    results = repository.get_results_by_cv_id(sample_matching_result.user_id, sample_matching_result.cv.id)
    assert len(results) == 1
    assert results[0]["cv"]["id"] == str(sample_matching_result.cv.id)
    assert results[0]["jd"]["id"] == str(sample_matching_result.jd.id)

def test_delete_matching_results_by_file(repository, sample_matching_result):
    matching_result = sample_matching_result.model_dump(mode="json")
    # Upsert the result to the repository
    repository.upsert_result(matching_result)
    # Delete the result by user_id and file_id
    repository.delete_matching_results_by_file(sample_matching_result.user_id, sample_matching_result.cv.id)
    # Retrieve the result from the repository
    results = repository.get_results_by_cv_id(sample_matching_result.user_id, sample_matching_result.cv.id)
    assert len(results) == 0

def test_get_results_by_cv_id(repository, sample_matching_result):
    matching_result = sample_matching_result.model_dump(mode="json")
    # Upsert the result to the repository
    repository.upsert_result(matching_result)
    # Retrieve results by CV ID
    results = repository.get_results_by_cv_id(sample_matching_result.user_id, sample_matching_result.cv.id)
    assert len(results) == 1
    assert results[0]["cv"]["id"] == str(sample_matching_result.cv.id)

def test_get_results_by_jd_id(repository, sample_matching_result):
    matching_result = sample_matching_result.model_dump(mode="json")
    # Upsert the result to the repository
    repository.upsert_result(matching_result)
    # Retrieve results by JD ID
    results = repository.get_results_by_jd_id(sample_matching_result.user_id, sample_matching_result.jd.id)
    assert len(results) == 1
    assert results[0]["jd"]["id"] == str(sample_matching_result.jd.id)