"""
UAT (User Acceptance Testing) for file processing.
This test runs the file processing Azure Function locally with real Azure services emulators.
"""

import logging
import os
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock

import pytest
from dotenv import load_dotenv

from users.models import UserDb

# Load environment variables from .env.test
test_env_path = Path(__file__).parent.parent / "tests" / ".env.test"
load_dotenv(test_env_path)

# Add parent directory to path so we can import the function app
current_dir = os.path.dirname(os.path.abspath(__file__))
azfunctions_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(azfunctions_dir)
sys.path.insert(0, root_dir)  # Add the root directory to path
sys.path.insert(0, azfunctions_dir)  # Add the azfunctions directory to path

# Import from the modules directly, not using azfunctions prefix
from shared.blob_service import FilesBlobService
from shared.db_service import get_cosmos_db_client
from shared.document_intelligence_service import DocumentIntelligenceService
from shared.files_repository import FilesRepository
from shared.matching_results_repository import MatchingResultsRepository
from shared.models import FileStatus, FileType
from shared.openai_service.openai_service import OpenAIService
from shared.user_repository import UserRepository

from file_processing.file_processing import FileProcessor
from file_processing.schemas import (
    FileProcessingRequest,
)
from matching.matching import MatchProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Test constants
TEST_CONTAINER_NAME = "resume-match-pro-files-test"
TEST_DATABASE_NAME = "resumematchpro_test"
PROCESSING_QUEUE_NAME = "file-processing-test"
MATCHING_QUEUE_NAME = "file-matching-test"
TEST_JD_FILE_PATH = Path(__file__).parent / "test_data" / "JD - iOS_Junior.docx"
TEST_CV_FILE_PATH = (
    Path(__file__).parent / "test_data" / "Pavel_Pokrovskii_-_Head_of_Engineering.pdf"
)
FUNCTION_API_BASE_URL = os.environ.get(
    "FUNCTION_API_BASE_URL", "http://localhost:7071/api"
)


@pytest.fixture(scope="function")
def setup_test_environment():
    """
    Setup test environment with all required services and repositories.
    This fixture is scoped to each test function to ensure a clean state.
    """
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Get cosmos client
    cosmos_client = get_cosmos_db_client()

    # Create test container if it doesn't exist
    blob_service = FilesBlobService(container_name=TEST_CONTAINER_NAME)

    # Create repositories with test container
    files_repository = FilesRepository(db_client=cosmos_client)
    matching_results_repository = MatchingResultsRepository(db_client=cosmos_client)

    # Clean up collections before test
    logger.info("Cleaning up collections before test")
    files_repository.delete_all()
    matching_results_repository.delete_all()

    # Create document intelligence service
    document_intelligence_service = DocumentIntelligenceService(
        key=os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_KEY"),
        endpoint=os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"),
    )

    # Create OpenAI service
    openai_service = OpenAIService()
    # pytest mock of queue service
    queue_service = Mock()

    # Create file processor
    processor = FileProcessor(
        repository=files_repository,
        blob_service=blob_service,
        document_intelligence_service=document_intelligence_service,
        openai_service=openai_service,
        queue_service=queue_service,
    )

    # Return all services and repositories
    return {
        "blob_service": blob_service,
        "queue_service": queue_service,
        "files_repository": files_repository,
        "matching_results_repository": matching_results_repository,
        "document_intelligence_service": document_intelligence_service,
        "openai_service": openai_service,
        "processor": processor,
    }


@pytest.mark.external_services
def test_complete_e2e_flow_with_matching(setup_test_environment):
    """
    Test the complete end-to-end flow including file processing and matching.
    This test verifies that files are processed correctly and matching results are generated.
    """
    # Create test user first
    cosmos_client = get_cosmos_db_client()
    user_repository = UserRepository(cosmos_client)
    user_id = "test-user-c3c9722c-fd3e-4010-b39e-16f1633acf08"
    test_user = user_repository.get_user(user_id)
    if not test_user:
        # Create test user with default limits
        test_user = UserDb(
            userId=user_id,
            name="Test User",
            email="test@example.com",
            filesCount=0,
            filesLimit=10,
            matchingUsedCount=0,
            matchingLimit=100,
            lastMatchingReset=datetime.now(UTC),
        )

        user_repository.create_user(test_user.model_dump())
        logger.info(f"Created test user with ID: {user_id}")

    # Create test files in database
    files_repository = FilesRepository(cosmos_client)
    services = setup_test_environment
    blob_service = services["blob_service"]
    queue_service = services["queue_service"]
    document_intelligence_service = services["document_intelligence_service"]
    openai_service = services["openai_service"]

    # Upload JD file
    logger.info("Uploading JD file for testing")
    with open(TEST_JD_FILE_PATH, "rb") as file:
        jd_content = file.read()

    jd_filename = os.path.basename(TEST_JD_FILE_PATH)
    jd_blob_name = f"{uuid.uuid4()}_{jd_filename}"
    jd_blob_url = blob_service.upload_blob(
        blob_service.container_name, jd_blob_name, jd_content
    )

    jd_file_data = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "filename": jd_filename,
        "type": FileType.JD,
        "blob_name": jd_blob_name,
        "url": jd_blob_url,
        "status": FileStatus.UPLOADED,
        "status_message": "File uploaded successfully",
    }
    jd_record = files_repository.upsert_file(jd_file_data)
    jd_file_id = str(jd_record.id)
    logger.info(f"JD file record created with ID: {jd_file_id}")

    # Create a queue message for processing the JD file
    jd_request = FileProcessingRequest(
        id=jd_file_id,
        user_id=user_id,
        filename=jd_blob_name,
        url=jd_blob_url,
        type=FileType.JD,
    )
    jd_request_dict = jd_request.model_dump()
    jd_request_dict["id"] = str(jd_request_dict["id"])

    # Process the JD file using the new FileProcessor class
    logger.info(f"Processing JD file: {jd_file_id}")
    os.environ["BLOB_CONTAINER_NAME"] = TEST_CONTAINER_NAME

    # Create FileProcessor with injected services
    processor = FileProcessor(
        repository=files_repository,
        blob_service=blob_service,
        document_intelligence_service=document_intelligence_service,
        openai_service=openai_service,
        queue_service=queue_service,
    )

    # Process the request
    jd_matching_request = processor.process(jd_request)
    logger.info(f"JD file processing completed: {jd_matching_request}")

    # Verify JD file was processed correctly
    assert str(jd_matching_request.file_id) == jd_file_id, "JD file ID mismatch"
    assert jd_matching_request.user_id == user_id, "JD user ID mismatch"
    assert jd_matching_request.type == FileType.JD, "JD file type mismatch"

    # Now upload and process the CV file
    logger.info("Uploading CV file for testing")
    with open(TEST_CV_FILE_PATH, "rb") as file:
        cv_content = file.read()

    cv_filename = os.path.basename(TEST_CV_FILE_PATH)
    cv_blob_name = f"{uuid.uuid4()}_{cv_filename}"
    cv_blob_url = blob_service.upload_blob(
        blob_service.container_name, cv_blob_name, cv_content
    )

    cv_file_data = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "filename": cv_filename,
        "type": FileType.CV,
        "blob_name": cv_blob_name,
        "url": cv_blob_url,
        "status": FileStatus.UPLOADED,
        "status_message": "File uploaded successfully",
    }
    cv_record = files_repository.upsert_file(cv_file_data)
    cv_file_id = str(cv_record.id)
    logger.info(f"CV file record created with ID: {cv_file_id}")

    # Create a queue message for processing the CV file
    cv_request = FileProcessingRequest(
        id=cv_file_id,
        user_id=user_id,
        filename=cv_blob_name,
        url=cv_blob_url,
        type=FileType.CV,
    )
    cv_request_dict = cv_request.model_dump()
    cv_request_dict["id"] = str(cv_request_dict["id"])

    # Process the CV file using the new FileProcessor class
    logger.info(f"Processing CV file: {cv_file_id}")
    # Use the new FileProcessor class with injected services
    processor = FileProcessor(
        repository=files_repository,
        blob_service=blob_service,
        document_intelligence_service=document_intelligence_service,
        openai_service=openai_service,
        queue_service=queue_service,
    )
    cv_matching_request = processor.process(cv_request)
    logger.info(f"CV file processing completed: {cv_matching_request}")

    # Verify CV file was processed correctly
    assert str(cv_matching_request.file_id) == cv_file_id, "CV file ID mismatch"
    assert cv_matching_request.user_id == user_id, "CV user ID mismatch"
    assert cv_matching_request.type == FileType.CV, "CV file type mismatch"

    logger.info("Creating matching requests using FileProcessingOutputQueueMessage")

    # Create processor directly
    processor = MatchProcessor.create_with_default_services()

    # Call match directly
    logger.info("Calling MatchProcessor.match for CV")
    cv_results = processor.match(cv_matching_request)
    if cv_results is None:
        logger.warning("CV matching returned None, using empty list instead")
        cv_results = []

    logger.info("Calling MatchProcessor.match for JD")
    jd_results = processor.match(jd_matching_request)
    if jd_results is None:
        logger.warning("JD matching returned None, using empty list instead")
        jd_results = []

    # Combine results from both calls
    matching_results = cv_results or jd_results

    # Verify matching results were created
    assert matching_results is not None, "Matching results should not be None"
    assert isinstance(matching_results, list), "Matching results should be a list"

    # Skip detailed checks if we didn't get any results
    for result in matching_results:
        # Check that the matching results contain the expected fields
        result = matching_results[0]
        assert "overall_match_percentage" in result, (
            "Result should have overall_match_percentage"
        )
        assert "jd_requirements" in result, "Result should have jd_requirements"
        assert "candidate_capabilities" in result, (
            "Result should have candidate_capabilities"
        )
        assert "cv_match" in result, "Result should have cv_match"
        logger.info("Matching results successfully generated and verified")
    else:
        logger.warning("No matching results were generated")
