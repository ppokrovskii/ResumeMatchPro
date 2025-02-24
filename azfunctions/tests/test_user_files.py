import logging
import sys
import base64
import json
import os
import pytest
from uuid import uuid4
import azure.functions as func
from pathlib import Path
from dotenv import load_dotenv
from azure.cosmos import CosmosClient
from user_files.user_files import _get_file, _download_file
from azure.ai.formrecognizer import DocumentAnalysisClient
from user_files.user_files import _get_files, _delete_file, user_files_bp
from user_files.models import UserFilesRequest, UserFilesResponse
from shared.models import FileMetadataDb, FileType, DocumentPage, Line, TableCell, DocumentStyle
from shared.files_repository import FilesRepository
from shared.blob_service import FilesBlobService
from unittest import mock

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

# Ensure all loggers propagate to root
for name in logging.root.manager.loggerDict:
    logging.getLogger(name).propagate = True
    logging.getLogger(name).setLevel(logging.DEBUG)

# add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

# Load test environment variables
load_dotenv(Path(__file__).parent / ".env.test")

@pytest.fixture
def client():
    """Create a test client for the Azure Functions app."""
    from azure.functions import WsgiMiddleware
    from flask import Flask

    app = Flask(__name__)
    app.wsgi_app = WsgiMiddleware(user_files_bp.as_flask_app())
    app.config['TESTING'] = True
    return app.test_client()

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

    # Create mock B2C claims
    mock_claims = {
        "claims": [
            {"typ": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier", "val": "123"},
            {"typ": "name", "val": "Test User"},
            {"typ": "emails", "val": "test@example.com"}
        ]
    }
    encoded_claims = base64.b64encode(json.dumps(mock_claims).encode()).decode()

    # Create a mock HTTP request with B2C headers
    req = func.HttpRequest(
        method='GET',
        url='/api/files',
        params={'type': 'CV'},
        headers={
            'X-MS-CLIENT-PRINCIPAL': encoded_claims
        },
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

def create_mock_claims(user_id: str) -> str:
    claims = {"claims": [{
        "typ": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier",
        "val": user_id
    }]}
    return base64.b64encode(json.dumps(claims).encode()).decode()

def test_get_file_success(repository, sample_file_metadata):
    # Assume sample_file_metadata is a fixture providing a file metadata object with attributes id, user_id, filename, etc.
    user_id = sample_file_metadata.user_id
    file_id = sample_file_metadata.id
    client_principal = create_mock_claims(user_id)
    req = func.HttpRequest(
        method="GET",
        url=f"/api/files/{file_id}",
        body=None,
        params={},
        route_params={"file_id": file_id},
        headers={"X-MS-CLIENT-PRINCIPAL": client_principal}
    )
    
    resp = _get_file(req, repository)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = json.loads(resp.get_body().decode())
    assert data["filename"] == sample_file_metadata.filename, "Filename mismatch"

def test_get_file_missing_file_id(repository):
    user_id = "test_user"
    client_principal = create_mock_claims(user_id)
    req = func.HttpRequest(
        method="GET",
        url="/api/files/",
        body=None,
        params={},
        route_params={},  # Missing file_id
        headers={"X-MS-CLIENT-PRINCIPAL": client_principal}
    )
    resp = _get_file(req, repository)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
    data = json.loads(resp.get_body().decode())
    assert "file_id is required" in data.get("error", ""), "Missing error message for missing file_id"

def test_get_file_missing_claims(repository):
    file_id = "some_file_id"
    req = func.HttpRequest(
        method="GET",
        url=f"/api/files/{file_id}",
        body=None,
        params={},
        route_params={"file_id": file_id},
        headers={}  # Missing X-MS-CLIENT-PRINCIPAL header
    )
    resp = _get_file(req, repository)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
    data = json.loads(resp.get_body().decode())
    assert "Missing user claims" in data.get("error", ""), "Expected missing claims error message"

def test_get_file_not_found(repository):
    user_id = "test_user"
    file_id = "nonexistent_file"
    client_principal = create_mock_claims(user_id)
    req = func.HttpRequest(
        method="GET",
        url=f"/api/files/{file_id}",
        body=None,
        params={},
        route_params={"file_id": file_id},
        headers={"X-MS-CLIENT-PRINCIPAL": client_principal}
    )
    resp = _get_file(req, repository)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"
    data = json.loads(resp.get_body().decode())
    assert "File not found" in data.get("error", ""), "Expected file not found error message"

def test_get_file_unauthorized(repository, sample_file_metadata):
    # File exists but the authenticated user's id does not match the file's user_id
    file_id = sample_file_metadata.id
    different_user_id = "different_user"
    client_principal = create_mock_claims(different_user_id)
    req = func.HttpRequest(
        method="GET",
        url=f"/api/files/{file_id}",
        body=None,
        params={},
        route_params={"file_id": file_id},
        headers={"X-MS-CLIENT-PRINCIPAL": client_principal}
    )
    resp = _get_file(req, repository)
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}"
    data = json.loads(resp.get_body().decode())
    assert "don't have permission" in data.get("error", ""), "Expected unauthorized access error message"

def test_download_file_success(repository, blob_service, sample_file_metadata, sample_file_content):
    # Create mock B2C claims
    mock_claims = {
        "claims": [
            {"typ": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier", "val": sample_file_metadata.user_id}
        ]
    }
    encoded_claims = base64.b64encode(json.dumps(mock_claims).encode()).decode()
    
    # Create mock request
    req = func.HttpRequest(
        method='GET',
        url=f'/files/{sample_file_metadata.id}/download',
        route_params={'file_id': str(sample_file_metadata.id)},
        headers={'X-MS-CLIENT-PRINCIPAL': encoded_claims},
        body=None
    )
    
    response = _download_file(req, repository, blob_service)
    
    assert response.status_code == 200
    assert response.get_body() == sample_file_content
    assert response.headers['Content-Disposition'] == f'attachment; filename="{sample_file_metadata.filename}"'
    assert response.headers['Content-Type'] == 'application/octet-stream'


def test_download_file_not_found(repository, blob_service):
    user_id = str(uuid4())
    non_existent_file_id = str(uuid4())
    
    # Create mock B2C claims
    mock_claims = {
        "claims": [
            {"typ": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier", "val": user_id}
        ]
    }
    encoded_claims = base64.b64encode(json.dumps(mock_claims).encode()).decode()
    
    # Create mock request
    req = func.HttpRequest(
        method='GET',
        url=f'/files/{non_existent_file_id}/download',
        route_params={'file_id': str(non_existent_file_id)},
        headers={'X-MS-CLIENT-PRINCIPAL': encoded_claims},
        body=None
    )
    
    response = _download_file(req, repository, blob_service)
    
    assert response.status_code == 404
    assert json.loads(response.get_body())['error'] == 'File not found'


def test_download_file_unauthorized(repository, blob_service):
    # Create mock request without claims header
    req = func.HttpRequest(
        method='GET',
        url='/files/some-id/download',
        route_params={'file_id': 'some-id'},
        headers={},
        body=None
    )
    
    response = _download_file(req, repository, blob_service)
    
    assert response.status_code == 401
    assert json.loads(response.get_body())['error'] == 'Unauthorized - Missing user claims'


def test_download_file_forbidden(repository, blob_service, sample_file_metadata):
    different_user_id = str(uuid4())
    
    # Create mock B2C claims with different user_id
    mock_claims = {
        "claims": [
            {"typ": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier", "val": different_user_id}
        ]
    }
    encoded_claims = base64.b64encode(json.dumps(mock_claims).encode()).decode()
    
    # Create mock request
    req = func.HttpRequest(
        method='GET',
        url=f'/files/{sample_file_metadata.id}/download',
        route_params={'file_id': str(sample_file_metadata.id)},
        headers={'X-MS-CLIENT-PRINCIPAL': encoded_claims},
        body=None
    )
    
    response = _download_file(req, repository, blob_service)
    
    assert response.status_code == 403
    error_response = json.loads(response.get_body())
    assert "don't have permission" in error_response['error']

@pytest.fixture
def structured_docx_file_metadata(repository, blob_service):
    # Create a unique filename
    filename = f"test_docx_{uuid4()}.docx"
    user_id = "test-user-123"
    
    # Create file metadata with structured information
    file_metadata = FileMetadataDb(
        filename=filename,
        type=FileType.CV,
        user_id=user_id,
        url=f"https://test.blob.core.windows.net/{filename}",
        text="Sample CV text",
        pages=[DocumentPage(
            page_number=1,
            content="Page 1 content",
            lines=[
                Line(content="Line 1"),
                Line(content="Line 2")
            ],
            tables=[[
                [TableCell(text="Header 1"), TableCell(text="Header 2")],
                [TableCell(text="Data 1"), TableCell(text="Data 2")]
            ]]
        )],
        paragraphs=["Paragraph 1", "Paragraph 2"],
        tables=[[
            [TableCell(text="Header 1"), TableCell(text="Header 2")],
            [TableCell(text="Data 1"), TableCell(text="Data 2")]
        ]],
        styles={
            "Heading1": DocumentStyle(
                name="Heading 1",
                font_name="Arial",
                font_size=16.0,
                is_bold=True,
                is_italic=False,
                is_underline=False
            )
        },
        headers=["Document Header"],
        footers=["Document Footer"]
    )
    
    # Save to database
    saved_metadata = repository.upsert_file(file_metadata.model_dump(mode="json"))
    yield saved_metadata
    
    # Cleanup after test
    try:
        repository.delete_file(user_id=user_id, file_id=str(saved_metadata.id))
    except Exception as e:
        print(f"Error cleaning up DOCX test file: {e}")

@pytest.fixture
def structured_pdf_file_metadata(repository, blob_service):
    # Create a unique filename
    filename = f"test_pdf_{uuid4()}.pdf"
    user_id = "test-user-123"
    
    # Create file metadata with structured information
    file_metadata = FileMetadataDb(
        filename=filename,
        type=FileType.CV,
        user_id=user_id,
        url=f"https://test.blob.core.windows.net/{filename}",
        text="Sample CV text",
        pages=[DocumentPage(
            page_number=1,
            content="Page 1 content",
            lines=[
                Line(content="Line 1"),
                Line(content="Line 2")
            ],
            tables=[[
                [TableCell(text="Header 1"), TableCell(text="Header 2")],
                [TableCell(text="Data 1"), TableCell(text="Data 2")]
            ]]
        )],
        paragraphs=["Paragraph 1", "Paragraph 2"],
        tables=[[
            [TableCell(text="Header 1"), TableCell(text="Header 2")],
            [TableCell(text="Data 1"), TableCell(text="Data 2")]
        ]],
        styles={
            "style_1": DocumentStyle(
                name="style_1",
                font_name="Times New Roman",
                font_size=12.0,
                is_bold=True,
                is_italic=False,
                is_underline=False
            )
        }
    )
    
    # Save to database
    saved_metadata = repository.upsert_file(file_metadata.model_dump(mode="json"))
    yield saved_metadata
    
    # Cleanup after test
    try:
        repository.delete_file(user_id=user_id, file_id=str(saved_metadata.id))
    except Exception as e:
        print(f"Error cleaning up PDF test file: {e}")

def test_get_file_with_docx_structure(repository, structured_docx_file_metadata):
    """Test getting a DOCX file with structured information from real Cosmos DB"""
    # Create request with mock claims
    req = func.HttpRequest(
        method='GET',
        url=f'/api/files/{structured_docx_file_metadata.id}',
        route_params={'file_id': str(structured_docx_file_metadata.id)},
        headers={'X-MS-CLIENT-PRINCIPAL': create_mock_claims(structured_docx_file_metadata.user_id)},
        body=None
    )
    
    # Call the function
    response = _get_file(req, repository)
    
    # Assert response
    assert response.status_code == 200
    result = json.loads(response.get_body())
    
    # Verify all structured information is present
    assert result['filename'].endswith('.docx')
    assert result['text'] == 'Sample CV text'
    assert len(result['pages']) == 1
    assert result['pages'][0]['page_number'] == 1
    assert len(result['pages'][0]['lines']) == 2
    assert len(result['pages'][0]['tables']) == 1
    assert len(result['paragraphs']) == 2
    assert len(result['tables']) == 1
    assert len(result['styles']) == 1
    assert result['styles']['Heading1']['font_name'] == 'Arial'
    assert result['headers'] == ['Document Header']
    assert result['footers'] == ['Document Footer']

def test_get_file_with_pdf_structure(repository, structured_pdf_file_metadata):
    # Create mock B2C claims
    mock_claims = {
        "claims": [
            {"typ": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier", "val": structured_pdf_file_metadata.user_id},
            {"typ": "name", "val": "Test User"},
            {"typ": "emails", "val": "test@example.com"}
        ]
    }
    encoded_claims = base64.b64encode(json.dumps(mock_claims).encode()).decode()
    
    # Create mock request with B2C headers
    req = func.HttpRequest(
        method='GET',
        url=f'/api/files/{structured_pdf_file_metadata.id}',
        route_params={'file_id': str(structured_pdf_file_metadata.id)},
        headers={
            'X-MS-CLIENT-PRINCIPAL': encoded_claims,
            'X-MS-CLIENT-PRINCIPAL-ID': structured_pdf_file_metadata.user_id,
            'X-MS-CLIENT-PRINCIPAL-NAME': 'test@example.com'
        },
        body=None
    )
    
    # Call the function
    response = _get_file(req, repository)
    
    # Verify response
    assert response.status_code == 200
    result = json.loads(response.get_body())
    
    # Verify basic structure
    assert result['id'] == str(structured_pdf_file_metadata.id)
    assert result['filename'] == structured_pdf_file_metadata.filename
    assert result['type'] == structured_pdf_file_metadata.type
    assert result['user_id'] == structured_pdf_file_metadata.user_id
    assert result['url'] == structured_pdf_file_metadata.url
    
    # Verify structured information
    assert 'pages' in result
    assert len(result['pages']) == 1
    assert result['pages'][0]['page_number'] == 1
    assert result['pages'][0]['content'] == "Page 1 content"
    assert len(result['pages'][0]['lines']) == 2
    assert result['pages'][0]['lines'][0]['content'] == "Line 1"
    assert result['pages'][0]['lines'][1]['content'] == "Line 2"
    
    # Verify tables
    assert len(result['pages'][0]['tables']) == 1
    assert len(result['pages'][0]['tables'][0]) == 2  # Two rows
    assert len(result['pages'][0]['tables'][0][0]) == 2  # Two columns
    assert result['pages'][0]['tables'][0][0][0]['text'] == "Header 1"
    assert result['pages'][0]['tables'][0][0][1]['text'] == "Header 2"
    assert result['pages'][0]['tables'][0][1][0]['text'] == "Data 1"
    assert result['pages'][0]['tables'][0][1][1]['text'] == "Data 2"

@pytest.fixture
def sample_resume_structure():
    return {
        "personal_details": [
            {"type": "name", "text": "John Doe"},
            {"type": "email", "text": "john@example.com"},
            {"type": "phone", "text": "+1234567890"},
            {"type": "location", "text": "New York, USA"}
        ],
        "professional_summary": "Experienced software engineer with 10 years of experience",
        "skills": ["Python", "TypeScript", "React", "Azure"],
        "experience": [
            {
                "title": "Senior Software Engineer",
                "start_date": "2020",
                "end_date": "Present",
                "lines": [
                    "Led development of cloud-native applications",
                    "Managed team of 5 developers"
                ]
            }
        ],
        "education": [],
        "additional_information": ["Languages: English, Spanish"]
    }

@pytest.fixture
def structured_file_metadata(repository, blob_service, sample_file_content, sample_resume_structure):
    # Create a unique filename
    filename = f"test_cv_{uuid4()}.pdf"
    
    # Upload file to blob storage
    blob_url = blob_service.upload_blob(
        container_name="resume-match-pro-files",
        filename=filename,
        content=sample_file_content
    )
    
    # Create file metadata with document analysis structure
    file_metadata = FileMetadataDb(
        filename=filename,
        type=FileType.CV,
        user_id="test-user-123",
        url=blob_url,
        document_analysis={
            "document_type": "CV",
            "structure": sample_resume_structure
        }
    )
    
    # Save to database
    return repository.upsert_file(file_metadata.model_dump(mode="json"))

def test_get_file_with_structure(repository, structured_file_metadata):
    # Create mock B2C claims
    mock_claims = {
        "claims": [
            {"typ": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier", "val": "test-user-123"},
            {"typ": "name", "val": "Test User"},
            {"typ": "emails", "val": "test@example.com"}
        ]
    }
    encoded_claims = base64.b64encode(json.dumps(mock_claims).encode()).decode()
    
    # Create mock request
    req = func.HttpRequest(
        method='GET',
        url=f'/api/files/{structured_file_metadata.id}',
        route_params={'file_id': str(structured_file_metadata.id)},
        headers={
            'X-MS-CLIENT-PRINCIPAL': encoded_claims
        },
        body=None
    )
    
    # Call the function
    response = _get_file(req, repository)
    
    # Assert response
    assert response.status_code == 200
    result = json.loads(response.get_body())
    
    # Verify structure fields
    assert 'structure' in result
    structure = result['structure']
    assert len(structure['personal_details']) == 4
    assert structure['professional_summary'] == "Experienced software engineer with 10 years of experience"
    assert len(structure['skills']) == 4
    assert len(structure['experience']) == 1
    assert structure['experience'][0]['title'] == "Senior Software Engineer"
    assert len(structure['experience'][0]['lines']) == 2

def test_get_file_without_structure(repository, sample_file_metadata):
    # Create mock B2C claims
    mock_claims = {
        "claims": [
            {"typ": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier", "val": "test-user-123"},
            {"typ": "name", "val": "Test User"},
            {"typ": "emails", "val": "test@example.com"}
        ]
    }
    encoded_claims = base64.b64encode(json.dumps(mock_claims).encode()).decode()
    
    # Create mock request
    req = func.HttpRequest(
        method='GET',
        url=f'/api/files/{sample_file_metadata.id}',
        route_params={'file_id': str(sample_file_metadata.id)},
        headers={
            'X-MS-CLIENT-PRINCIPAL': encoded_claims
        },
        body=None
    )
    
    # Call the function
    response = _get_file(req, repository)
    
    # Assert response
    assert response.status_code == 200
    result = json.loads(response.get_body())
    
    # Verify structure is not present
    assert 'structure' not in result

def test_get_file_with_partial_structure(repository, blob_service, sample_file_content):
    # Create a unique filename
    filename = f"test_cv_{uuid4()}.pdf"
    
    # Upload file to blob storage
    blob_url = blob_service.upload_blob(
        container_name="resume-match-pro-files",
        filename=filename,
        content=sample_file_content
    )
    
    # Create file metadata with partial document analysis structure
    partial_structure = {
        "personal_details": [
            {"type": "name", "text": "John Doe"}
        ],
        "professional_summary": "Experienced software engineer",
        "skills": ["Python"],
        "experience": [],
        "education": [],
        "additional_information": []
    }
    
    file_metadata = FileMetadataDb(
        filename=filename,
        type=FileType.CV,
        user_id="test-user-123",
        url=blob_url,
        document_analysis={
            "document_type": "CV",
            "structure": partial_structure
        }
    )
    
    # Save to database
    file_metadata = repository.upsert_file(file_metadata.model_dump(mode="json"))
    
    # Create mock B2C claims
    mock_claims = {
        "claims": [
            {"typ": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier", "val": "test-user-123"},
            {"typ": "name", "val": "Test User"},
            {"typ": "emails", "val": "test@example.com"}
        ]
    }
    encoded_claims = base64.b64encode(json.dumps(mock_claims).encode()).decode()
    
    # Create mock request
    req = func.HttpRequest(
        method='GET',
        url=f'/api/files/{file_metadata.id}',
        route_params={'file_id': str(file_metadata.id)},
        headers={
            'X-MS-CLIENT-PRINCIPAL': encoded_claims
        },
        body=None
    )
    
    # Call the function
    response = _get_file(req, repository)
    
    # Assert response
    assert response.status_code == 200
    result = json.loads(response.get_body())
    
    # Verify partial structure
    assert 'structure' in result
    structure = result['structure']
    assert len(structure['personal_details']) == 1
    assert structure['professional_summary'] == "Experienced software engineer"
    assert len(structure['skills']) == 1
    assert len(structure['experience']) == 0
    assert len(structure['education']) == 0
    assert len(structure['additional_information']) == 0