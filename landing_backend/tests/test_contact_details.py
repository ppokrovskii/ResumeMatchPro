import json
from azure import functions as func
from unittest import mock
# add project root to sys.path
import sys
from pathlib import Path

from landing_backend.contact_details.models import ContactDetailsDbModelResponse
sys.path.append(str(Path(__file__).parent.parent))

from landing_backend.contact_details.contact_details import get_contact_details


# mocking the imported modules in the function
# in the function I have 'from contact_details.db_service import get_cosmos_db_client'
# so that's why I mock 'contact_details.contact_details.get_cosmos_db_client'
# and not 'contact_details.db_service.get_cosmos_db_client'
@mock.patch("landing_backend.contact_details.contact_details.get_cosmos_db_client")
@mock.patch("landing_backend.contact_details.contact_details.ContactDetailsRepository")
def test_get_all_contact_details(mock_contact_details_repository, mock_get_cosmos_db_client):
    mock_get_cosmos_db_client.return_value = "mock_get_cosmos_db_client"
    # [ContactDetailsDbModelResponse(**item) for item in items]
    expected_contact_details = [
        {
        "email": "test@gmail.com",
        "first_name": "Test",
        "last_name": "User",
        },
        {
        "email": "email2",
        "first_name": "Test2",
        "last_name": "User2",
        }
    ]
    mock_contact_details = [ContactDetailsDbModelResponse(**item) for item in expected_contact_details]
    mock_contact_details_repository.return_value.get_all_contact_details.return_value = mock_contact_details
    # Patch the ContactDetailsRepository to use the mock_db_client
    # # Instantiate the repository to attach the mock container
    # repository = ContactDetailsRepository(db_client=mock_db_client)
    # repository.container = mock_container  # Ensure the mock container is set

    # Create the request
    req = func.HttpRequest(
        method='GET',
        body=None,
        url='/api/results',
        params={'user_id': '123', 'file_id': 'cba283f1-552e-4e75-9629-659cb42f8b20', 'file_type': 'CV'}
    )

    # Call the function
    func_call = get_contact_details.build().get_user_function()
    response = func_call(req)

    # Assertions
    assert response.status_code == 200
    assert response.mimetype == "application/json"
    body = response.get_body()
    body_json = json.loads(body)
    [item.pop('id') for item in body_json['contact_details']]
    assert body_json['contact_details'] == expected_contact_details
    