import base64
import json
import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4

import azure.functions as func
from shared.models import FileMetadataDb, FileType
from user_files.exceptions import FileNotFoundError, UnauthorizedError, ValidationError
from user_files.user_files import _download_file


class TestDownloadFile(unittest.TestCase):
    def setUp(self):
        # Create mock services
        self.blob_service = MagicMock()
        self.repository = MagicMock()

        # Create sample data
        self.user_id = "test-user-123"
        self.file_id = str(uuid4())

        # Create mock claims
        mock_claims = {
            "claims": [
                {
                    "typ": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier",
                    "val": self.user_id,
                }
            ]
        }
        self.encoded_claims = base64.b64encode(
            json.dumps(mock_claims).encode()
        ).decode()

    def test_download_file_success(self):
        """Test successful file download."""
        # Create sample file metadata
        file_metadata = FileMetadataDb(
            id=self.file_id,
            filename="test_document.pdf",
            type=FileType.CV,
            user_id=self.user_id,
            url="https://test.blob.core.windows.net/test_document.pdf",
            content_type="application/pdf",
        )

        # Configure mock repository
        self.repository.get_file_by_id.return_value = file_metadata

        # Configure mock blob service
        sample_content = b"This is a sample file content"
        self.blob_service.get_file_content.return_value = sample_content
        self.blob_service.container_name = "test-container"

        # Create mock request
        req = func.HttpRequest(
            method="GET",
            url=f"/api/files/{self.file_id}/download",
            route_params={"file_id": self.file_id},
            headers={"X-MS-CLIENT-PRINCIPAL": self.encoded_claims},
            body=None,
        )

        # Call the function
        response = _download_file(req, self.blob_service, self.repository)

        # Assert response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_body(), sample_content)
        self.assertEqual(response.headers["Content-Type"], "application/pdf")
        self.assertEqual(
            response.headers["Content-Disposition"],
            'attachment; filename="test_document.pdf"',
        )

        # Assert calls
        self.repository.get_file_by_id.assert_called_once_with(
            self.user_id, self.file_id
        )
        self.blob_service.get_file_content.assert_called_once_with(
            container_name=self.blob_service.container_name,
            filename=file_metadata.filename,
        )

    def test_download_file_missing_file_id(self):
        """Test download with missing file_id."""
        # Create mock request without file_id
        req = func.HttpRequest(
            method="GET",
            url="/api/files/download",
            route_params={},  # Missing file_id
            headers={"X-MS-CLIENT-PRINCIPAL": self.encoded_claims},
            body=None,
        )

        # Call the function and expect ValidationError
        with self.assertRaises(ValidationError) as context:
            _download_file(req, self.blob_service, self.repository)

        # Assert the error message
        self.assertEqual(str(context.exception), "File ID is required")

        # Verify no service calls were made
        self.repository.get_file_by_id.assert_not_called()
        self.blob_service.get_file_content.assert_not_called()

    def test_download_file_not_found(self):
        """Test download with non-existent file_id."""
        # Configure mock repository
        self.repository.get_file_by_id.return_value = None

        # Create mock request
        req = func.HttpRequest(
            method="GET",
            url=f"/api/files/{self.file_id}/download",
            route_params={"file_id": self.file_id},
            headers={"X-MS-CLIENT-PRINCIPAL": self.encoded_claims},
            body=None,
        )

        # Call the function
        with self.assertRaises(FileNotFoundError) as context:
            response = _download_file(req, self.blob_service, self.repository)

        # check that context.exception.message contains File * not found
        self.assertTrue(str(context.exception).startswith("File"))
        self.assertTrue(str(context.exception).endswith("not found"))

        # Verify no service calls were made
        self.repository.get_file_by_id.assert_called_once_with(
            self.user_id, self.file_id
        )
        self.blob_service.get_file_content.assert_not_called()

    def test_download_file_missing_claims(self):
        """Test download with missing user claims."""
        # Create mock request without claims
        req = func.HttpRequest(
            method="GET",
            url=f"/api/files/{self.file_id}/download",
            route_params={"file_id": self.file_id},
            headers={},  # No claims header
            body=None,
        )

        # Call the function
        with self.assertRaises(UnauthorizedError) as context:
            response = _download_file(req, self.blob_service, self.repository)

        # check that context.exception.message contains Unauthorized
        self.assertEqual(str(context.exception), "Missing user claims")

        # Verify no service calls were made
        self.repository.get_file_by_id.assert_not_called()
        self.blob_service.get_file_content.assert_not_called()


if __name__ == "__main__":
    unittest.main()
