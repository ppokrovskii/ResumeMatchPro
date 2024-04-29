import json
from unittest import mock
import azure.functions as func



# add project root to sys.path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from user_files.user_files import get_files
from shared.models import FileMetadataDb

@mock.patch("user_files.user_files.get_cosmos_db_client")
@mock.patch("user_files.user_files.FilesRepository")
def test_get_files(mock_files_repository, mock_get_cosmos_db_client):
    # Mock the necessary dependencies
    mock_files_metadata_db = [
        FileMetadataDb(filename="file1.txt", type="CV", user_id="123", url="https://file1.txt"),
        FileMetadataDb(filename="file2.txt", type="CV", user_id="123", url="https://file2.txt"),
    ]
    mock_files_repository.return_value.get_files_from_db.return_value = mock_files_metadata_db
    mock_get_cosmos_db_client.return_value = "mock_cosmos_db_client"

    req = func.HttpRequest(method='GET',
                           body=None,
                           url='/api/files',
                           params={'user_id': '123', 'type': 'CV'})
    # Call the function.
    func_call = get_files.build().get_user_function()
    response = func_call(req)


    # Assert the expected behavior
    assert response.status_code == 200
    assert response.mimetype == "application/json"
    # assert expected response will be like '{"files":[{"id":"cba283f1-552e-4e75-9629-659cb42f8b20","filename":"file1.txt","type":"CV","user_id":"123","url":"https://file1.txt","text":null},{"id":"4bb8031e-2ea0-4498-a8be-8835c68411a2","filename":"file2.txt","type":"CV","user_id":"123","url":"https://file2.txt","text":null}]}'
    # don't asser id because it's generated randomly
    result = json.loads(response.get_body().decode("utf-8"))
    [file.pop("id") for file in result["files"]]
    assert result == {
        "files": [
            {"filename": "file1.txt", "type": "CV", "user_id": "123", "url": "https://file1.txt", "text": None},
            {"filename": "file2.txt", "type": "CV", "user_id": "123", "url": "https://file2.txt", "text": None}
        ]
    }
    assert mock_files_repository.return_value.get_files_from_db.call_args == mock.call("123", "CV")
    assert mock_files_repository.return_value.get_files_from_db.call_count == 1
    assert mock_get_cosmos_db_client.call_count == 1
    assert mock_get_cosmos_db_client.call_args == mock.call()
    

@mock.patch("user_files.user_files.get_cosmos_db_client")
@mock.patch("user_files.user_files.FilesRepository")    
def test_get_files_no_files_found(mock_files_repository, mock_get_cosmos_db_client):
    # Mock the necessary dependencies
    mock_files_repository.return_value.get_files_from_db.return_value = []
    mock_get_cosmos_db_client.return_value = "mock_cosmos_db_client"

    req = func.HttpRequest(method='GET',
                           body=None,
                           url='/api/files',
                           params={'user_id': '123', 'type': 'CV'})
    # Call the function.
    func_call = get_files.build().get_user_function()
    response = func_call(req)


    # Assert the expected behavior
    assert response.status_code == 200
    assert response.mimetype == "application/json"
    assert response.get_body().decode("utf-8") == '{"files":[]}'
    assert mock_files_repository.return_value.get_files_from_db.call_args == mock.call("123", "CV")
    assert mock_files_repository.return_value.get_files_from_db.call_count == 1
    assert mock_get_cosmos_db_client.call_count == 1
    assert mock_get_cosmos_db_client.call_args == mock.call()