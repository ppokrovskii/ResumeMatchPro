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
from pathlib import Path
from dotenv import load_dotenv
from azure.cosmos import CosmosClient

# Add parent directory to path so we can import the function app
current_dir = os.path.dirname(os.path.abspath(__file__))
azfunctions_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(azfunctions_dir)
sys.path.insert(0, azfunctions_dir)

# Load environment variables from test env file
load_dotenv(Path(azfunctions_dir) / "tests" / ".env.test")

from azfunctions.shared.blob_service import FilesBlobService
from azfunctions.shared.queue_service import QueueService
from azfunctions.shared.files_repository import FilesRepository
from azfunctions.shared.models import FileStatus, FileType
from azfunctions.file_processing.schemas import FileProcessingRequest
from azfunctions.file_processing.file_processing import _process_file_impl, _get_blob_service

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test constants
TEST_CONTAINER_NAME = "test-files"
PROCESSING_QUEUE_NAME = "processing-queue"
TEST_FILE_PATH = os.path.join(os.path.dirname(__file__), "test_data", "JD - iOS_Junior.docx")

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
    from azfunctions.file_processing import file_processing
    file_processing._get_blob_service = mock_get_blob_service
    
    # Ensure container exists
    container_client = blob_service.blob_service_client.get_container_client(TEST_CONTAINER_NAME)
    if not container_client.exists():
        container_client.create_container()
    
    # Create queue service and ensure queue exists
    queue_service = QueueService(connection_string=connection_string)
    queue_service.create_queue_if_not_exists(PROCESSING_QUEUE_NAME)
    
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
    original_filename = os.path.basename(TEST_FILE_PATH)
    
    # Step 2: Read the test file
    logger.info(f"Reading test file: {TEST_FILE_PATH}")
    with open(TEST_FILE_PATH, "rb") as file:
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

if __name__ == "__main__":
    """Run the UAT test directly."""
    logging.basicConfig(level=logging.INFO)
    
    # Call pytest programmatically
    pytest.main(["-xvs", __file__]) 