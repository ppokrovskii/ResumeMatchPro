"""
UAT (User Acceptance Testing) for file processing.
This test runs the file processing Azure Function locally with real Azure services emulators.
"""
import os
import sys
import pytest
import uuid
import json
import logging
import time
import requests
from pathlib import Path
from dotenv import load_dotenv
from azure.cosmos import CosmosClient

# Add parent directory to path so we can import the function app
current_dir = os.path.dirname(os.path.abspath(__file__))
azfunctions_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(azfunctions_dir)
sys.path.insert(0, root_dir)  # Add the root directory to path
sys.path.insert(0, azfunctions_dir)  # Add the azfunctions directory to path

# Load environment variables from test env file
load_dotenv(Path(azfunctions_dir) / "tests" / ".env.test")

# Import from the modules directly, not using azfunctions prefix
from shared.blob_service import FilesBlobService
from shared.queue_service import QueueService
from shared.files_repository import FilesRepository
from shared.models import FileStatus, FileType
from file_processing.schemas import FileProcessingRequest
from matching_results.models import MatchingResultsRequest
from file_processing.file_processing import _process_file_impl, _get_blob_service

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test constants
TEST_CONTAINER_NAME = "test-files"
PROCESSING_QUEUE_NAME = "processing-queue"
MATCHING_QUEUE_NAME = "matching-queue"
TEST_JD_FILE_PATH = os.path.join(os.path.dirname(__file__), "test_data", "JD - iOS_Junior.docx")
TEST_CV_FILE_PATH = os.path.join(os.path.dirname(__file__), "test_data", "Pavel_Pokrovskii_-_Head_of_Engineering.pdf")
FUNCTION_API_BASE_URL = os.environ.get("FUNCTION_API_BASE_URL", "http://localhost:7071/api")

# Store the original _get_blob_service function
original_get_blob_service = _get_blob_service

# Create a test blob service instance
test_blob_service = None

# Override the _get_blob_service function
def mock_get_blob_service():
    """Return the test blob service instance."""
    return test_blob_service

# Override the default container name in FilesBlobService
original_init = FilesBlobService.__init__

def patched_init(self):
    original_init(self)
    self.container_name = TEST_CONTAINER_NAME

FilesBlobService.__init__ = patched_init

def get_cosmos_db_client():
    """Get a Cosmos DB client for testing."""
    # Use the same environment variables as in the application
    url = os.environ.get("COSMOS_DB_URL")
    cosmos_key = os.environ.get("COSMOS_DB_KEY")
    db_name = os.environ.get("COSMOS_DB_DATABASE")
    
    # Set the environment variables expected by the application
    os.environ["COSMOS_URL"] = url
    os.environ["COSMOS_KEY"] = cosmos_key
    os.environ["COSMOS_DB_NAME"] = db_name
    
    logger.info(f"Connecting to Cosmos DB at {url}")
    
    # Create a CosmosClient
    client = CosmosClient(url=url, credential=cosmos_key)
    
    # Create db if not exists
    client.create_database_if_not_exists(db_name)
    return client.get_database_client(db_name)

@pytest.fixture(scope="module")
def setup_test_environment():
    """Set up the test environment by ensuring containers and queues exist."""
    # Get connection string from environment
    connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        pytest.skip("AZURE_STORAGE_CONNECTION_STRING environment variable not set")
    
    logger.info(f"Using connection string: {connection_string[:20]}...")
    
    # Create blob service with explicit connection string
    blob_service = FilesBlobService()
    blob_service.container_name = TEST_CONTAINER_NAME
    
    # Set the global test blob service
    global test_blob_service
    test_blob_service = blob_service
    
    # Patch the _get_blob_service function
    from file_processing import file_processing
    file_processing._get_blob_service = mock_get_blob_service
    
    # Ensure container exists
    container_client = blob_service.blob_service_client.get_container_client(TEST_CONTAINER_NAME)
    if not container_client.exists():
        container_client.create_container()
    
    # Create queue service and ensure queue exists
    queue_service = QueueService(connection_string=connection_string)
    queue_service.create_queue_if_not_exists(PROCESSING_QUEUE_NAME)
    queue_service.create_queue_if_not_exists(MATCHING_QUEUE_NAME)
    
    # Get database client
    db = get_cosmos_db_client()
    
    # Create files repository
    files_repository = FilesRepository(db)
    
    # Return services for use in tests
    return {
        "blob_service": blob_service,
        "queue_service": queue_service,
        "files_repository": files_repository
    }

class MockQueueMessage:
    """Mock Azure Queue Message for testing."""
    def __init__(self, message_body):
        self.message_body = message_body
    
    def get_body(self):
        if isinstance(self.message_body, str):
            return self.message_body.encode('utf-8')
        return self.message_body
    
    def get_json(self):
        """Parse the message body as JSON."""
        if isinstance(self.message_body, str):
            return json.loads(self.message_body)
        return json.loads(self.message_body.decode('utf-8'))

@pytest.mark.external_services
def test_file_processing_e2e(setup_test_environment):
    """
    End-to-end test for file processing.
    
    This test:
    1. Uploads a file to blob storage
    2. Creates a file record in the database
    3. Creates a queue message for processing the file
    4. Calls the file processing function directly
    5. Verifies the file was processed correctly
    """
    services = setup_test_environment
    blob_service = services["blob_service"]
    queue_service = services["queue_service"]
    files_repository = services["files_repository"]
    
    # Step 1: Generate a unique ID for this test
    file_id = str(uuid.uuid4())
    user_id = "test-user-id"
    original_filename = os.path.basename(TEST_JD_FILE_PATH)
    
    # Step 2: Read the test file
    logger.info(f"Reading test file: {TEST_JD_FILE_PATH}")
    with open(TEST_JD_FILE_PATH, "rb") as file:
        file_content = file.read()
    
    # Step 3: Upload the file to blob storage
    logger.info(f"Uploading file to blob storage: {file_id}")
    blob_name = f"{file_id}_{original_filename}"
    blob_url = blob_service.upload_blob(TEST_CONTAINER_NAME, blob_name, file_content)
    
    # Verify the file was uploaded
    assert blob_service.blob_exists(TEST_CONTAINER_NAME, blob_name), "File was not uploaded to blob storage"
    
    # Step 4: Create a file record in the database
    logger.info(f"Creating file record in database: {file_id}")
    file_data = {
        "id": file_id,
        "user_id": user_id,
        "filename": original_filename,
        "blob_name": blob_name,
        "url": blob_url,
        "status": FileStatus.UPLOADED,
        "status_message": "File uploaded successfully"
    }
    file_record = files_repository.upsert_file(file_data)
    
    # The ID might have changed during upsert, so use the returned ID
    file_id = str(file_record.id)
    logger.info(f"File record created with ID: {file_id}")
    
    # Step 5: Create a queue message for processing the file
    logger.info(f"Creating queue message for file processing: {file_id}")
    request = FileProcessingRequest(
        id=file_id,
        user_id=user_id,
        filename=blob_name,
        url=blob_url,
        type=None  # Let the AI determine the file type
    )

    # Create a mock queue message
    # Convert UUID to string for JSON serialization
    request_dict = request.model_dump()
    request_dict["id"] = str(request_dict["id"])  # Convert UUID to string
    logger.info(f"Request dict: {request_dict}")
    message = MockQueueMessage(json.dumps(request_dict))
    
    # Step 6: Process the file
    logger.info(f"Processing file: {file_id}")
    logger.info(f"Blob name: {blob_name}")
    logger.info(f"Container name: {TEST_CONTAINER_NAME}")
    logger.info(f"Blob exists: {blob_service.blob_exists(TEST_CONTAINER_NAME, blob_name)}")
    try:
        # Set the container name in the environment for the file processing function
        os.environ["BLOB_CONTAINER_NAME"] = TEST_CONTAINER_NAME
        _process_file_impl(message)
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise
    
    # Step 7: Wait for processing to complete (up to 60 seconds)
    logger.info(f"Waiting for file processing to complete: {file_id}")
    max_wait_time = 60  # seconds
    wait_interval = 2   # seconds
    elapsed_time = 0
    processed_file = None
    
    while elapsed_time < max_wait_time:
        try:
            processed_file = files_repository.get_file(file_id, user_id)
            logger.info(f"File status: {processed_file.status} - {processed_file.status_message}")
            if processed_file.status in [FileStatus.COMPLETED, FileStatus.ERROR]:
                break
        except Exception as e:
            logger.error(f"Error getting file status: {e}")
        
        time.sleep(wait_interval)
        elapsed_time += wait_interval
    
    # Step 8: Verify the file was processed correctly
    assert processed_file is not None, "File record not found after processing"
    assert processed_file.status == FileStatus.COMPLETED, f"File processing failed: {processed_file.status_message}"
    
    # Verify file analysis results
    assert processed_file.document_analysis is not None, "Document analysis is missing"
    assert processed_file.type is not None, "Document type was not detected"
    
    # Log the final status
    logger.info(f"File processing completed successfully. File type: {processed_file.type}")
    logger.info(f"Document analysis: {processed_file.document_analysis}")
    
    # Clean up
    blob_service.delete_blob(TEST_CONTAINER_NAME, blob_name)
    files_repository.delete_file(user_id, file_id)
    
    return processed_file

@pytest.mark.external_services
def test_complete_e2e_flow_with_matching(setup_test_environment):
    """
    Complete end-to-end test including file upload, processing, and matching.
    
    This test:
    1. Uploads a JD file via HTTP API
    2. Uploads a CV file via HTTP API  
    3. Verifies both files are processed successfully
    4. Checks that matching is performed
    5. Validates the matching results via HTTP API
    """
    services = setup_test_environment
    blob_service = services["blob_service"]
    queue_service = services["queue_service"]
    files_repository = services["files_repository"]
    
    # Generate a unique user ID for this test
    user_id = f"test-user-{uuid.uuid4()}"
    
    # Upload JD file 
    logger.info(f"Uploading JD file for testing")
    with open(TEST_JD_FILE_PATH, "rb") as file:
        jd_content = file.read()
    
    jd_filename = os.path.basename(TEST_JD_FILE_PATH)
    jd_blob_name = f"{uuid.uuid4()}_{jd_filename}"
    jd_blob_url = blob_service.upload_blob(TEST_CONTAINER_NAME, jd_blob_name, jd_content)
    
    jd_file_data = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "filename": jd_filename,
        "type": FileType.JD,
        "blob_name": jd_blob_name,
        "url": jd_blob_url,
        "status": FileStatus.UPLOADED,
        "status_message": "File uploaded successfully"
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
        type=FileType.JD
    )
    jd_request_dict = jd_request.model_dump()
    jd_request_dict["id"] = str(jd_request_dict["id"])
    jd_message = MockQueueMessage(json.dumps(jd_request_dict))
    
    # Process the JD file
    logger.info(f"Processing JD file: {jd_file_id}")
    os.environ["BLOB_CONTAINER_NAME"] = TEST_CONTAINER_NAME
    _process_file_impl(jd_message)
    
    # Wait for JD processing to complete
    logger.info(f"Waiting for JD file processing to complete")
    max_wait_time = 60  # seconds
    wait_interval = 2   # seconds
    elapsed_time = 0
    processed_jd = None
    
    while elapsed_time < max_wait_time:
        processed_jd = files_repository.get_file(jd_file_id, user_id)
        logger.info(f"JD file status: {processed_jd.status} - {processed_jd.status_message}")
        if processed_jd.status in [FileStatus.COMPLETED, FileStatus.ERROR]:
            break
        time.sleep(wait_interval)
        elapsed_time += wait_interval
    
    # Verify JD file was processed correctly
    assert processed_jd is not None, "JD file record not found after processing"
    assert processed_jd.status == FileStatus.COMPLETED, f"JD file processing failed: {processed_jd.status_message}"
    assert processed_jd.type == FileType.JD, "JD file type was not detected correctly"
    
    # Now upload and process the CV file
    logger.info(f"Uploading CV file for testing")
    with open(TEST_CV_FILE_PATH, "rb") as file:
        cv_content = file.read()
    
    cv_filename = os.path.basename(TEST_CV_FILE_PATH)
    cv_blob_name = f"{uuid.uuid4()}_{cv_filename}"
    cv_blob_url = blob_service.upload_blob(TEST_CONTAINER_NAME, cv_blob_name, cv_content)
    
    cv_file_data = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "filename": cv_filename,
        "type": FileType.CV,
        "blob_name": cv_blob_name,
        "url": cv_blob_url,
        "status": FileStatus.UPLOADED,
        "status_message": "File uploaded successfully"
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
        type=FileType.CV
    )
    cv_request_dict = cv_request.model_dump()
    cv_request_dict["id"] = str(cv_request_dict["id"])
    cv_message = MockQueueMessage(json.dumps(cv_request_dict))
    
    # Process the CV file
    logger.info(f"Processing CV file: {cv_file_id}")
    _process_file_impl(cv_message)
    
    # Wait for CV processing to complete
    logger.info(f"Waiting for CV file processing to complete")
    elapsed_time = 0
    processed_cv = None
    
    while elapsed_time < max_wait_time:
        processed_cv = files_repository.get_file(cv_file_id, user_id)
        logger.info(f"CV file status: {processed_cv.status} - {processed_cv.status_message}")
        if processed_cv.status in [FileStatus.COMPLETED, FileStatus.ERROR]:
            break
        time.sleep(wait_interval)
        elapsed_time += wait_interval
    
    # Verify CV file was processed correctly
    assert processed_cv is not None, "CV file record not found after processing"
    assert processed_cv.status == FileStatus.COMPLETED, f"CV file processing failed: {processed_cv.status_message}"
    assert processed_cv.type == FileType.CV, "CV file type was not detected correctly"
    
    # Wait for matching to complete (check for matching results)
    logger.info(f"Waiting for matching to complete")
    elapsed_time = 0
    has_matching_results = False
    
    # Instead of directly accessing the matching results, let's call the HTTP API
    while elapsed_time < max_wait_time * 2:  # Matching may take longer
        try:
            # Try to get matching results for CV file
            results_url = f"{FUNCTION_API_BASE_URL}/results?file_id={cv_file_id}&file_type=CV"
            response = requests.get(results_url)
            
            if response.status_code == 200:
                results_data = response.json()
                if results_data and results_data.get('results') and len(results_data['results']) > 0:
                    logger.info(f"Found matching results: {results_data}")
                    has_matching_results = True
                    break
            
            # Also try with JD file
            results_url = f"{FUNCTION_API_BASE_URL}/results?file_id={jd_file_id}&file_type=JD"
            response = requests.get(results_url)
            
            if response.status_code == 200:
                results_data = response.json()
                if results_data and results_data.get('results') and len(results_data['results']) > 0:
                    logger.info(f"Found matching results: {results_data}")
                    has_matching_results = True
                    break
            
            logger.info(f"Waiting for matching results... ({elapsed_time}s)")
            time.sleep(wait_interval)
            elapsed_time += wait_interval
            
        except Exception as e:
            logger.error(f"Error checking matching results: {e}")
            time.sleep(wait_interval)
            elapsed_time += wait_interval
    
    # Verify matching results were created
    assert has_matching_results, "No matching results found after waiting"
    
    # Clean up
    logger.info("Cleaning up test resources")
    blob_service.delete_blob(TEST_CONTAINER_NAME, jd_blob_name)
    blob_service.delete_blob(TEST_CONTAINER_NAME, cv_blob_name)
    files_repository.delete_file(user_id, jd_file_id)
    files_repository.delete_file(user_id, cv_file_id)
    
    logger.info("Test completed successfully")
    
    return {
        "jd_file": processed_jd,
        "cv_file": processed_cv
    }

if __name__ == "__main__":
    """Run the UAT test directly."""
    logging.basicConfig(level=logging.INFO)
    
    # Call pytest programmatically
    pytest.main(["-xvs", __file__]) 