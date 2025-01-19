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

# add project root to sys.path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from user_files.user_files import _get_files, _delete_file
from user_files.models import UserFilesRequest, UserFilesResponse
from shared.models import FileMetadataDb, FileType
from shared.files_repository import FilesRepository
from shared.blob_service import FilesBlobService

# Load test environment variables
load_dotenv(Path(__file__).parent / ".env.test")

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
def blob_service():
    return FilesBlobService()

@pytest.fixture
def sample_file_content():
    return b"Test file content"

@pytest.fixture
def sample_file_metadata(repository, blob_service, sample_file_content):
    # Create a unique filename
    filename = f"test_file_{uuid4()}.txt"
    
    # Upload file to blob storage
    blob_url = blob_service.upload_blob(
        container_name="resume-match-pro-files",
        filename=filename,
        content=sample_file_content
    )
    
    # Create file metadata
    file_metadata = FileMetadataDb(
        filename=filename,
        type=FileType.CV,
        user_id="test-user-123",
        url=blob_url
    )
    
    # Save to database
    return repository.upsert_file(file_metadata.model_dump(mode="json"))

def test_delete_file_integration(repository, blob_service, sample_file_metadata):
    # Create mock B2C claims
    mock_claims = {
        "claims": [
            {"typ": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier", "val": "test-user-123"},
            {"typ": "name", "val": "Test User"},
            {"typ": "emails", "val": "test@example.com"}
        ]
    }
    encoded_claims = base64.b64encode(json.dumps(mock_claims).encode()).decode()
    
    # Create mock request with B2C headers
    req = func.HttpRequest(
        method='DELETE',
        url=f'/api/files/{sample_file_metadata.id}',
        route_params={'file_id': str(sample_file_metadata.id)},
        headers={
            'X-MS-CLIENT-PRINCIPAL': encoded_claims,
            'X-MS-CLIENT-PRINCIPAL-ID': 'test-user-123',
            'X-MS-CLIENT-PRINCIPAL-NAME': 'test@example.com'
        },
        body=None
    )
    
    # Call the delete function
    response = _delete_file(req, blob_service, repository)
    
    # Assert response
    assert response.status_code == 204
    assert response.get_body() == b''
    
    # Verify file is deleted from Cosmos DB
    assert repository.get_file_by_id('test-user-123', str(sample_file_metadata.id)) is None
    
    # Verify file is deleted from blob storage
    assert not blob_service.blob_exists(
        container_name="resume-match-pro-files",
        filename=sample_file_metadata.filename
    )

def test_get_files_logic():
    # Mock the repository
    mock_files_repository = mock.Mock()
    mock_files = [
        FileMetadataDb(
            id=uuid4(),
            filename="file1.txt",
            type=FileType.CV,
            user_id="123",
            url="https://file1.txt",
            text="Sample text 1"
        ),
        FileMetadataDb(
            id=uuid4(),
            filename="file2.txt",
            type=FileType.JD,
            user_id="123",
            url="https://file2.txt",
            text="Sample text 2"
        )
    ]
    mock_files_repository.get_files_from_db.return_value = mock_files

    # Create a mock HTTP request
    req = func.HttpRequest(
        method='GET',
        url='/api/files',
        params={'user_id': '123', 'type': 'CV'},
        body=None
    )

    # Call the function
    response = _get_files(req, mock_files_repository)

    # Assert the response
    assert response.status_code == 200
    result = json.loads(response.get_body())
    assert len(result['files']) == 2
    assert result['files'][0]['filename'] == 'file1.txt'
    assert result['files'][1]['filename'] == 'file2.txt'


def test_delete_file_logic():
    # Mock dependencies
    mock_files_repository = mock.Mock()
    mock_blob_service = mock.Mock()
    
    # Mock file metadata
    file_id = uuid4()
    mock_file = FileMetadataDb(
        id=file_id,
        filename="test.pdf",
        type=FileType.CV,
        user_id="user-123",
        url="https://test.pdf",
        text="Sample CV text"
    )
    
    # Setup repository mock
    mock_files_repository.get_file_by_id.return_value = mock_file
    mock_files_repository.delete_file.return_value = True
    
    # Create mock B2C claims
    mock_claims = {
        "claims": [
            {"typ": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier", "val": "user-123"},
            {"typ": "name", "val": "Test User"},
            {"typ": "emails", "val": "test@example.com"}
        ]
    }
    encoded_claims = base64.b64encode(json.dumps(mock_claims).encode()).decode()
    
    # Create mock request with B2C headers
    req = func.HttpRequest(
        method='DELETE',
        url=f'/api/files/{file_id}',
        route_params={'file_id': str(file_id)},
        headers={
            'X-MS-CLIENT-PRINCIPAL': encoded_claims,
            'X-MS-CLIENT-PRINCIPAL-ID': 'user-123',
            'X-MS-CLIENT-PRINCIPAL-NAME': 'test@example.com'
        },
        body=None
    )
    
    # Call the function
    response = _delete_file(req, mock_blob_service, mock_files_repository)
    
    # Assert response
    assert response.status_code == 204
    assert response.get_body() == b''
    
    # Verify calls
    mock_files_repository.get_file_by_id.assert_called_once_with('user-123', str(file_id))
    mock_blob_service.delete_blob.assert_called_once_with(
        container_name="resume-match-pro-files",
        filename="test.pdf"
    )
    mock_files_repository.delete_file.assert_called_once_with(user_id='user-123', file_id=str(file_id))


def test_delete_file_logic_not_found():
    # Mock dependencies
    mock_files_repository = mock.Mock()
    mock_blob_service = mock.Mock()
    
    # Setup repository mock to return None (file not found)
    mock_files_repository.get_file_by_id.return_value = None
    
    # Create mock B2C claims
    mock_claims = {
        "claims": [
            {"typ": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier", "val": "user-123"},
            {"typ": "name", "val": "Test User"},
            {"typ": "emails", "val": "test@example.com"}
        ]
    }
    encoded_claims = base64.b64encode(json.dumps(mock_claims).encode()).decode()
    
    # Create mock request with B2C headers
    req = func.HttpRequest(
        method='DELETE',
        url=f'/api/files/file-123',
        route_params={'file_id': 'file-123'},
        headers={
            'X-MS-CLIENT-PRINCIPAL': encoded_claims,
            'X-MS-CLIENT-PRINCIPAL-ID': 'user-123',
            'X-MS-CLIENT-PRINCIPAL-NAME': 'test@example.com'
        },
        body=None
    )
    
    # Call the function
    response = _delete_file(req, mock_blob_service, mock_files_repository)
    
    # Assert response
    assert response.status_code == 404
    error_response = json.loads(response.get_body())
    assert error_response['error'] == "File not found"
    
    # Verify no delete calls were made
    mock_blob_service.delete_blob.assert_not_called()
    mock_files_repository.delete_file.assert_not_called()


def test_delete_file_logic_missing_params():
    # Mock dependencies
    mock_files_repository = mock.Mock()
    mock_blob_service = mock.Mock()
    
    # Test missing file_id
    req1 = func.HttpRequest(
        method='DELETE',
        url='/api/files',
        route_params={},
        body=None
    )
    # Mock the get_claims method
    req1.get_claims = mock.Mock(return_value={'sub': 'user-123'})
    
    response = _delete_file(req1, mock_blob_service, mock_files_repository)
    assert response.status_code == 400
    error_response = json.loads(response.get_body())
    assert error_response['error'] == "file_id is required"
    
    # Verify no service calls were made
    mock_blob_service.assert_not_called()
    mock_files_repository.get_file_by_id.assert_not_called()
    mock_files_repository.delete_file.assert_not_called()


def test_delete_file_unauthorized():
    # Mock dependencies
    mock_files_repository = mock.Mock()
    mock_blob_service = mock.Mock()
    
    # Create mock request without claims header
    req = func.HttpRequest(
        method='DELETE',
        url='/api/files/file-123',
        route_params={'file_id': 'file-123'},
        headers={},
        body=None
    )
    
    # Call the function
    response = _delete_file(req, mock_blob_service, mock_files_repository)
    
    # Assert response
    assert response.status_code == 401
    error_response = json.loads(response.get_body())
    assert error_response['error'] == "Unauthorized - Missing user claims"
    
    # Verify no service calls were made
    mock_blob_service.assert_not_called()
    mock_files_repository.get_file_by_id.assert_not_called()
    mock_files_repository.delete_file.assert_not_called()


def test_delete_file_forbidden():
    # Mock dependencies
    mock_files_repository = mock.Mock()
    mock_blob_service = mock.Mock()
    
    # Mock file metadata with different user_id
    file_id = uuid4()
    mock_file = FileMetadataDb(
        id=file_id,
        filename="test.pdf",
        type=FileType.CV,
        user_id="different-user",
        url="https://test.pdf",
        text="Sample CV text"
    )
    
    # Setup repository mock
    mock_files_repository.get_file_by_id.return_value = mock_file
    
    # Create mock B2C claims
    mock_claims = {
        "claims": [
            {"typ": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier", "val": "user-123"},
            {"typ": "name", "val": "Test User"},
            {"typ": "emails", "val": "test@example.com"}
        ]
    }
    encoded_claims = base64.b64encode(json.dumps(mock_claims).encode()).decode()
    
    # Create mock request with B2C headers
    req = func.HttpRequest(
        method='DELETE',
        url=f'/api/files/{file_id}',
        route_params={'file_id': str(file_id)},
        headers={
            'X-MS-CLIENT-PRINCIPAL': encoded_claims,
            'X-MS-CLIENT-PRINCIPAL-ID': 'user-123',
            'X-MS-CLIENT-PRINCIPAL-NAME': 'test@example.com'
        },
        body=None
    )
    
    # Call the function
    response = _delete_file(req, mock_blob_service, mock_files_repository)
    
    # Assert response
    assert response.status_code == 403
    error_response = json.loads(response.get_body())
    assert error_response['error'] == "Unauthorized - You don't have permission to delete this file"
    
    # Verify no delete calls were made
    mock_blob_service.delete_blob.assert_not_called()
    mock_files_repository.delete_file.assert_not_called()