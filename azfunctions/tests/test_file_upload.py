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

# add project root to sys.path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from file_upload.file_upload import _files_upload
from shared.models import FileMetadataDb, FileType
from shared.files_repository import FilesRepository
from shared.blob_service import FilesBlobService
from shared.user_repository import UserRepository
from users.models import UserDb

# Load test environment variables
load_dotenv(Path(__file__).parent / ".env.test")

# Constants for testing
TEST_CONTAINER_NAME = "test-resume-match-pro-files"

# Mock classes for testing
class MockStream:
    def read(self, *args):
        return b'test content'

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
    service = FilesBlobService()
    # Create test container if it doesn't exist
    try:
        service.blob_service_client.create_container(TEST_CONTAINER_NAME)
    except azure.core.exceptions.ResourceExistsError:
        pass  # Container already exists, which is fine
    return service

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

def test_file_upload_success(repository, user_repository, blob_service, test_user):
    # Create mock file
    mock_file = type('MockFile', (), {
        'filename': f'test_{uuid4()}.pdf',
        'stream': MockStream()
    })
    
    # Create request
    req = MockHttpRequest(
        method='POST',
        url='/api/files/upload',
        params={},
        body=None
    )
    req.files = {'content': [mock_file]}
    req.form = {'type': 'CV'}
    req.headers = {'X-MS-CLIENT-PRINCIPAL': create_mock_b2c_token(test_user.userId)}
    
    # Override container name for test
    original_container = blob_service.container_name
    blob_service.container_name = TEST_CONTAINER_NAME
    
    try:
        # Call the function
        response = _files_upload(req, blob_service, repository, user_repository)
        
        # Assert response
        assert response.status_code == 200
        result = json.loads(response.get_body())
        assert len(result['files']) == 1
        assert result['files'][0]['filename'] == mock_file.filename
        
        # Verify file was saved
        files = repository.get_files_from_db(test_user.userId)
        assert len(files) == 1
        assert files[0].filename == mock_file.filename
        
        # Verify file exists in blob storage
        assert blob_service.blob_exists(TEST_CONTAINER_NAME, mock_file.filename)
        
        # Verify user's file count was incremented
        updated_user = user_repository.get_user(test_user.userId)
        assert updated_user.filesCount == 1
    finally:
        # Restore original container name
        blob_service.container_name = original_container

def test_file_upload_limit_reached(repository, user_repository, blob_service, test_user):
    # Override container name for test
    original_container = blob_service.container_name
    blob_service.container_name = TEST_CONTAINER_NAME
    
    try:
        # First, upload files up to the limit
        for i in range(test_user.filesLimit):
            mock_file = type('MockFile', (), {
                'filename': f'test_{i}_{uuid4()}.pdf',
                'stream': MockStream()
            })
            req = MockHttpRequest(
                method='POST',
                url='/api/files/upload',
                params={},
                body=None
            )
            req.files = {'content': [mock_file]}
            req.form = {'type': 'CV'}
            req.headers = {'X-MS-CLIENT-PRINCIPAL': create_mock_b2c_token(test_user.userId)}
            response = _files_upload(req, blob_service, repository, user_repository)
            assert response.status_code == 200
        
        # Try to upload one more file
        mock_file = type('MockFile', (), {
            'filename': f'test_extra_{uuid4()}.pdf',
            'stream': MockStream()
        })
        req = MockHttpRequest(
            method='POST',
            url='/api/files/upload',
            params={},
            body=None
        )
        req.files = {'content': [mock_file]}
        req.form = {'type': 'CV'}
        req.headers = {'X-MS-CLIENT-PRINCIPAL': create_mock_b2c_token(test_user.userId)}
        
        # Call the function
        response = _files_upload(req, blob_service, repository, user_repository)
        
        # Assert response
        assert response.status_code == 403
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

def test_file_upload_user_not_found(repository, user_repository, blob_service):
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
    req.files = {'content': [mock_file]}
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
    req.files = {'content': [mock_file]}
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
    assert error_response == "No files in request"
    
    # Verify no file was saved
    files = repository.get_files_from_db(test_user.userId)
    assert len(files) == 0
    
    # Verify user's file count wasn't changed
    updated_user = user_repository.get_user(test_user.userId)
    assert updated_user.filesCount == 0 