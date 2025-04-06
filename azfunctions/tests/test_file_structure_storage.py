import unittest
import uuid
from unittest.mock import MagicMock, patch

import pytest
from file_processing.file_processing import FileProcessor
from file_processing.schemas import FileProcessingRequest
from shared.models import (
    FileMetadataDb,
    FileStatus,
    FileType,
)
from shared.openai_service.models import (
    CVStructure,
    CVStructureLoose,
    DocumentAnalysis,
    DocumentType,
    PersonalDetail,
)
from shared.openai_service.models import DocumentType as OpenAIDocumentType


class TestFileStructureStorage(unittest.TestCase):
    """
    Tests to verify that document_analysis data is properly stored at the top level.
    This reproduces the issue where document_analysis is nested instead of flattened.
    """

    def setUp(self):
        """Set up test environment."""
        # Create mock services
        self.mock_repository = MagicMock()
        self.mock_blob_service = MagicMock()
        self.mock_document_intelligence_service = MagicMock()
        self.mock_openai_service = MagicMock()
        self.mock_queue_service = MagicMock()

        # Create the processor with mock services
        self.processor = FileProcessor(
            repository=self.mock_repository,
            blob_service=self.mock_blob_service,
            document_intelligence_service=self.mock_document_intelligence_service,
            openai_service=self.mock_openai_service,
            queue_service=self.mock_queue_service,
        )

    @pytest.mark.external_services
    def test_file_processing_stores_document_fields(self):
        """
        Test that file processing correctly stores document_type and structure fields.
        """
        # Create a test CV document analysis with structure
        cv_structure = CVStructureLoose(
            personal_details=[
                PersonalDetail(type="Name", text="John Doe"),
                PersonalDetail(type="Email", text="john@example.com"),
            ],
            professional_summary="Experienced professional",
            skills=["Python", "Azure", "Testing"],
            experience=[],
            education=[],
            job_title="Software Engineer",
            additional_information=["Languages: English, Spanish"],
        )

        document_analysis = DocumentAnalysis(
            document_type=OpenAIDocumentType.CV, structure=cv_structure
        )

        # Create a request object
        test_request = FileProcessingRequest(
            id=uuid.uuid4(),
            user_id="test-user-123",
            filename="test_cv.pdf",
            url="http://example.com/test_cv.pdf",
            type=FileType.CV,
        )

        # Set up the mocks to return expected values
        self.mock_blob_service.get_file_content.return_value = b"test file content"

        self.mock_document_intelligence_service.get_text_from_pdf.return_value = {
            "text": "Test document text",
            "pages": [],
            "paragraphs": ["Test paragraph"],
        }

        self.mock_openai_service.analyze_document.return_value = document_analysis

        # Keep track of what's been saved to the repository
        saved_metadata = None

        def mock_upsert_file(file_data):
            nonlocal saved_metadata
            saved_metadata = file_data
            return file_data

        self.mock_repository.upsert_file.side_effect = mock_upsert_file

        # Call the process method
        result = self.processor.process(test_request)

        # Verify that the file was processed correctly
        self.assertTrue(self.mock_repository.upsert_file.called)

        # Print the saved metadata for debugging
        print("Saved metadata:", saved_metadata)

        # Verify the document_type and structure fields in the JSON data
        self.assertIn("document_type", saved_metadata)
        self.assertEqual(
            saved_metadata["document_type"], str(OpenAIDocumentType.CV.value)
        )

        # Verify the structure field
        self.assertIn("structure", saved_metadata)
        self.assertIsNotNone(saved_metadata["structure"])

        # Verify structure contains expected data
        self.assertIn("personal_details", saved_metadata["structure"])
        self.assertIn("professional_summary", saved_metadata["structure"])
        self.assertIn("skills", saved_metadata["structure"])

        # Verify document_analysis field is completely gone
        self.assertNotIn("document_analysis", saved_metadata)


if __name__ == "__main__":
    unittest.main()
