import os
import sys
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from dotenv import load_dotenv

# Load test environment variables
load_dotenv(Path(__file__).parent / ".env.test")

# add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from shared.files_repository import FilesRepository
from shared.models import FileMetadataDb


@pytest.fixture
def repository(cosmos_client):
    # Use the session-scoped cosmos_client
    database = cosmos_client.get_database_client("resumematchpro_test")
    return FilesRepository(database)


# add pytest fixture to delete all items from the container before each test
@pytest.fixture(autouse=True)
def run_around_tests(repository):
    repository.delete_all()


@pytest.fixture
def sample_CV() -> FileMetadataDb:
    return FileMetadataDb(
        user_id="b3f7b3b3-3b3b-3b3b-3b3b-3b3b3b3b3b3b",
        filename="cv.txt",
        type="CV",
        url="https://cv.com",
        text="Python Developer",
    )


def test_upsert_file(repository, sample_CV):
    # Create a sample file
    file = sample_CV

    # Add the file to the repository
    repository.upsert_file(file.model_dump(mode="json"))

    # Retrieve the file from the repository
    files = repository.get_files_from_db(user_id=file.user_id)
    assert len(files) == 1
    assert files[0].filename == file.filename


def test_upsert_file_empty_text(repository, sample_CV):
    # Create a sample file
    file = sample_CV
    file.text = None

    # Add the file to the repository
    repository.upsert_file(file.model_dump(mode="json"))

    # Retrieve the file from the repository
    files = repository.get_files_from_db(user_id=file.user_id)
    assert len(files) == 1
    assert files[0].filename == file.filename
    assert files[0].text == None


def test_get_files_from_db(repository, sample_CV):
    # Create a sample file
    file = sample_CV

    # Add the file to the repository
    repository.upsert_file(file.model_dump(mode="json"))

    # Retrieve the file from the repository
    files = repository.get_files_from_db(user_id=file.user_id)
    assert len(files) == 1
    assert files[0].filename == file.filename


def test_delete_file_by_user_id_and_filename(repository, sample_CV):
    # Create a sample file
    file = sample_CV

    # Add the file to the repository
    repository.upsert_file(file.model_dump(mode="json"))

    # Delete the file from the repository
    repository.delete_file(user_id=file.user_id, filename=file.filename)

    # Retrieve the file from the repository
    files = repository.get_files_from_db(user_id=file.user_id)
    assert len(files) == 0


# def test_delete_file_by_id(repository, sample_CV):
#     # Create a sample file
#     file = sample_CV

#     # Add the file to the repository
#     repository.upsert_file(file.model_dump(mode="json"))

#     # Retrieve the file from the repository
#     files = repository.get_files_from_db(user_id=file.user_id)
#     file_id = files[0].id

#     # Delete the file from the repository
#     repository.delete_file(file_id=file_id)

#     # Retrieve the file from the repository
#     files = repository.get_files_from_db(user_id=file.user_id)
#     assert len(files) == 0


def test_get_file_by_id(repository, sample_CV):
    # Create a sample file
    file = sample_CV

    # Add the file to the repository
    repository.upsert_file(file.model_dump(mode="json"))

    # Retrieve the file from the repository
    files = repository.get_files_from_db(user_id=file.user_id)
    file_id = str(files[0].id)

    # Retrieve the file by ID
    file = repository.get_file_by_id(user_id=file.user_id, file_id=file_id)
    assert file is not None
    assert file.filename == sample_CV.filename


def test_get_file_by_id_not_found(repository):
    # Retrieve the file by ID
    file = repository.get_file_by_id(user_id=str(uuid4()), file_id=str(uuid4()))
    assert file is None
