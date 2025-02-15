import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from azure.cosmos import CosmosClient
from shared.matching_results_repository import MatchingResultsRepository

@pytest.fixture(scope="session")
def cosmos_client():
    # Create a Cosmos DB client for testing
    client = CosmosClient(
        url="https://localhost:8081",
        credential="C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
        connection_verify=False  # Disable SSL verification for local emulator
    )
    
    # Create database if it doesn't exist
    try:
        database = client.create_database_if_not_exists("resumematchpro_test")
    except Exception as e:
        print(f"Error creating database: {e}")
        raise
    
    return client

@pytest.fixture
def repository(cosmos_client) -> MatchingResultsRepository:
    db_client = cosmos_client.get_database_client("resumematchpro_test")
    repo = MatchingResultsRepository(db_client)
    
    # Ensure the container exists
    try:
        repo.container.read()
    except Exception as e:
        print(f"Error reading container: {e}")
        raise
        
    return repo

# Add pytest fixture to delete all items from the container before each test
@pytest.fixture(autouse=True)
def cleanup(repository):
    repository.delete_all()
    yield
    repository.delete_all()

# Mock the get_cosmos_db_client function for tests, but only for specific test files
@pytest.fixture(autouse=True)
def mock_cosmos_db_client(request, monkeypatch, cosmos_client):
    # Skip mocking for test_matching_results.py
    if "test_matching_results.py" not in str(request.fspath):
        def mock_get_client():
            db = cosmos_client.get_database_client("resumematchpro_test")
            db._client = cosmos_client  # Ensure the client is properly set
            return db
        
        from shared import db_service
        monkeypatch.setattr(db_service, "get_cosmos_db_client", mock_get_client) 