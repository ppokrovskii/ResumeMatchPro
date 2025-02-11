import os
import sys
from datetime import datetime, timedelta
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
        createdAt=datetime.utcnow(),
        lastMatchingReset=datetime.utcnow()
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
    repository.create_user(sample_user.model_dump())
    
    # Decrement files count
    updated_user = repository.decrement_files_count(sample_user.userId)
    assert updated_user.filesCount == 1
    
    # Decrement again
    updated_user = repository.decrement_files_count(sample_user.userId)
    assert updated_user.filesCount == 0
    
    # Decrement below zero should stay at zero
    updated_user = repository.decrement_files_count(sample_user.userId)
    assert updated_user.filesCount == 0

def test_increment_matching_count(repository, sample_user):
    # Create a user
    repository.create_user(sample_user.model_dump())
    
    # Increment matching count
    updated_user = repository.increment_matching_count(sample_user.userId)
    assert updated_user.matchingUsedCount == 1
    
    # Set last reset to more than 30 days ago
    updated_user.lastMatchingReset = datetime.utcnow() - timedelta(days=31)
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
    sample_user.lastMatchingReset = datetime.utcnow() - timedelta(days=31)
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