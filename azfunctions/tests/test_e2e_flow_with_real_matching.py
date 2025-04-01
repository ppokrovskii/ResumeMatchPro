import json
import logging
import os
import uuid
from unittest.mock import MagicMock, patch

import pytest
from file_processing.file_processing import FileProcessor
from file_processing.schemas import FileProcessingRequest
from matching.matching import MatchProcessor
from matching.schemas import MatchingRequestMessage
from shared.blob_service import FilesBlobService
from shared.db_service import get_cosmos_db_client
from shared.document_intelligence_service import DocumentIntelligenceService
from shared.files_repository import FilesRepository
from shared.matching_results_repository import MatchingResultsRepository
from shared.models import FileMetadataDb, FileStatus, FileType
from shared.openai_service.openai_service import OpenAIService
from shared.queue_service import QueueService
from shared.user_repository import UserRepository
from users.models import UserDb

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Mock class for Queue Message
class MockQueueMessage:
    def __init__(self, body):
        self.body = body if isinstance(body, bytes) else body.encode("utf-8")

    def get_body(self):
        return self.body

    def get_json(self):
        return json.loads(self.body)


# Test container name
TEST_CONTAINER_NAME = "test-files"

# Test file paths - update with actual test files
TEST_JD_FILE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "uat", "test_data", "JD - iOS_Junior.docx"
)
TEST_CV_FILE_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "uat",
    "test_data",
    "Pavel_Pokrovskii_-_Head_of_Engineering.pdf",
)


@pytest.fixture
def setup_test_environment():
    """Set up the test environment with all required services."""
    # Create service instances
    cosmos_db_client = get_cosmos_db_client()
    files_repository = FilesRepository(cosmos_db_client)
    matching_results_repository = MatchingResultsRepository(cosmos_db_client)
    user_repository = UserRepository(cosmos_db_client)
    blob_service = FilesBlobService(container_name=TEST_CONTAINER_NAME)
    queue_service = QueueService(os.environ.get("AZURE_STORAGE_CONNECTION_STRING"))
    document_intelligence_service = DocumentIntelligenceService(
        key=os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_KEY"),
        endpoint=os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"),
    )
    openai_service = OpenAIService()

    # Return the services for use in tests
    services = {
        "files_repository": files_repository,
        "matching_results_repository": matching_results_repository,
        "user_repository": user_repository,
        "blob_service": blob_service,
        "queue_service": queue_service,
        "document_intelligence_service": document_intelligence_service,
        "openai_service": openai_service,
    }

    return services


@pytest.mark.external_services
def test_complete_e2e_flow_with_real_matching(setup_test_environment):
    """
    Complete end-to-end test including file upload, processing, and matching.
    This test ensures that matching happens naturally without manually creating data.

    Steps:
    1. Upload and process a JD file
    2. Upload and process a CV file
    3. Trigger matching through the queue for both files
    4. Verify matching results are generated automatically
    """
    # Set up test environment
    services = setup_test_environment
    blob_service = services["blob_service"]
    queue_service = services["queue_service"]
    files_repository = services["files_repository"]
    matching_results_repository = services["matching_results_repository"]
    user_repository = services["user_repository"]
    document_intelligence_service = services["document_intelligence_service"]
    openai_service = services["openai_service"]

    # Generate a unique user ID for this test
    user_id = f"test-user-{uuid.uuid4()}"
    logger.info(f"Using test user ID: {user_id}")

    # Create test user
    test_user = UserDb(
        id=user_id,
        userId=user_id,
        email=f"test-{uuid.uuid4()}@example.com",
        name="Test User",
        isAdmin=False,
        filesLimit=20,
        matchingLimit=100,
        matchingUsedCount=0,
        filesCount=0,
    )
    user_repository.create_user(test_user.model_dump())
    logger.info(f"Created test user: {user_id}")

    # Upload JD file
    logger.info("Uploading JD file for testing")
    with open(TEST_JD_FILE_PATH, "rb") as file:
        jd_content = file.read()

    jd_filename = os.path.basename(TEST_JD_FILE_PATH)
    jd_blob_name = f"{uuid.uuid4()}_{jd_filename}"
    jd_blob_url = blob_service.upload_blob(
        TEST_CONTAINER_NAME, jd_blob_name, jd_content
    )

    jd_file_data = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "filename": jd_filename,
        "type": FileType.JD,
        "url": jd_blob_url,
        "status": FileStatus.UPLOADED,
        "status_message": "File uploaded successfully",
    }
    jd_record = files_repository.upsert_file(jd_file_data)
    jd_file_id = str(jd_record.id)
    logger.info(f"JD file record created with ID: {jd_file_id}")

    # Create a request for processing the JD file
    jd_request = FileProcessingRequest(
        id=jd_file_id,
        user_id=user_id,
        filename=jd_blob_name,
        url=jd_blob_url,
        type=FileType.JD,
    )

    # Process the JD file
    logger.info(f"Processing JD file: {jd_file_id}")
    processor = FileProcessor(
        repository=files_repository,
        blob_service=blob_service,
        document_intelligence_service=document_intelligence_service,
        openai_service=openai_service,
        queue_service=queue_service,
    )
    jd_result = processor.process(jd_request)
    logger.info(f"JD file processing completed: {jd_result}")

    # Verify JD file was processed correctly
    processed_jd = files_repository.get_file_by_id(user_id, jd_file_id)
    assert processed_jd is not None, "JD file record not found after processing"
    assert processed_jd.status == FileStatus.COMPLETED, (
        f"JD file processing failed: {processed_jd.status_message}"
    )
    assert processed_jd.type == FileType.JD, "JD file type was not detected correctly"

    # Upload CV file
    logger.info("Uploading CV file for testing")
    with open(TEST_CV_FILE_PATH, "rb") as file:
        cv_content = file.read()

    cv_filename = os.path.basename(TEST_CV_FILE_PATH)
    cv_blob_name = f"{uuid.uuid4()}_{cv_filename}"
    cv_blob_url = blob_service.upload_blob(
        TEST_CONTAINER_NAME, cv_blob_name, cv_content
    )

    cv_file_data = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "filename": cv_filename,
        "type": FileType.CV,
        "url": cv_blob_url,
        "status": FileStatus.UPLOADED,
        "status_message": "File uploaded successfully",
    }
    cv_record = files_repository.upsert_file(cv_file_data)
    cv_file_id = str(cv_record.id)
    logger.info(f"CV file record created with ID: {cv_file_id}")

    # Create a request for processing the CV file
    cv_request = FileProcessingRequest(
        id=cv_file_id,
        user_id=user_id,
        filename=cv_blob_name,
        url=cv_blob_url,
        type=FileType.CV,
    )

    # Process the CV file
    logger.info(f"Processing CV file: {cv_file_id}")
    cv_result = processor.process(cv_request)
    logger.info(f"CV file processing completed: {cv_result}")

    # Verify CV file was processed correctly
    processed_cv = files_repository.get_file_by_id(user_id, cv_file_id)
    assert processed_cv is not None, "CV file record not found after processing"
    assert processed_cv.status == FileStatus.COMPLETED, (
        f"CV file processing failed: {processed_cv.status_message}"
    )
    assert processed_cv.type == FileType.CV, "CV file type was not detected correctly"

    # Important: Process files should have text or structure stored
    assert processed_cv.text is not None or (
        hasattr(processed_cv, "structure") and processed_cv.structure is not None
    ), "CV file does not have text or structure data"

    assert processed_jd.text is not None or (
        hasattr(processed_jd, "structure") and processed_jd.structure is not None
    ), "JD file does not have text or structure data"

    # Manually call the matching function (this should be done by the queue in production)
    # This simulates the queue trigger but in a controlled test environment
    logger.info("Triggering matching process for CV and JD")

    # Create matching request messages
    cv_matching_data = MatchingRequestMessage(
        file_id=cv_file_id,
        user_id=user_id,
        filename=cv_blob_name,
        url=cv_blob_url,
        type=FileType.CV,
    )

    jd_matching_data = MatchingRequestMessage(
        file_id=jd_file_id,
        user_id=user_id,
        filename=jd_blob_name,
        url=jd_blob_url,
        type=FileType.JD,
    )

    # Process the matching - let the real matching happen
    logger.info("Calling matching function for CV")
    match_processor = MatchProcessor(
        files_repository=files_repository,
        matching_results_repository=matching_results_repository,
        openai_service=openai_service,
        user_repository=user_repository,
    )
    match_processor.match(cv_matching_data)

    logger.info("Calling matching function for JD")
    match_processor.match(jd_matching_data)

    # Get matching results
    logger.info("Getting matching results")
    # Check for results with CV as source
    cv_results = matching_results_repository.get_results_by_file_type_and_id(
        user_id, cv_file_id, "CV"
    )

    # Check for results with JD as source
    jd_results = matching_results_repository.get_results_by_file_type_and_id(
        user_id, jd_file_id, "JD"
    )

    matching_results = cv_results or jd_results
    logger.info(f"Found matching results: {len(matching_results)} result(s)")

    # Verify matching results
    assert matching_results is not None, "Matching results should not be None"
    assert len(matching_results) > 0, "Should have at least one matching result"

    # Check that the matching results contain the expected fields
    for result in matching_results:
        assert "overall_match_percentage" in result, (
            "Result should have overall_match_percentage"
        )
        assert "jd_requirements" in result, "Result should have jd_requirements"
        assert "candidate_capabilities" in result, (
            "Result should have candidate_capabilities"
        )
        assert "cv_match" in result, "Result should have cv_match"

    # Clean up
    logger.info("Cleaning up test resources")
    blob_service.delete_blob(TEST_CONTAINER_NAME, jd_blob_name)
    blob_service.delete_blob(TEST_CONTAINER_NAME, cv_blob_name)
    files_repository.delete_file(user_id, jd_file_id)
    files_repository.delete_file(user_id, cv_file_id)

    matching_results_repository.delete_all()

    logger.info("Test completed successfully")
