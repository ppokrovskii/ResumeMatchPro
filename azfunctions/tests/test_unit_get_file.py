import unittest
from unittest.mock import MagicMock, patch
import json
import base64
import azure.functions as func
from user_files.user_files import _get_file
from shared.openai_service.models import DocumentAnalysis, DocumentStructure
from shared.models import FileMetadataDb, FileType
from uuid import uuid4

class TestGetFile(unittest.TestCase):
    
    def setUp(self):
        # Create a mock repository
        self.repository = MagicMock()
        
        # Create sample data
        self.user_id = "test-user-123"
        self.file_id = str(uuid4())
        
        # Create mock claims
        mock_claims = {
            "claims": [
                {"typ": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier", "val": self.user_id}
            ]
        }
        self.encoded_claims = base64.b64encode(json.dumps(mock_claims).encode()).decode()
        
    def test_get_file_success_with_structure(self):
        """Test get_file with document_analysis structure."""
        # Create sample document structure
        structure = DocumentStructure(
            personal_details=[{"type": "name", "text": "John Doe"}],
            professional_summary="Software Engineer",
            skills=["Python", "Azure"],
            experience=[{
                "title": "Developer",
                "start_date": "2020",
                "end_date": "Present",
                "lines": ["Developed stuff"]
            }],
            education=[],
            additional_information=[]
        )
        
        # Create document analysis
        document_analysis = DocumentAnalysis(
            document_type="CV",
            structure=structure
        )
        
        # Create file metadata
        file_metadata = FileMetadataDb(
            id=self.file_id,
            filename="test_cv.pdf",
            type=FileType.CV,
            user_id=self.user_id,
            url="https://test.blob.core.windows.net/test_cv.pdf",
            document_analysis=document_analysis
        )
        
        # Configure mock repository
        self.repository.get_file_by_id.return_value = file_metadata
        
        # Create mock request
        req = func.HttpRequest(
            method='GET',
            url=f'/api/files/{self.file_id}',
            route_params={'file_id': self.file_id},
            headers={
                'X-MS-CLIENT-PRINCIPAL': self.encoded_claims
            },
            body=None
        )
        
        # Call the function
        response = _get_file(req, self.repository)
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.get_body())
        
        # Verify structure fields
        self.assertIn('structure', result)
        self.assertEqual(result['structure']['personal_details'][0]['text'], "John Doe")
        self.assertEqual(result['structure']['skills'], ["Python", "Azure"])
    
    def test_get_file_missing_file_id(self):
        """Test get_file with missing file_id."""
        # Create mock request without file_id
        req = func.HttpRequest(
            method='GET',
            url='/api/files/',
            route_params={},  # Missing file_id
            headers={
                'X-MS-CLIENT-PRINCIPAL': self.encoded_claims
            },
            body=None
        )
        
        # Call the function
        response = _get_file(req, self.repository)
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        result = json.loads(response.get_body())
        self.assertEqual(result['error'], "file_id is required")
    
    def test_get_file_not_found(self):
        """Test get_file with non-existent file_id."""
        # Configure mock repository
        self.repository.get_file_by_id.return_value = None
        
        # Create mock request
        req = func.HttpRequest(
            method='GET',
            url=f'/api/files/{self.file_id}',
            route_params={'file_id': self.file_id},
            headers={
                'X-MS-CLIENT-PRINCIPAL': self.encoded_claims
            },
            body=None
        )
        
        # Call the function
        response = _get_file(req, self.repository)
        
        # Assert response
        self.assertEqual(response.status_code, 404)
        result = json.loads(response.get_body())
        self.assertEqual(result['error'], "File not found")

if __name__ == '__main__':
    unittest.main() 