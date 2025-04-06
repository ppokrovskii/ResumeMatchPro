import logging
import os
import socket
import sys
from pathlib import Path

from dotenv import load_dotenv

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load test environment variables
load_dotenv(Path(__file__).parent / ".env.test")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from azure.cosmos import CosmosClient
from shared.matching_results_repository import MatchingResultsRepository


# Define markers for tests requiring external services
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "requires_cosmos: mark test as requiring Azure Cosmos DB"
    )
    config.addinivalue_line(
        "markers", "requires_blob_storage: mark test as requiring Azure Blob Storage"
    )
    config.addinivalue_line(
        "markers", "requires_queue: mark test as requiring Azure Queue Storage"
    )
    config.addinivalue_line(
        "markers",
        "external_services: mark test as requiring any external Azure services",
    )


# Helper function to check if a service is available
def is_service_available(host, port):
    """Check if a service is available at the given host and port."""
    try:
        socket.create_connection((host, port), timeout=1)
        return True
    except (socket.timeout, socket.error, ConnectionRefusedError):
        return False


# Skip tests requiring external services if they are not available
def pytest_runtest_setup(item):
    markers = [m.name for m in item.iter_markers()]

    # Skip tests that require Cosmos DB if it's not available
    if "requires_cosmos" in markers or "external_services" in markers:
        if not is_service_available("localhost", 8081):
            pytest.skip("Cosmos DB emulator is not available")

    # Skip tests that require Blob Storage if it's not available
    if "requires_blob_storage" in markers or "external_services" in markers:
        if not is_service_available("127.0.0.1", 10000):
            pytest.skip("Azure Blob Storage emulator is not available")

    # Skip tests that require Queue Storage if it's not available
    if "requires_queue" in markers or "external_services" in markers:
        if not is_service_available("127.0.0.1", 10001):
            pytest.skip("Azure Queue Storage emulator is not available")


@pytest.fixture(scope="session")
def cosmos_client():
    # Create a Cosmos DB client for testing
    from azure.cosmos import CosmosClient

    client = CosmosClient(
        url="https://localhost:8081",
        credential="C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
        connection_verify=False,  # Disable SSL verification for local emulator
        connection_timeout=60,  # 60 seconds timeout
        retry_total=3,  # Maximum number of retries
        retry_backoff_max=10,  # Maximum backoff time between retries
        retry_fixed_interval=1,  # Fixed interval for retries in seconds
        retry_read=3,  # Number of read retries
        retry_connect=3,  # Number of connection retries
    )

    # Create database if it doesn't exist
    try:
        database = client.create_database_if_not_exists("resumematchpro_test")
    except Exception as e:
        print(f"Error creating database: {e}")
        raise

    return client


@pytest.fixture(scope="session", autouse=True)
def cleanup_database(cosmos_client):
    """Clean up all containers after all tests complete"""
    yield
    try:
        db = cosmos_client.get_database_client("resumematchpro_test")
        for container in db.list_containers():
            try:
                container.delete_container()
            except Exception as e:
                logger.warning(f"Failed to delete container {container.id}: {e}")
    except Exception as e:
        logger.warning(f"Failed to clean up database: {e}")


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
    try:
        repository.delete_all()
    except Exception as e:
        logger.warning(f"Failed to clean up database: {e}")
    yield
    try:
        repository.delete_all()
    except Exception as e:
        logger.warning(f"Failed to clean up database after test: {e}")


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
