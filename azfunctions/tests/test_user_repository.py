import os
import sys
from datetime import datetime, timedelta, UTC
from pathlib import Path
from unittest import mock

import pytest
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

# Load test environment variables
load_dotenv(Path(__file__).parent / ".env.test")

# add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from shared.user_repository import UserRepository
from users.models import UserDb

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
    return UserRepository(database)

@pytest.fixture
def sample_user() -> UserDb:
    return UserDb(
        userId="test-user-123",
        email="test@example.com",
        name="Test User",
        isAdmin=False,
        filesLimit=20,
        matchingLimit=100,
        matchingUsedCount=0,
        filesCount=0,
        createdAt=datetime.now(UTC),
        lastMatchingReset=datetime.now(UTC)
    )

@pytest.fixture(autouse=True)
def cleanup(repository, sample_user):
    # This will run before each test
    try:
        # Try to get the user
        user = repository.get_user(sample_user.userId)
        if user:
            # If user exists, delete it
            repository.container.delete_item(user.id, partition_key=user.userId)
    except:
        pass
    
    yield  # This is where the test runs
    
    # This will run after each test
    try:
        # Try to get the user
        user = repository.get_user(sample_user.userId)
        if user:
            # If user exists, delete it
            repository.container.delete_item(user.id, partition_key=user.userId)
    except:
        pass

def test_create_and_get_user(repository, sample_user):
    # Create a user
    created_user = repository.create_user(sample_user.model_dump())
    assert created_user.userId == sample_user.userId
    assert created_user.email == sample_user.email
    
    # Get the user
    retrieved_user = repository.get_user(sample_user.userId)
    assert retrieved_user is not None
    assert retrieved_user.userId == sample_user.userId
    assert retrieved_user.email == sample_user.email

def test_update_user(repository, sample_user):
    # Create a user first
    created_user = repository.create_user(sample_user.model_dump())
    
    # Update user
    created_user.filesCount = 5
    updated_user = repository.update_user(created_user)
    
    # Verify update
    assert updated_user.filesCount == 5
    retrieved_user = repository.get_user(sample_user.userId)
    assert retrieved_user.filesCount == 5

def test_increment_files_count(repository, sample_user):
    # Create a user
    repository.create_user(sample_user.model_dump())
    
    # Increment files count
    updated_user = repository.increment_files_count(sample_user.userId)
    assert updated_user.filesCount == 1
    
    # Increment again
    updated_user = repository.increment_files_count(sample_user.userId)
    assert updated_user.filesCount == 2

def test_decrement_files_count(repository, sample_user):
    # Create a user with files
    sample_user.filesCount = 2
    created_user = repository.create_user(sample_user.model_dump())
    
    try:
        # Decrement files count
        updated_user = repository.decrement_files_count(created_user.userId)
        assert updated_user.filesCount == 1
        
        # Decrement again
        updated_user = repository.decrement_files_count(created_user.userId)
        assert updated_user.filesCount == 0
        
        # Decrement below zero should stay at zero
        updated_user = repository.decrement_files_count(created_user.userId)
        assert updated_user.filesCount == 0
    finally:
        # Clean up
        try:
            repository.container.delete_item(item=created_user.userId, partition_key=created_user.userId)
        except:
            pass

def test_increment_matching_count(repository, sample_user):
    # Create a user
    repository.create_user(sample_user.model_dump())
    
    # Increment matching count
    updated_user = repository.increment_matching_count(sample_user.userId)
    assert updated_user.matchingUsedCount == 1
    
    # Set last reset to more than 30 days ago
    updated_user.lastMatchingReset = datetime.now(UTC) - timedelta(days=31)
    repository.update_user(updated_user)
    
    # Increment again - should reset count first
    updated_user = repository.increment_matching_count(sample_user.userId)
    assert updated_user.matchingUsedCount == 1  # Started from 0 after reset

def test_can_upload_file(repository, sample_user):
    # Create a user with limit of 2 files
    sample_user.filesLimit = 2
    repository.create_user(sample_user.model_dump())
    
    # Should be able to upload initially
    assert repository.can_upload_file(sample_user.userId) is True
    
    # Add files up to limit
    sample_user.filesCount = 2
    repository.update_user(sample_user)
    
    # Should not be able to upload more
    assert repository.can_upload_file(sample_user.userId) is False

def test_can_perform_matching(repository, sample_user):
    # Create a user with limit of 2 matches
    sample_user.matchingLimit = 2
    repository.create_user(sample_user.model_dump())
    
    # Should be able to match initially
    assert repository.can_perform_matching(sample_user.userId) is True
    
    # Add matches up to limit
    sample_user.matchingUsedCount = 2
    repository.update_user(sample_user)
    
    # Should not be able to match more
    assert repository.can_perform_matching(sample_user.userId) is False
    
    # Set last reset to more than 30 days ago
    sample_user.lastMatchingReset = datetime.now(UTC) - timedelta(days=31)
    repository.update_user(sample_user)
    
    # Should be able to match again after 30 days
    assert repository.can_perform_matching(sample_user.userId) is True

def test_get_nonexistent_user(repository):
    # Try to get a user that doesn't exist
    user = repository.get_user("nonexistent-user")
    assert user is None

def test_increment_files_count_nonexistent_user(repository):
    # Try to increment files count for nonexistent user
    with pytest.raises(ValueError, match="User nonexistent-user not found"):
        repository.increment_files_count("nonexistent-user")

def test_matching_counter_increment_during_matching(repository, sample_user):
    # Create a user
    repository.create_user(sample_user.model_dump())
    
    # Increment matching count multiple times
    for i in range(3):
        updated_user = repository.increment_matching_count(sample_user.userId)
        assert updated_user.matchingUsedCount == i + 1

def test_matching_counter_reset_after_30_days(repository, sample_user):
    # Create a user with some matching count
    sample_user.matchingUsedCount = 50
    sample_user.lastMatchingReset = datetime.now(UTC) - timedelta(days=31)
    repository.create_user(sample_user.model_dump())
    
    # Increment matching count - should reset first
    updated_user = repository.increment_matching_count(sample_user.userId)
    assert updated_user.matchingUsedCount == 1  # Should be 1 after reset and increment
    assert updated_user.lastMatchingReset > sample_user.lastMatchingReset

def test_can_upload_file_with_matching_limit_not_exceeded(repository, sample_user):
    # Create a user with matching count below limit
    sample_user.matchingLimit = 10
    sample_user.matchingUsedCount = 5
    repository.create_user(sample_user.model_dump())
    
    # Should be able to upload
    assert repository.can_upload_file(sample_user.userId) is True

def test_cannot_upload_file_with_matching_limit_exceeded(repository, sample_user):
    # Create a user with matching count at limit
    sample_user.matchingLimit = 10
    sample_user.matchingUsedCount = 10
    repository.create_user(sample_user.model_dump())
    
    # Should not be able to upload
    assert repository.can_upload_file(sample_user.userId) is False

def test_cannot_upload_file_with_either_limit_exceeded(repository, sample_user):
    # Create user once
    repository.create_user(sample_user.model_dump())
    
    # Test cases with different limit combinations
    test_cases = [
        # (filesCount, filesLimit, matchingUsedCount, matchingLimit, expected_result)
        (19, 20, 100, 100, False),  # Matching limit reached
        (20, 20, 50, 100, False),   # Files limit reached
        (20, 20, 100, 100, False),  # Both limits reached
        (19, 20, 50, 100, True),    # Neither limit reached
    ]
    
    for files_count, files_limit, matching_used, matching_limit, expected in test_cases:
        # Update user with test case values
        sample_user.filesCount = files_count
        sample_user.filesLimit = files_limit
        sample_user.matchingUsedCount = matching_used
        sample_user.matchingLimit = matching_limit
        repository.update_user(sample_user)
        
        # Check if can upload matches expected result
        assert repository.can_upload_file(sample_user.userId) is expected

def test_matching_counter_reset_in_can_upload_file(repository, sample_user):
    # Create a user with matching count at limit but old reset date
    sample_user.matchingLimit = 10
    sample_user.matchingUsedCount = 10
    sample_user.lastMatchingReset = datetime.now(UTC) - timedelta(days=31)
    repository.create_user(sample_user.model_dump())
    
    # Should be able to upload after reset
    assert repository.can_upload_file(sample_user.userId) is True
    
    # Verify counter was reset
    updated_user = repository.get_user(sample_user.userId)
    assert updated_user.matchingUsedCount == 0
    assert updated_user.lastMatchingReset > sample_user.lastMatchingReset 

def test_can_upload_file_with_naive_datetime(repository, sample_user):
    # Create a user with naive datetime for lastMatchingReset
    naive_datetime = datetime.now() - timedelta(days=31)
    # Simulate how the data might come from Cosmos DB by converting to string and back
    naive_datetime_str = naive_datetime.isoformat()
    
    # Create user data as it would come from Cosmos DB
    user_data = sample_user.model_dump()
    user_data['lastMatchingReset'] = naive_datetime_str
    
    # Create user with the naive datetime string
    repository.container.create_item(user_data)
    
    # Should not raise timezone error
    assert repository.can_upload_file(sample_user.userId) is True
    
    # Verify the reset happened
    updated_user = repository.get_user(sample_user.userId)
    assert updated_user.matchingUsedCount == 0
    assert updated_user.lastMatchingReset.tzinfo is not None  # Should be timezone-aware 