import json
from unittest import mock
import azure.functions as func
from datetime import datetime

# add project root to sys.path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from users.users import create_user
from users.models import CreateUserRequest, CreateUserResponse, UserDb

@mock.patch("users.users.get_cosmos_db_client")
@mock.patch("users.users.UserRepository")
def test_create_user_success(mock_user_repository, mock_get_cosmos_db_client):
    # Mock the necessary dependencies
    mock_user_repository.return_value.get_user.return_value = None  # User doesn't exist
    mock_saved_user = UserDb(
        userId="test-user-123",
        email="test@example.com",
        name="Test User",
        isAdmin=False,
        filesLimit=20,
        matchingLimit=100,
        matchingUsedCount=0,
        filesCount=0,
        createdAt=datetime.utcnow(),
        lastMatchingReset=datetime.utcnow()
    )
    mock_user_repository.return_value.create_user.return_value = mock_saved_user
    mock_get_cosmos_db_client.return_value = "mock_cosmos_db_client"

    # Create test request
    req = func.HttpRequest(
        method='POST',
        url='/api/users',
        body=json.dumps({
            "userId": "test-user-123",
            "email": "test@example.com",
            "name": "Test User",
            "isAdmin": False,
            "filesLimit": 20,
            "matchingLimit": 100
        }).encode(),
        params={}
    )

    # Call the function
    func_call = create_user.build().get_user_function()
    response = func_call(req)

    # Assert response
    assert response.status_code == 201
    assert response.mimetype == "application/json"
    
    # Verify response body
    result = json.loads(response.get_body().decode("utf-8"))
    # Remove timestamp fields for comparison
    result.pop("createdAt")
    
    assert result == {
        "userId": "test-user-123",
        "email": "test@example.com",
        "name": "Test User",
        "isAdmin": False,
        "filesLimit": 20,
        "matchingLimit": 100,
        "matchingUsedCount": 0,
        "filesCount": 0
    }

    # Verify repository calls
    assert mock_user_repository.return_value.get_user.call_count == 1
    assert mock_user_repository.return_value.get_user.call_args == mock.call("test-user-123")
    assert mock_user_repository.return_value.create_user.call_count == 1
    assert mock_get_cosmos_db_client.call_count == 1

@mock.patch("users.users.get_cosmos_db_client")
@mock.patch("users.users.UserRepository")
def test_create_user_already_exists(mock_user_repository, mock_get_cosmos_db_client):
    # Mock existing user
    mock_existing_user = UserDb(
        userId="test-user-123",
        email="test@example.com",
        name="Test User",
        isAdmin=False,
        filesLimit=20,
        matchingLimit=100,
        matchingUsedCount=0,
        filesCount=0,
        createdAt=datetime.utcnow(),
        lastMatchingReset=datetime.utcnow()
    )
    mock_user_repository.return_value.get_user.return_value = mock_existing_user
    mock_get_cosmos_db_client.return_value = "mock_cosmos_db_client"

    # Create test request
    req = func.HttpRequest(
        method='POST',
        url='/api/users',
        body=json.dumps({
            "userId": "test-user-123",
            "email": "test@example.com",
            "name": "Test User"
        }).encode(),
        params={}
    )

    # Call the function
    func_call = create_user.build().get_user_function()
    response = func_call(req)

    # Assert response
    assert response.status_code == 409
    assert response.mimetype == "application/json"
    result = json.loads(response.get_body().decode("utf-8"))
    assert result == {"error": "User already exists"}

    # Verify repository calls
    assert mock_user_repository.return_value.get_user.call_count == 1
    assert mock_user_repository.return_value.create_user.call_count == 0

@mock.patch("users.users.get_cosmos_db_client")
@mock.patch("users.users.UserRepository")
def test_create_user_invalid_request(mock_user_repository, mock_get_cosmos_db_client):
    # Create test request with missing required fields
    req = func.HttpRequest(
        method='POST',
        url='/api/users',
        body=json.dumps({
            "email": "test@example.com"  # Missing required fields
        }).encode(),
        params={}
    )

    # Call the function
    func_call = create_user.build().get_user_function()
    response = func_call(req)

    # Assert response
    assert response.status_code == 400
    assert response.mimetype == "application/json"
    
    # Verify no repository calls were made
    assert mock_user_repository.return_value.get_user.call_count == 0
    assert mock_user_repository.return_value.create_user.call_count == 0 