import json
from unittest import mock
import azure.functions as func
from datetime import datetime
import pytest
import base64

# add project root to sys.path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from users.users import create_user
from users.models import CreateUserRequest, CreateUserResponse, UserDb

# Mock client principal for admin user
MOCK_CLIENT_PRINCIPAL = base64.b64encode(json.dumps({
    "claims": [
        {"typ": "extension_IsAdmin", "val": "true"}
    ]
}).encode()).decode()

@mock.patch("users.users.verify_admin_token", return_value=True)
@mock.patch("users.users.get_cosmos_db_client")
@mock.patch("users.users.UserRepository")
def test_create_user_success(mock_user_repository, mock_get_cosmos_db_client, mock_verify_admin):
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

    # Create test request with admin token
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
        headers={'x-ms-client-principal': MOCK_CLIENT_PRINCIPAL},
        params={}
    )

    # Call the function
    func_call = create_user.build().get_user_function()
    response = func_call(req)

    # Assert response
    assert response.status_code == 201
    response_body = json.loads(response.get_body())
    assert response_body["userId"] == "test-user-123"
    assert response_body["email"] == "test@example.com"
    assert response_body["name"] == "Test User"
    assert not response_body["isAdmin"]
    assert response_body["filesLimit"] == 20
    assert response_body["matchingLimit"] == 100

    # Verify repository calls
    assert mock_user_repository.return_value.get_user.call_count == 1
    assert mock_user_repository.return_value.get_user.call_args == mock.call("test-user-123")
    assert mock_user_repository.return_value.create_user.call_count == 1
    assert mock_get_cosmos_db_client.call_count == 1

@mock.patch("users.users.verify_admin_token", return_value=True)
@mock.patch("users.users.get_cosmos_db_client")
@mock.patch("users.users.UserRepository")
def test_create_user_already_exists(mock_user_repository, mock_get_cosmos_db_client, mock_verify_admin):
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

    # Create test request with admin token
    req = func.HttpRequest(
        method='POST',
        url='/api/users',
        body=json.dumps({
            "userId": "test-user-123",
            "email": "test@example.com",
            "name": "Test User"
        }).encode(),
        headers={'x-ms-client-principal': MOCK_CLIENT_PRINCIPAL},
        params={}
    )

    # Call the function
    func_call = create_user.build().get_user_function()
    response = func_call(req)

    # Assert response
    assert response.status_code == 409
    response_body = json.loads(response.get_body())
    assert response_body["error"] == "User already exists"

    # Verify repository calls
    assert mock_user_repository.return_value.get_user.call_count == 1
    assert mock_user_repository.return_value.create_user.call_count == 0

@mock.patch("users.users.verify_admin_token", return_value=True)
@mock.patch("users.users.get_cosmos_db_client")
@mock.patch("users.users.UserRepository")
def test_create_user_invalid_request(mock_user_repository, mock_get_cosmos_db_client, mock_verify_admin):
    # Create test request with missing required fields and admin token
    req = func.HttpRequest(
        method='POST',
        url='/api/users',
        body=json.dumps({
            "email": "test@example.com"  # Missing required fields
        }).encode(),
        headers={'x-ms-client-principal': MOCK_CLIENT_PRINCIPAL},
        params={}
    )

    # Call the function
    func_call = create_user.build().get_user_function()
    response = func_call(req)

    # Assert response
    assert response.status_code == 400
    response_body = json.loads(response.get_body())
    assert "error" in response_body
    assert "userId" in response_body["error"]
    assert "name" in response_body["error"]

    # Verify no repository calls were made
    assert mock_user_repository.return_value.get_user.call_count == 0
    assert mock_user_repository.return_value.create_user.call_count == 0

def test_user_db_cosmos_id_field():
    # Case 1: When id is not provided, it should use userId
    user_without_id = UserDb(
        userId="test123",
        email="test@example.com",
        name="Test User"
    )
    user_dict = user_without_id.model_dump()
    assert "id" in user_dict, "Cosmos DB requires an 'id' field"
    assert user_dict["id"] == user_dict["userId"], "id should match userId when not provided"

    # Case 2: When id is explicitly provided, it should use that value
    user_with_id = UserDb(
        id="custom-id",
        userId="test123",
        email="test@example.com",
        name="Test User"
    )
    user_dict = user_with_id.model_dump()
    assert user_dict["id"] == "custom-id", "id should use the provided value"
    assert user_dict["userId"] == "test123", "userId should remain unchanged"

def test_user_db_datetime_serialization():
    # Create a user with specific datetime values
    test_date = datetime(2024, 1, 26, 5, 17, 59)
    user = UserDb(
        userId="test123",
        email="test@example.com",
        name="Test User",
        createdAt=test_date,
        lastMatchingReset=test_date
    )

    # Convert to JSON using the new method
    user_json = user.model_dump_json()
    user_dict = json.loads(user_json)

    # Verify datetime fields are serialized as ISO format strings
    assert user_dict["createdAt"] == "2024-01-26T05:17:59"
    assert user_dict["lastMatchingReset"] == "2024-01-26T05:17:59"

    # Verify other fields are present and correct
    assert user_dict["userId"] == "test123"
    assert user_dict["email"] == "test@example.com"
    assert user_dict["name"] == "Test User"
    assert user_dict["isAdmin"] is False
    assert user_dict["filesLimit"] == 20
    assert user_dict["matchingLimit"] == 100
    assert user_dict["matchingUsedCount"] == 0
    assert user_dict["filesCount"] == 0 