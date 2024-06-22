import pytest
from azure.cosmos import CosmosClient

# add project root to sys.path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from landing_backend.contact_details.models import ContactDetailsDbModelCreate


from contact_details.contact_details_repository import ContactDetailsRepository

@pytest.fixture
def repository():
    # Create a Cosmos DB client and initialize the repository
    client = CosmosClient(url="https://localhost:8081",
                credential=(
                    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
                ),)
    db_client = client.get_database_client("resumematchpro_test")
    return ContactDetailsRepository(db_client)


# add pytest fixture to delete all items from the container before each test
@pytest.fixture(autouse=True)
def run_around_tests(repository):
    repository.delete_all()
    

@pytest.fixture
def sample_contact_details() -> dict:
    contact_details = {
        "email": "test@gmail.com",
        "first_name": "Test",
        "last_name": "User",
    }
    return ContactDetailsDbModelCreate(**contact_details)
    
def test_upsert_contact_details(repository, sample_contact_details):
    # Create a sample contact details
    contact_details = sample_contact_details

    # Add the contact details to the repository
    repository.upsert_contact_details(contact_details.model_dump(mode="json", exclude_none=True))

    # Retrieve the contact details from the repository
    contact_details = repository.get_contact_details_from_db(email=contact_details.email)
    assert contact_details.email == sample_contact_details.email
    
    
def test_get_all_contact_details(repository, sample_contact_details):
    # Create a sample contact details
    contact_details = sample_contact_details

    # Add the contact details to the repository
    repository.upsert_contact_details(contact_details.model_dump(mode="json", exclude_none=True))

    # Retrieve all contact details from the repository
    contact_details_list = repository.get_all_contact_details()
    assert len(contact_details_list) == 1
    assert contact_details_list[0].email == sample_contact_details.email
    assert contact_details_list[0].first_name == sample_contact_details.first_name
    assert contact_details_list[0].last_name == sample_contact_details.last_name
    assert contact_details_list[0].id == sample_contact_details.id
        