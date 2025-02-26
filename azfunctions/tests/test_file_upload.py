import json
from unittest import mock
import azure.functions as func
from uuid import uuid4
import os
from pathlib import Path
import pytest
from azure.cosmos import CosmosClient
from dotenv import load_dotenv
import base64
import azure.core.exceptions
import re
from unittest.mock import MagicMock
from shared.queue_service import QueueService
from shared.mock_queue_service import MockQueueService
from shared.blob_service import FilesBlobService
from shared.files_repository import FilesRepository

# add project root to sys.path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from file_upload.file_upload import _files_upload
from shared.models import FileMetadataDb, FileType
from shared.user_repository import UserRepository
from users.models import UserDb

# Load test environment variables
load_dotenv(Path(__file__).parent / ".env.test")

# Constants for testing
TEST_CONTAINER_NAME = "test-resume-match-pro-files"

# Mock classes for testing
class MockStream:
    def __init__(self, content=b'test content'):
        self._content = content
        self._position = 0

    def read(self, *args):
        if self._position < len(self._content):
            content = self._content[self._position:]
            self._position = len(self._content)
            return content
        return b''

    def seek(self, position):
        self._position = position

class MockFile:
    def __init__(self, filename, content=b'test content'):
        self.filename = filename
        self._content = content
        self._position = 0

    def read(self, *args):
        if self._position < len(self._content):
            content = self._content[self._position:]
            self._position = len(self._content)
            return content
        return b''

    def seek(self, position):
        self._position = position

class MockHttpRequest(func.HttpRequest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._files = {}
        self._form = {}
        self._headers = {}
    
    @property
    def files(self):
        return self._files
        
    @files.setter
    def files(self, value):
        self._files = value
        
    @property
    def form(self):
        return self._form
        
    @form.setter
    def form(self, value):
        self._form = value

    @property
    def headers(self):
        return self._headers
    
    @headers.setter
    def headers(self, value):
        self._headers = value

class MockBytesFile(bytes):
    def __new__(cls, content, headers):
        obj = super().__new__(cls, content)
        obj._headers = headers
        obj._content = content
        return obj
    
    @property
    def headers(self):
        return self._headers
    
    @property
    def filename(self):
        content_disp = self._headers.get('Content-Disposition', '')
        m = re.search('filename="([^"]+)"', content_disp)
        if m:
            return m.group(1)
        return None
    
    def read(self, *args):
        return self._content

class MockFiles:
    def __init__(self, files):
        self._files = files
    def getlist(self, key):
        return self._files.get(key, [])
    def get(self, key, default=None):
        return self._files.get(key, default)

def create_mock_b2c_token(user_id: str) -> str:
    claims = {
        "claims": [
            {
                "typ": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier",
                "val": user_id
            }
        ]
    }
    return base64.b64encode(json.dumps(claims).encode()).decode()

@pytest.fixture
def repository():
    # Create a Cosmos DB client and initialize the repository
    client = CosmosClient(
        url=os.getenv("COSMOS_DB_URL"),
        credential=os.getenv("COSMOS_DB_KEY"),
        connection_verify=False  # Skip SSL verification for emulator
    )
    # Create database if not exists
    database = client.create_database_if_not_exists(os.getenv("COSMOS_DB_DATABASE"))
    return FilesRepository(database)

@pytest.fixture
def user_repository():
    # Create a Cosmos DB client and initialize the repository
    client = CosmosClient(
        url=os.getenv("COSMOS_DB_URL"),
        credential=os.getenv("COSMOS_DB_KEY"),
        connection_verify=False  # Skip SSL verification for emulator
    )
    # Create database if not exists
    database = client.create_database_if_not_exists(os.getenv("COSMOS_DB_DATABASE"))
    return UserRepository(database)

@pytest.fixture
def blob_service():
    mock_blob_service = MagicMock()
    mock_blob_service.container_name = TEST_CONTAINER_NAME
    mock_blob_service.blob_service_client = MagicMock()
    mock_blob_service.blob_service_client.create_container.return_value = None
    mock_blob_service.upload_blob.return_value = "https://example.com/test-blob"
    
    # Track uploaded blobs
    uploaded_blobs = set()
    def mock_upload_blob(container_name, filename, content):
        uploaded_blobs.add((container_name, filename))
        return "https://example.com/test-blob"
    def mock_blob_exists(container_name, filename):
        return (container_name, filename) in uploaded_blobs
    
    mock_blob_service.upload_blob.side_effect = mock_upload_blob
    mock_blob_service.blob_exists.side_effect = mock_blob_exists
    return mock_blob_service

# add pytest fixture to clean up data before each test
@pytest.fixture(autouse=True)
def cleanup(repository, user_repository, blob_service):
    # Clean up before test
    repository.delete_all()
    try:
        user = user_repository.get_user("test-user-123")
        if user:
            user_repository.container.delete_item(user.id, partition_key=user.userId)
    except:
        pass
    
    # Clean up blob storage
    container_client = blob_service.blob_service_client.get_container_client(TEST_CONTAINER_NAME)
    blobs = container_client.list_blobs()
    for blob in blobs:
        container_client.delete_blob(blob.name)
    
    yield  # This is where the test runs
    
    # Clean up after test
    repository.delete_all()
    try:
        user = user_repository.get_user("test-user-123")
        if user:
            user_repository.container.delete_item(user.id, partition_key=user.userId)
    except:
        pass
    
    # Clean up blob storage
    blobs = container_client.list_blobs()
    for blob in blobs:
        container_client.delete_blob(blob.name)

@pytest.fixture
def test_user(user_repository) -> UserDb:
    user = UserDb(
        userId="test-user-123",
        email="test@example.com",
        name="Test User",
        filesLimit=2,
        filesCount=0
    )
    return user_repository.create_user(user.model_dump())

def test_file_upload_success(repository, user_repository, blob_service, test_user, monkeypatch):
    # Mock QueueService
    monkeypatch.setattr('file_upload.file_upload.QueueService', DummyQueueService)
    
    # Create mock file
    filename = f'test_{uuid4()}.pdf'
    mock_file = MockFile(filename)
    
    # Create request
    req = MockHttpRequest(
        method='POST',
        url='/api/files/upload',
        params={},
        body=None
    )
    req.files = MockFiles({'content': [mock_file]})
    req.form = {'type': 'CV'}
    req.headers = {'X-MS-CLIENT-PRINCIPAL': create_mock_b2c_token(test_user.userId)}
    
    # Override container name for test
    original_container = blob_service.container_name
    blob_service.container_name = TEST_CONTAINER_NAME
    
    try:
        # Call the function
        response = _files_upload(req, blob_service, repository, user_repository)
        
        # Print error details if status code is not 200
        if response.status_code != 200:
            error_body = json.loads(response.get_body())
            print(f"Error response: {error_body}")
        
        # Assert response
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.get_body()}"
        result = json.loads(response.get_body())
        assert len(result['files']) == 1
        assert result['files'][0]['filename'] == filename
        
        # Verify file was saved
        files = repository.get_files_from_db(test_user.userId)
        assert len(files) == 1
        assert files[0].filename == filename
        
        # Verify file exists in blob storage
        assert blob_service.blob_exists(TEST_CONTAINER_NAME, filename)
        
        # Verify user's file count was incremented
        updated_user = user_repository.get_user(test_user.userId)
        assert updated_user.filesCount == 1
    finally:
        # Restore original container name
        blob_service.container_name = original_container

def test_file_upload_raw_bytes(repository, user_repository, blob_service, test_user):
    # Create mock file as raw bytes
    filename = f'test_{uuid4()}.pdf'
    content = b'test content'
    
    # Create request
    req = MockHttpRequest(
        method='POST',
        url='/api/files/upload',
        params={},
        body=None
    )
    req.files = MockFiles({'content': [content]})
    req.form = {
        'type': 'CV',
        'filename': filename
    }
    req.headers = {'X-MS-CLIENT-PRINCIPAL': create_mock_b2c_token(test_user.userId)}
    
    # Override container name for test
    original_container = blob_service.container_name
    blob_service.container_name = TEST_CONTAINER_NAME
    
    try:
        # Call the function
        response = _files_upload(req, blob_service, repository, user_repository)
        
        # For raw bytes branch, expected status code is 400 because no filename is extracted
        assert response.status_code == 400
        error_response = json.loads(response.get_body())
        assert "Invalid request: Filename not provided" == error_response
    finally:
        # Restore original container name
        blob_service.container_name = original_container

def test_file_upload_raw_bytes_missing_filename(repository, user_repository, blob_service, test_user):
    # Create mock file as raw bytes
    content = b'test content'
    
    # Create request without filename
    req = MockHttpRequest(
        method='POST',
        url='/api/files/upload',
        params={},
        body=None
    )
    req.files = MockFiles({'content': [content]})
    req.form = {'type': 'CV'}  # No filename provided
    req.headers = {'X-MS-CLIENT-PRINCIPAL': create_mock_b2c_token(test_user.userId)}
    
    # Call the function
    response = _files_upload(req, blob_service, repository, user_repository)
    
    # Assert response
    assert response.status_code == 400
    error_response = json.loads(response.get_body())
    assert "Invalid request: Filename not provided" == error_response

def test_file_upload_limit_reached(repository, user_repository, blob_service, test_user, monkeypatch):
    # Mock QueueService
    monkeypatch.setattr('file_upload.file_upload.QueueService', DummyQueueService)
    
    # Override container name for test
    original_container = blob_service.container_name
    blob_service.container_name = TEST_CONTAINER_NAME
    
    try:
        # First, upload files up to the limit
        for i in range(test_user.filesLimit):
            mock_file = MockFile(f'test_{i}_{uuid4()}.pdf')
            req = MockHttpRequest(
                method='POST',
                url='/api/files/upload',
                params={},
                body=None
            )
            req.files = MockFiles({'content': [mock_file]})
            req.form = {'type': 'CV'}
            req.headers = {'X-MS-CLIENT-PRINCIPAL': create_mock_b2c_token(test_user.userId)}
            response = _files_upload(req, blob_service, repository, user_repository)
            assert response.status_code == 200, f"Failed to upload file {i}: {response.get_body()}"
        
        # Try to upload one more file
        mock_file = MockFile(f'test_extra_{uuid4()}.pdf')
        req = MockHttpRequest(
            method='POST',
            url='/api/files/upload',
            params={},
            body=None
        )
        req.files = MockFiles({'content': [mock_file]})
        req.form = {'type': 'CV'}
        req.headers = {'X-MS-CLIENT-PRINCIPAL': create_mock_b2c_token(test_user.userId)}
        
        # Call the function
        response = _files_upload(req, blob_service, repository, user_repository)
        
        # Assert response
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.get_body()}"
        error_response = json.loads(response.get_body())
        assert error_response == "File upload limit reached"
        
        # Verify no extra file was saved
        files = repository.get_files_from_db(test_user.userId)
        assert len(files) == test_user.filesLimit
        
        # Verify file wasn't uploaded to blob storage
        assert not blob_service.blob_exists(TEST_CONTAINER_NAME, mock_file.filename)
        
        # Verify user's file count wasn't incremented
        updated_user = user_repository.get_user(test_user.userId)
        assert updated_user.filesCount == test_user.filesLimit
    finally:
        # Restore original container name
        blob_service.container_name = original_container

def test_file_upload_user_not_found(repository, user_repository, blob_service, monkeypatch):
    # Mock QueueService
    monkeypatch.setattr('file_upload.file_upload.QueueService', DummyQueueService)
    
    # Create mock file
    mock_file = type('MockFile', (), {
        'filename': f'test_{uuid4()}.pdf',
        'stream': MockStream()
    })
    
    # Create request with non-existent user
    req = MockHttpRequest(
        method='POST',
        url='/api/files/upload',
        params={},
        body=None
    )
    req.files = MockFiles({'content': [mock_file]})
    req.form = {'type': 'CV'}
    req.headers = {'X-MS-CLIENT-PRINCIPAL': create_mock_b2c_token('non-existent-user')}
    
    # Override container name for test
    original_container = blob_service.container_name
    blob_service.container_name = TEST_CONTAINER_NAME
    
    try:
        # Call the function
        response = _files_upload(req, blob_service, repository, user_repository)
        
        # Assert response
        assert response.status_code == 404
        error_response = json.loads(response.get_body())
        assert "User not found" in error_response
        
        # Verify no file was saved
        files = repository.get_files_from_db('non-existent-user')
        assert len(files) == 0
        
        # Verify file wasn't uploaded to blob storage
        assert not blob_service.blob_exists(TEST_CONTAINER_NAME, mock_file.filename)
    finally:
        # Restore original container name
        blob_service.container_name = original_container

def test_file_upload_missing_claims(repository, user_repository, blob_service):
    # Create mock file
    mock_file = type('MockFile', (), {
        'filename': f'test_{uuid4()}.pdf',
        'stream': MockStream()
    })
    
    # Create request without claims
    req = MockHttpRequest(
        method='POST',
        url='/api/files/upload',
        params={},
        body=None
    )
    req.files = MockFiles({'content': [mock_file]})
    req.form = {'type': 'CV'}
    # No headers set - missing claims
    
    # Call the function
    response = _files_upload(req, blob_service, repository, user_repository)
    
    # Assert response
    assert response.status_code == 401
    error_response = json.loads(response.get_body())
    assert error_response == "Unauthorized - Missing user claims"

def test_file_upload_no_files(repository, user_repository, blob_service, test_user):
    # Create request without files
    req = MockHttpRequest(
        method='POST',
        url='/api/files/upload',
        params={},
        body=None
    )
    req.files = {}  # No files
    req.form = {'type': 'CV'}
    req.headers = {'X-MS-CLIENT-PRINCIPAL': create_mock_b2c_token(test_user.userId)}
    
    # Call the function
    response = _files_upload(req, blob_service, repository, user_repository)
    
    # Assert response
    assert response.status_code == 400
    error_response = json.loads(response.get_body())
    assert error_response == "Invalid request: No files provided"
    
    # Verify no file was saved
    files = repository.get_files_from_db(test_user.userId)
    assert len(files) == 0
    
    # Verify user's file count wasn't changed
    updated_user = user_repository.get_user(test_user.userId)
    assert updated_user.filesCount == 0

def test_file_upload_with_content_disposition(repository, user_repository, blob_service, test_user, monkeypatch):
    # Mock QueueService
    monkeypatch.setattr('file_upload.file_upload.QueueService', MockQueueService)
    
    # Create mock file
    filename = "CV_Gleb F.-Fullstack_Developer.pdf"
    mock_file = MockBytesFile(b'test content', {'Content-Disposition': f'form-data; name="content"; filename="{filename}"'})
    
    # Create request
    req = MockHttpRequest(
        method='POST',
        url='/api/files/upload',
        params={},
        body=None
    )
    req.files = MockFiles({'content': [mock_file]})
    req.form = {'type': 'CV'}
    req.headers = {'X-MS-CLIENT-PRINCIPAL': create_mock_b2c_token(test_user.userId)}
    
    # Call the function
    response = _files_upload(req, blob_service, repository, user_repository)
    
    # Assert response
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.get_body()}"
    result = json.loads(response.get_body())
    assert len(result['files']) == 1
    assert result['files'][0]['filename'] == filename
    
    # Verify file was saved in repository
    files = repository.get_files_from_db(test_user.userId)
    assert len(files) == 1
    assert files[0].filename == filename
    
    # Verify file exists in blob storage
    assert blob_service.blob_exists(TEST_CONTAINER_NAME, filename)
    
    # Verify user's file count was incremented
    updated_user = user_repository.get_user(test_user.userId)
    assert updated_user.filesCount == 1

def test_file_upload_with_form_data_boundary(repository, user_repository, blob_service, test_user):
    # Create request with exact same format as the cURL request
    filename = "CV_Gleb F.-Fullstack_Developer.pdf"
    content = b'test content'  # In real request this would be PDF content
    
    # Create request
    req = MockHttpRequest(
        method='POST',
        url='/api/files/upload',
        params={},
        body=None
    )
    
    # Set up headers exactly as in cURL request
    req.headers = {
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,ar;q=0.6',
        'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundaryPWWfyszh0L8W2KB1',
        'Origin': 'https://app.dev.resumematch.pro',
        'Referer': 'https://app.dev.resumematch.pro/',
        'X-MS-CLIENT-PRINCIPAL': create_mock_b2c_token(test_user.userId)
    }
    
    # Set up form data exactly as in cURL request
    mock_file = MockFile(filename, content)
    req.files = MockFiles({'content': [mock_file]})
    req.form = {'type': 'CV'}
    
    # Override container name for test
    original_container = blob_service.container_name
    blob_service.container_name = TEST_CONTAINER_NAME
    
    try:
        # Call the function
        response = _files_upload(req, blob_service, repository, user_repository)
        
        # Assert response
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.get_body()}"
        result = json.loads(response.get_body())
        assert len(result['files']) == 1
        assert result['files'][0]['filename'] == filename
        assert result['files'][0]['type'] == 'CV'
        
        # Verify file was saved
        files = repository.get_files_from_db(test_user.userId)
        assert len(files) == 1
        assert files[0].filename == filename
        
        # Verify file exists in blob storage
        assert blob_service.blob_exists(TEST_CONTAINER_NAME, filename)
        
        # Verify user's file count was incremented
        updated_user = user_repository.get_user(test_user.userId)
        assert updated_user.filesCount == 1
    finally:
        # Restore original container name
        blob_service.container_name = original_container

class DummyQueueService:
    def __init__(self, connection_string=None):
        pass

    def create_queue_if_not_exists(self, queue_name):
        pass

    def send_message(self, queue_name, message):
        pass

def test_file_upload_bytes_with_content_disposition():
    # Setup dummy dependencies
    repository = DummyFilesRepository()
    user_repository = DummyUserRepository()
    blob_service = DummyBlobService()
    test_user = DummyTestUser('12345')

    # Simulate a file upload request where the file is passed as raw bytes with a Content-Disposition header
    filename = "Павел _ Lead Product Manager.pdf"
    content = b'test content'
    headers = {"Content-Disposition": f'form-data; name="content"; filename="{filename}"'}
    mock_bytes = MockBytesFile(content, headers)

    req = MockHttpRequest(
        method='POST',
        url='/api/files/upload',
        params={},
        body=None
    )
    # Set req.files to contain our mock_bytes object as a list under the key 'content'
    req.files = {"content": [mock_bytes]}
    # Provide form data without an explicit 'filename'
    req.form = {"user_id": test_user.userId, "type": "CV"}
    req.headers = {"X-MS-CLIENT-PRINCIPAL": create_mock_b2c_token(test_user.userId)}

    # Call the file upload function
    response = _files_upload(req, blob_service, repository, user_repository)

    # We expect a 400 error response because the filename extraction from raw bytes fails
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    # The response body is a JSON string; load it
    body = response.get_body().decode('utf-8') if hasattr(response, 'get_body') else response._body
    error_response = json.loads(body)
    assert error_response == "Invalid request: Filename not provided", f"Unexpected error response: {error_response}"

# Dummy implementations for dependencies
class DummyFilesRepository:
    def upsert_file(self, file_metadata):
        # Return a dummy file metadata object with required attributes
        return DummyFileMetadata(file_metadata)

class DummyFileMetadata:
    def __init__(self, file_metadata):
        self.filename = file_metadata.get('filename')
        self.type = file_metadata.get('type')
        self.user_id = file_metadata.get('user_id')
        self.url = 'http://dummyurl'

    def model_dump(self, mode=None):
        return {'filename': self.filename, 'type': self.type, 'user_id': self.user_id, 'url': self.url}

class DummyUserRepository:
    def can_upload_file(self, user_id):
        return True

    def increment_files_count(self, user_id):
        pass

class DummyBlobService:
    container_name = 'dummy-container'

    def upload_blob(self, container_name, filename, content):
        return 'http://dummyurl'

class DummyTestUser:
    def __init__(self, user_id):
        self.userId = user_id

# Simple main to run the test if executed directly
if __name__ == '__main__':
    test_file_upload_bytes_with_content_disposition()
    print("Test completed successfully") 