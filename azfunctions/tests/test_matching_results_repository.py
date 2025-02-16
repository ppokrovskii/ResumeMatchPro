from uuid import UUID, uuid4
import pytest

# add project root to sys.path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from matching.schemas import CV_Match, Candidate_Capabilities, FileModel, JD_Requirements, MatchingResultModel

@pytest.fixture
def create_matching_result():
    def _create_matching_result():
        jd_id = uuid4()
        cv_id = uuid4()
        user_id = "test_user_123"
        return MatchingResultModel(
            user_id=user_id,
            cv=FileModel(id=cv_id, filename="cv.txt", type="CV", url="https://cv.com", text="Python Developer", user_id=user_id),
            jd=FileModel(id=jd_id, filename="jd.txt", type="JD", url="https://jd.com", text="Python Developer", user_id=user_id),
            jd_requirements=JD_Requirements(skills=["Python"], experience=["2 years"], education=["Bachelor"]),
            candidate_capabilities=Candidate_Capabilities(skills=["Python"], experience=["2 years"], education=["Bachelor"]),
            cv_match=CV_Match(skills_match=["Python"], experience_match=["2 years"], education_match=["Bachelor"], gaps=[]),
            overall_match_percentage=0.9
        )
    return _create_matching_result

def test_upsert_result(repository, create_matching_result):
    sample_matching_result = create_matching_result()
    matching_result = sample_matching_result.model_dump(mode="json")
    # Upsert the result to the repository
    repository.upsert_result(matching_result)
    # Retrieve the result from the repository
    results = repository.get_results_by_cv_id(sample_matching_result.user_id, sample_matching_result.cv.id)
    assert len(results) == 1
    assert results[0]["cv"]["id"] == str(sample_matching_result.cv.id)
    assert results[0]["jd"]["id"] == str(sample_matching_result.jd.id)

def test_delete_matching_results_by_file(repository, create_matching_result):
    sample_matching_result = create_matching_result()
    matching_result = sample_matching_result.model_dump(mode="json")
    # Upsert the result to the repository
    repository.upsert_result(matching_result)
    # Delete the result by file_id
    repository.delete_matching_results_by_file(sample_matching_result.user_id, sample_matching_result.cv.id)
    # Retrieve the result from the repository
    results = repository.get_results_by_cv_id(sample_matching_result.user_id, sample_matching_result.cv.id)
    assert len(results) == 0

def test_get_results_by_cv_id(repository, create_matching_result):
    sample_matching_result = create_matching_result()
    matching_result = sample_matching_result.model_dump(mode="json")
    # Upsert the result to the repository
    repository.upsert_result(matching_result)
    # Retrieve results by CV ID
    results = repository.get_results_by_cv_id(sample_matching_result.user_id, sample_matching_result.cv.id)
    assert len(results) == 1
    assert results[0]["cv"]["id"] == str(sample_matching_result.cv.id)

def test_get_results_by_jd_id(repository, create_matching_result):
    sample_matching_result = create_matching_result()
    matching_result = sample_matching_result.model_dump(mode="json")
    # Upsert the result to the repository
    repository.upsert_result(matching_result)
    # Retrieve results by JD ID
    results = repository.get_results_by_jd_id(sample_matching_result.user_id, sample_matching_result.jd.id)
    assert len(results) == 1
    assert results[0]["jd"]["id"] == str(sample_matching_result.jd.id)