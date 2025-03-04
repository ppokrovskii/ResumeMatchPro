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
from unittest.mock import MagicMock, patch
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

# OPTIMIZATION: Use mock repository instead of real Cosmos DB
@pytest.fixture
def repository():
    # Create a mock repository with the necessary methods
    mock_repo = MagicMock()
    mock_repo.delete_all = MagicMock(return_value=None)
    mock_repo.upsert_file = MagicMock(side_effect=lambda file_metadata: FileMetadataDb(**file_metadata))
    return mock_repo

# OPTIMIZATION: Use mock user repository instead of real Cosmos DB
@pytest.fixture
def user_repository():
    # Create a mock user repository
    mock_user_repo = MagicMock()
    mock_user_repo.get_user = MagicMock(return_value=UserDb(
        userId="test-user-123",
        email="test@example.com",
        name="Test User",
        filesLimit=2,
        filesCount=0
    ))
    mock_user_repo.can_upload_file = MagicMock(return_value=True)
    mock_user_repo.increment_files_count = MagicMock(return_value=None)
    return mock_user_repo

@pytest.fixture
def blob_service():
    mock_blob_service = MagicMock()
    mock_blob_service.container_name = TEST_CONTAINER_NAME
    mock_blob_service.blob_service_client = MagicMock()
    mock_blob_service.blob_service_client.create_container.return_value = None
    mock_blob_service.upload_blob.return_value = "https://example.com/test-blob"
    
    # OPTIMIZATION: Simplify blob tracking with a dictionary
    uploaded_blobs = set()
    def mock_upload_blob(container_name, filename, content):
        uploaded_blobs.add((container_name, filename))
        return "https://example.com/test-blob"
    def mock_blob_exists(container_name, filename):
        return (container_name, filename) in uploaded_blobs
    
    mock_blob_service.upload_blob.side_effect = mock_upload_blob
    mock_blob_service.blob_exists.side_effect = mock_blob_exists
    
    # OPTIMIZATION: Mock blob container client
    mock_container_client = MagicMock()
    mock_container_client.list_blobs.return_value = []
    mock_container_client.delete_blob = MagicMock()
    mock_blob_service.blob_service_client.get_container_client.return_value = mock_container_client
    
    return mock_blob_service

# OPTIMIZATION: Remove real cleanup operations and use mocks only
@pytest.fixture
def test_user():
    return UserDb(
        userId="test-user-123",
        email="test@example.com",
        name="Test User",
        filesLimit=2,
        filesCount=0
    )

# OPTIMIZATION: Create a mock queue service fixture
@pytest.fixture
def queue_service():
    mock_queue = MagicMock()
    mock_queue.create_queue_if_not_exists = MagicMock()
    mock_queue.send_message = MagicMock()
    return mock_queue

def test_file_upload_success(repository, user_repository, blob_service, test_user, monkeypatch):
    # OPTIMIZATION: Use the queue_service fixture instead of monkeypatching
    queue_service = MagicMock()
    queue_service.create_queue_if_not_exists = MagicMock()
    queue_service.send_message = MagicMock()
    monkeypatch.setattr('file_upload.file_upload.QueueService', lambda connection_string=None: queue_service)
    
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
    
    # Test the function
    response = _files_upload(req, blob_service, repository, user_repository)
    
    # Assert
    assert response.status_code == 200
    response_body = json.loads(response.get_body())
    assert len(response_body["files"]) == 1
    assert response_body["files"][0]["filename"] == filename
    assert response_body["files"][0]["url"] == "https://example.com/test-blob"
    assert response_body["files"][0]["user_id"] == test_user.userId
    
    # Verify interactions
    blob_service.upload_blob.assert_called_once()
    repository.upsert_file.assert_called_once()
    user_repository.increment_files_count.assert_called_once_with(test_user.userId)
    queue_service.create_queue_if_not_exists.assert_called_once()
    queue_service.send_message.assert_called_once()

def test_file_upload_raw_bytes(repository, user_repository, blob_service, test_user):
    # OPTIMIZATION: Use patch instead of monkeypatching
    with patch('file_upload.file_upload.QueueService') as mock_queue_class:
        mock_queue = MagicMock()
        mock_queue_class.return_value = mock_queue
        
        # Create mock file as raw bytes
        filename = f'test_{uuid4()}.pdf'
        content = b'test content'
        headers = {'Content-Disposition': f'attachment; filename="{filename}"'}
        mock_file = MockBytesFile(content, headers)
        
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
        
        # Test the function
        response = _files_upload(req, blob_service, repository, user_repository)
        
        # Assert
        assert response.status_code == 200
        response_body = json.loads(response.get_body())
        assert len(response_body["files"]) == 1
        assert response_body["files"][0]["filename"] == filename
        assert response_body["files"][0]["url"] == "https://example.com/test-blob"
        assert response_body["files"][0]["user_id"] == test_user.userId

def test_file_upload_raw_bytes_missing_filename(repository, user_repository, blob_service, test_user):
    # OPTIMIZATION: Use patch instead of monkeypatching
    with patch('file_upload.file_upload.QueueService') as mock_queue_class:
        mock_queue = MagicMock()
        mock_queue_class.return_value = mock_queue
        
        # Create mock file as raw bytes without filename
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
        
        # Test the function
        response = _files_upload(req, blob_service, repository, user_repository)
        
        # Assert
        assert response.status_code == 400
        error_response = json.loads(response.get_body())
        assert "Invalid request: Filename not provided" == error_response

def test_file_upload_limit_reached(repository, user_repository, blob_service, test_user, monkeypatch):
    # OPTIMIZATION: Mock queue service
    queue_service = MagicMock()
    monkeypatch.setattr('file_upload.file_upload.QueueService', lambda connection_string=None: queue_service)
    
    # Configure user repository to indicate limit reached
    user_repository.can_upload_file.return_value = False
    
    # Create mock file
    filename = f'test_extra_{uuid4()}.pdf'
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
    
    # Test the function
    response = _files_upload(req, blob_service, repository, user_repository)
    
    # Assert
    assert response.status_code == 403
    error_response = json.loads(response.get_body())
    assert error_response["error"]["code"] == "FILE_UPLOAD_LIMIT_REACHED"
    assert "reached your file upload limit" in error_response["error"]["message"]
    
    # Verify interactions
    blob_service.upload_blob.assert_not_called()
    repository.upsert_file.assert_not_called()
    user_repository.increment_files_count.assert_not_called()

def test_file_upload_user_not_found(repository, user_repository, blob_service, monkeypatch):
    # OPTIMIZATION: Mock queue service
    queue_service = MagicMock()
    monkeypatch.setattr('file_upload.file_upload.QueueService', lambda connection_string=None: queue_service)
    
    # Configure user repository to simulate user not found
    def raise_value_error(*args, **kwargs):
        raise ValueError("User not found")
    user_repository.can_upload_file.side_effect = raise_value_error
    
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
    req.headers = {'X-MS-CLIENT-PRINCIPAL': create_mock_b2c_token('non-existent-user')}
    
    # Test the function
    response = _files_upload(req, blob_service, repository, user_repository)
    
    # Assert
    assert response.status_code == 404
    error_response = json.loads(response.get_body())
    assert error_response["error"]["code"] == "USER_NOT_FOUND"
    assert "User not found" in error_response["error"]["message"]
    
    # Verify interactions
    blob_service.upload_blob.assert_not_called()
    repository.upsert_file.assert_not_called()
    user_repository.increment_files_count.assert_not_called()

def test_file_upload_missing_claims(repository, user_repository, blob_service):
    # Create mock file
    filename = f'test_{uuid4()}.pdf'
    mock_file = MockFile(filename)
    
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
    
    # Test the function
    response = _files_upload(req, blob_service, repository, user_repository)
    
    # Assert
    assert response.status_code == 401
    error_response = json.loads(response.get_body())
    assert "Unauthorized - Missing user claims" == error_response
    
    # Verify interactions
    blob_service.upload_blob.assert_not_called()
    repository.upsert_file.assert_not_called()
    user_repository.increment_files_count.assert_not_called()

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
    
    # Test the function
    response = _files_upload(req, blob_service, repository, user_repository)
    
    # Assert
    assert response.status_code == 400
    error_response = json.loads(response.get_body())
    assert "Invalid request: No files provided" == error_response
    
    # Verify interactions
    blob_service.upload_blob.assert_not_called()
    repository.upsert_file.assert_not_called()
    user_repository.increment_files_count.assert_not_called()

def test_file_upload_with_content_disposition(repository, user_repository, blob_service, test_user, monkeypatch):
    # OPTIMIZATION: Mock queue service
    queue_service = MagicMock()
    monkeypatch.setattr('file_upload.file_upload.QueueService', lambda connection_string=None: queue_service)
    
    # Create mock file
    filename = "CV_Gleb F.-Fullstack_Developer.pdf"
    headers = {'Content-Disposition': f'form-data; name="content"; filename="{filename}"'}
    mock_file = MockBytesFile(b'test content', headers)
    
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
    
    # Test the function
    response = _files_upload(req, blob_service, repository, user_repository)
    
    # Assert
    assert response.status_code == 200
    response_body = json.loads(response.get_body())
    assert len(response_body["files"]) == 1
    assert response_body["files"][0]["filename"] == filename
    assert response_body["files"][0]["url"] == "https://example.com/test-blob"
    assert response_body["files"][0]["user_id"] == test_user.userId
    
    # Verify interactions
    blob_service.upload_blob.assert_called_once()
    repository.upsert_file.assert_called_once()
    user_repository.increment_files_count.assert_called_once_with(test_user.userId)
    queue_service.create_queue_if_not_exists.assert_called_once()
    queue_service.send_message.assert_called_once()

def test_file_upload_with_form_data_boundary(repository, user_repository, blob_service, test_user, monkeypatch):
    # OPTIMIZATION: Mock queue service
    queue_service = MagicMock()
    monkeypatch.setattr('file_upload.file_upload.QueueService', lambda connection_string=None: queue_service)
    
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
    
    # Test the function
    response = _files_upload(req, blob_service, repository, user_repository)
    
    # Assert
    assert response.status_code == 200
    response_body = json.loads(response.get_body())
    assert len(response_body["files"]) == 1
    assert response_body["files"][0]["filename"] == filename
    assert response_body["files"][0]["url"] == "https://example.com/test-blob"
    assert response_body["files"][0]["user_id"] == test_user.userId
    
    # Verify interactions
    blob_service.upload_blob.assert_called_once()
    repository.upsert_file.assert_called_once()
    user_repository.increment_files_count.assert_called_once_with(test_user.userId)
    queue_service.create_queue_if_not_exists.assert_called_once()
    queue_service.send_message.assert_called_once()

def test_file_upload_bytes_with_content_disposition(repository, user_repository, blob_service, test_user, monkeypatch):
    # OPTIMIZATION: Mock queue service
    queue_service = MagicMock()
    monkeypatch.setattr('file_upload.file_upload.QueueService', lambda connection_string=None: queue_service)
    
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
    req.files = MockFiles({"content": [mock_bytes]})
    # Provide form data with the type
    req.form = {"type": "CV"}
    req.headers = {"X-MS-CLIENT-PRINCIPAL": create_mock_b2c_token(test_user.userId)}

    # Test the function
    response = _files_upload(req, blob_service, repository, user_repository)

    # Assert
    assert response.status_code == 200
    response_body = json.loads(response.get_body())
    assert len(response_body["files"]) == 1
    assert response_body["files"][0]["filename"] == filename
    assert response_body["files"][0]["url"] == "https://example.com/test-blob"
    assert response_body["files"][0]["user_id"] == test_user.userId
    
    # Verify interactions
    blob_service.upload_blob.assert_called_once()
    repository.upsert_file.assert_called_once()
    user_repository.increment_files_count.assert_called_once_with(test_user.userId)
    queue_service.create_queue_if_not_exists.assert_called_once()
    queue_service.send_message.assert_called_once()

# OPTIMIZATION: Remove the dummy classes that are no longer needed
# The DummyQueueService can be kept for backward compatibility with other tests
# that might still use it 