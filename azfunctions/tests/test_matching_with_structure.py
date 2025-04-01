import unittest
import uuid
from unittest.mock import MagicMock, patch

import pytest
from matching.matching import MatchProcessor
from matching.schemas import FileType, MatchingRequestMessage
from shared.models import (
    FileMetadataDb,
    FileStatus,
)
from shared.openai_service.models import (
    CandidateCapabilities,
    CompanyDetail,
    CVMatch,
    CVStructure,
    DocumentAnalysis,
    DocumentType,
    JDRequirements,
    JDStructure,
    MatchingResultModel,
    PersonalDetail,
)


class TestMatchingWithStructure(unittest.TestCase):
    """
    Tests to verify that matching uses structured data properly instead of relying on raw text.
    This reproduces the issue where matching fails because text is null but structure is available.
    """

    def setUp(self):
        """Set up test environment."""
        # Create mock services
        self.mock_files_repository = MagicMock()
        self.mock_matching_results_repository = MagicMock()
        self.mock_user_repository = MagicMock()
        self.mock_openai_service = MagicMock()

        # Create the processor with mock services
        self.processor = MatchProcessor(
            files_repository=self.mock_files_repository,
            matching_results_repository=self.mock_matching_results_repository,
            user_repository=self.mock_user_repository,
            openai_service=self.mock_openai_service,
        )

    @pytest.mark.external_services
    def test_matching_with_structure_and_text(self):
        """
        Test that matching can process files that have both structure and text.
        This verifies that the matching processor properly uses structured data along with text.
        """
        # Test user and file IDs
        test_user_id = "test-user-123"
        cv_file_id = str(uuid.uuid4())
        jd_file_id = str(uuid.uuid4())

        # Create a CV file with structure but no text
        cv_structure = CVStructure(
            personal_details=[PersonalDetail(type="Name", text="John Doe")],
            professional_summary="Experienced software developer",
            skills=["Python", "Azure", "ML"],
            experience=[],
            education=[],
            job_title="Senior Developer",
            additional_information=[],
        )

        # Generate text content from the structure for realistic test data
        cv_text = """
John Doe
Experienced software developer

Professional Summary:
Experienced software developer with expertise in Python, Azure, and ML.

Skills:
- Python
- Azure
- ML

Job Title: Senior Developer
"""

        # Create a CV file with both text and structure
        cv_file = FileMetadataDb(
            id=uuid.UUID(cv_file_id),
            user_id=test_user_id,
            filename="test_cv.pdf",
            type=FileType.CV,
            url="http://example.com/test_cv.pdf",
            text=cv_text,  # Now has proper text content
            status=FileStatus.COMPLETED,
            status_message="File processing completed",
            document_type=DocumentType.CV,
            structure=cv_structure.model_dump(mode="json"),
        )

        # Create a JD file with structure but no text
        jd_structure = JDStructure(
            job_title="Senior Python Developer",
            company_details=[
                CompanyDetail(type="Company Name", text="Test Company Inc.")
            ],
            role_summary="We're looking for an experienced Python developer",
            required_skills=["Python", "Cloud", "ML"],
            experience_requirements=["5+ years of experience"],
            education_requirements=["Bachelor's degree"],
            additional_information=[],
        )

        # Generate text content from the structure for realistic test data
        jd_text = """
Senior Python Developer at Test Company Inc.

Role Summary:
We're looking for an experienced Python developer

Required Skills:
- Python
- Cloud
- ML

Experience Requirements:
- 5+ years of experience

Education Requirements:
- Bachelor's degree
"""

        # Create a JD file with both text and structure
        jd_file = FileMetadataDb(
            id=uuid.UUID(jd_file_id),
            user_id=test_user_id,
            filename="test_jd.pdf",
            type=FileType.JD,
            url="http://example.com/test_jd.pdf",
            text=jd_text,  # Now has proper text content
            status=FileStatus.COMPLETED,
            status_message="File processing completed",
            document_type=DocumentType.JD,
            structure=jd_structure.model_dump(mode="json"),
        )

        # Setup mock responses
        self.mock_files_repository.get_file_by_id.return_value = cv_file
        self.mock_files_repository.get_files_from_db.return_value = [jd_file]

        # Add debug prints to verify structure field is not None
        print(f"CV file structure: {cv_file.structure is not None}")
        print(f"JD file structure: {jd_file.structure is not None}")

        # Check hasattr as the matching code does
        print(f"CV has structure attribute: {hasattr(cv_file, 'structure')}")
        print(f"JD has structure attribute: {hasattr(jd_file, 'structure')}")

        # Mock the matching result from OpenAI
        mock_matching_result = MatchingResultModel(
            jd_requirements=JDRequirements(
                skills=["Python", "Cloud", "ML"],
                experience=["5+ years of experience"],
                education=["Bachelor's degree"],
            ),
            candidate_capabilities=CandidateCapabilities(
                skills=["Python", "Azure", "ML"],
                experience=["Experienced software developer"],
                education=[],
            ),
            cv_match=CVMatch(
                skills_match=["Python", "ML"],
                experience_match=["Experienced developer"],
                education_match=[],
                gaps=["Cloud experience"],
            ),
            overall_match_percentage=75.0,
        )
        self.mock_openai_service.match_cv_and_jd.return_value = mock_matching_result

        # Create the matching request
        request = MatchingRequestMessage(
            file_id=cv_file_id,
            user_id=test_user_id,
            filename="test_cv.pdf",
            url="http://example.com/test_cv.pdf",
            type=FileType.CV,
        )

        # Call the match method - this should succeed if structured data is properly used
        self.processor.match(request)

        # Verify that OpenAI service was called with correctly extracted text
        self.mock_openai_service.match_cv_and_jd.assert_called_once()

        # Get the arguments that were passed to match_cv_and_jd
        args, kwargs = self.mock_openai_service.match_cv_and_jd.call_args

        # Verify the extracted text contains structure data
        cv_text = kwargs.get("cv_text", "")
        jd_text = kwargs.get("jd_text", "")

        # Check that the structure data was correctly converted to text
        self.assertIn("John Doe", cv_text)
        self.assertIn("Experienced software developer", cv_text)
        self.assertIn("Python", cv_text)

        self.assertIn("Senior Python Developer", jd_text)
        self.assertIn("We're looking for an experienced Python developer", jd_text)
        self.assertIn("5+ years of experience", jd_text)

        # Verify that a matching result was stored
        self.mock_matching_results_repository.upsert_result.assert_called_once()


if __name__ == "__main__":
    unittest.main()
