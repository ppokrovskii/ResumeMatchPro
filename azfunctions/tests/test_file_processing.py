import json
import os
import pytest
import logging
import io
from uuid import uuid4
from pydantic import ValidationError
from unittest import TestCase
from unittest.mock import patch, MagicMock
import tempfile
from docx import Document
from pathlib import Path
from dotenv import load_dotenv

# Load test environment variables
load_dotenv(Path(__file__).parent / ".env.test")

from file_processing.file_processing import process_file
from file_processing.schemas import FileProcessingRequest, FileType
from shared.document_intelligence_service import DocumentIntelligenceService
from shared.docx_service import DocxService
from shared.models import DocumentPage, DocumentStyle
from shared.openai_service.openai_service import OpenAIService
from shared.openai_service.models import DocumentAnalysis, DocumentStructure

class TestFileProcessing(TestCase):
    def setUp(self):
        # Set up logging
        self.log_stream = io.StringIO()
        self.log_handler = logging.StreamHandler(self.log_stream)
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.INFO)

        # Create mock instances
        self.mock_blob_service_instance = MagicMock()
        self.mock_doc_intelligence_instance = MagicMock()
        self.mock_queue_service_instance = MagicMock()
        self.mock_files_repository_instance = MagicMock()
        self.mock_cosmos_db_instance = MagicMock()
        self.mock_openai_service_instance = MagicMock()

        # Configure mock instances
        self.mock_blob_service_instance.container_name = "test-container"
        self.mock_blob_service_instance.get_file_content.return_value = b"test content"
        
        # Mock DocumentAnalysisClient
        self.mock_client = MagicMock()
        self.mock_poller = MagicMock()
        self.mock_result = MagicMock()
        self.mock_poller.result.return_value = self.mock_result
        self.mock_client.begin_analyze_document.return_value = self.mock_poller
        self.mock_doc_intelligence_instance.client = self.mock_client
        self.mock_doc_intelligence_instance.process_analysis_result.return_value = {
            'text': "extracted text",
            'pages': [],
            'paragraphs': [],
            'tables': [],
            'styles': {},
            'headers': None,
            'footers': None
        }
        self.mock_queue_service_instance.create_queue_if_not_exists.return_value = None
        self.mock_queue_service_instance.send_message.return_value = None
        self.mock_files_repository_instance.upsert_file.return_value = None

        # Start patching services
        self.blob_service_patcher = patch('file_processing.file_processing.FilesBlobService')
        self.doc_intelligence_patcher = patch('file_processing.file_processing.DocumentIntelligenceService')
        self.queue_service_patcher = patch('file_processing.file_processing.QueueService')
        self.get_cosmos_db_client_patcher = patch('file_processing.file_processing.get_cosmos_db_client')
        self.files_repository_patcher = patch('file_processing.file_processing.FilesRepository')
        self.docx_service_patcher = patch('file_processing.file_processing.DocxService')
        self.openai_service_patcher = patch('file_processing.file_processing.OpenAIService')

        # Start the patches and configure returns
        self.mock_blob_service = self.blob_service_patcher.start()
        self.mock_doc_intelligence = self.doc_intelligence_patcher.start()
        self.mock_queue_service = self.queue_service_patcher.start()
        self.mock_get_cosmos_db_client = self.get_cosmos_db_client_patcher.start()
        self.mock_files_repository = self.files_repository_patcher.start()
        self.mock_docx_service = self.docx_service_patcher.start()
        self.mock_openai_service = self.openai_service_patcher.start()

        # Configure the mocks to return our instances
        self.mock_blob_service.return_value = self.mock_blob_service_instance
        self.mock_doc_intelligence.return_value = self.mock_doc_intelligence_instance
        self.mock_queue_service.return_value = self.mock_queue_service_instance
        self.mock_files_repository.return_value = self.mock_files_repository_instance
        self.mock_get_cosmos_db_client.return_value = self.mock_cosmos_db_instance
        self.mock_docx_service.get_text_from_docx.return_value = {
            'text': "extracted text from docx",
            'pages': [],
            'paragraphs': [],
            'tables': [],
            'styles': {},
            'headers': [],
            'footers': []
        }
        self.mock_openai_service.return_value = self.mock_openai_service_instance

    def tearDown(self):
        # Stop all patches
        self.blob_service_patcher.stop()
        self.doc_intelligence_patcher.stop()
        self.queue_service_patcher.stop()
        self.get_cosmos_db_client_patcher.stop()
        self.files_repository_patcher.stop()
        self.docx_service_patcher.stop()
        self.openai_service_patcher.stop()

        # Clean up logging
        logging.getLogger().removeHandler(self.log_handler)
        self.log_stream.close()

    def test_process_file_missing_user_id(self):
        # Verify that FileProcessingRequest requires user_id
        with pytest.raises(ValidationError) as exc_info:
            message = FileProcessingRequest(
                filename="test.pdf",
                type=FileType.CV,
                id=uuid4(),
                url="https://example.com/test.pdf"
            )
        
        # Verify the error message
        assert "user_id" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)

        # Create a valid message with user_id
        message = FileProcessingRequest(
            filename="test.pdf",
            type=FileType.CV,
            id=uuid4(),
            url="https://example.com/test.pdf",
            user_id="test_user"
        )

        # Mock OpenAI analysis result
        mock_cv_analysis = DocumentAnalysis(
            document_type="CV",
            structure=DocumentStructure(
                personal_details=[{"type": "name", "text": "John Doe"}],
                professional_summary="Experienced software engineer",
                skills=["Python", "Azure", "Machine Learning"],
                experience=[{
                    "title": "Senior Developer",
                    "start_date": "2020-01",
                    "end_date": "2023-12",
                    "lines": ["Led development team", "Implemented CI/CD"]
                }],
                education=[{
                    "title": "Computer Science",
                    "start_date": "2016-09",
                    "end_date": "2020-05",
                    "degree": "Bachelor's",
                    "details": "First Class Honours",
                    "city": "London"
                }]
            )
        )
        self.mock_openai_service_instance.analyze_document.return_value = mock_cv_analysis

        # Create queue message
        msg = MagicMock()
        msg.get_json.return_value = json.loads(message.model_dump_json())
        msg.get_body.return_value = message.model_dump_json().encode('utf-8')

        # Get the actual function from the blueprint
        func_call = process_file.build().get_user_function()

        # Call the function - it should not raise an error
        func_call(msg)

        # Print logs for debugging
        print("\nTest Logs:")
        print(self.log_stream.getvalue())

        # Verify that the file was processed
        self.mock_blob_service_instance.get_file_content.assert_called_once_with(
            self.mock_blob_service_instance.container_name,
            message.filename
        )

        # Verify that the document was analyzed
        self.mock_client.begin_analyze_document.assert_called_once_with("prebuilt-layout", document=b"test content")
        self.mock_doc_intelligence_instance.process_analysis_result.assert_called_once_with(self.mock_result)

        # Verify that the file metadata was saved
        self.mock_files_repository_instance.upsert_file.assert_called_once()
        file_metadata_call = self.mock_files_repository_instance.upsert_file.call_args[0][0]
        assert file_metadata_call["text"] == "extracted text"
        assert file_metadata_call["filename"] == message.filename
        assert file_metadata_call["type"] == message.type
        assert file_metadata_call["user_id"] == message.user_id
        assert file_metadata_call["url"] == message.url
        assert file_metadata_call["document_analysis"]["document_type"] == mock_cv_analysis.document_type
        assert file_metadata_call["document_analysis"]["structure"]["personal_details"] == [{"type": "name", "text": "John Doe"}]
        assert file_metadata_call["document_analysis"]["structure"]["professional_summary"] == "Experienced software engineer"
        assert file_metadata_call["document_analysis"]["structure"]["skills"] == ["Python", "Azure", "Machine Learning"]

        # Verify that the queue message was sent
        self.mock_queue_service_instance.create_queue_if_not_exists.assert_called_once_with("matching-queue")
        self.mock_queue_service_instance.send_message.assert_called_once()

    def test_process_file_document_intelligence_timeout(self):
        """Test handling of Document Intelligence service timeout"""
        # Configure Document Intelligence service to raise the timeout error
        self.mock_doc_intelligence_instance.client.begin_analyze_document.side_effect = Exception("Operation timed out")
        
        # Create a test message with a PDF file
        message = FileProcessingRequest(
            filename="test_timeout.pdf",
            type=FileType.CV,
            id=uuid4(),
            url="https://example.com/test_timeout.pdf",
            user_id="test_user"
        )
        
        # Create queue message
        msg = MagicMock()
        msg.get_json.return_value = json.loads(message.model_dump_json())
        msg.get_body.return_value = message.model_dump_json().encode('utf-8')
        
        # Get the actual function from the blueprint
        func_call = process_file.build().get_user_function()
        
        # Call the function - it should raise an exception
        with pytest.raises(Exception) as exc_info:
            func_call(msg)
        
        assert "Operation timed out" in str(exc_info.value)
        
        # Verify that the file was not saved to the database
        self.mock_files_repository_instance.upsert_file.assert_not_called()
        
        # Verify that no message was sent to the matching queue
        self.mock_queue_service_instance.send_message.assert_not_called()
        
        # Print logs for debugging
        print("\nTest Logs:")
        print(self.log_stream.getvalue())

    def test_process_file_with_cv_analysis(self):
        """Test processing a CV file with OpenAI analysis"""
        # Mock OpenAI analysis result
        mock_cv_analysis = DocumentAnalysis(
            document_type="CV",
            structure=DocumentStructure(
                personal_details=[{"type": "name", "text": "John Doe"}],
                professional_summary="Experienced software engineer",
                skills=["Python", "Azure", "Machine Learning"],
                experience=[{
                    "title": "Senior Developer",
                    "start_date": "2020-01",
                    "end_date": "2023-12",
                    "lines": ["Led development team", "Implemented CI/CD"]
                }],
                education=[{
                    "title": "Computer Science",
                    "start_date": "2016-09",
                    "end_date": "2020-05",
                    "degree": "Bachelor's",
                    "details": "First Class Honours",
                    "city": "London"
                }]
            )
        )
        self.mock_openai_service_instance.analyze_document.return_value = mock_cv_analysis

        # Create a test message
        message = FileProcessingRequest(
            filename="test_cv.pdf",
            type=FileType.CV,
            id=uuid4(),
            url="https://example.com/test_cv.pdf",
            user_id="test_user"
        )

        # Create queue message
        msg = MagicMock()
        msg.get_json.return_value = json.loads(message.model_dump_json())
        msg.get_body.return_value = message.model_dump_json().encode('utf-8')

        # Get the function from the blueprint
        func_call = process_file.build().get_user_function()

        # Call the function
        func_call(msg)

        # Verify OpenAI service was called
        self.mock_openai_service_instance.analyze_document.assert_called_once()
        call_args = self.mock_openai_service_instance.analyze_document.call_args[1]
        self.assertEqual(call_args['text'], "extracted text")

        # Verify file metadata was saved with analysis results
        saved_metadata = self.mock_files_repository_instance.upsert_file.call_args[0][0]
        self.assertEqual(saved_metadata['type'], FileType.CV)
        self.assertEqual(saved_metadata['filename'], "test_cv.pdf")
        self.assertEqual(saved_metadata['user_id'], "test_user")

    def test_process_file_with_jd_analysis(self):
        """Test processing a Job Description file with OpenAI analysis"""
        # Mock OpenAI analysis result
        mock_jd_analysis = DocumentAnalysis(
            document_type="JD",
            structure=DocumentStructure(
                personal_details=[{"type": "company", "text": "Tech Corp"}],
                professional_summary="Looking for a senior developer",
                skills=["Python", "Azure", "Leadership"],
                experience=[{
                    "title": "Requirements",
                    "start_date": "2024-01",
                    "lines": ["5+ years experience", "Team leadership"]
                }],
                education=[{
                    "title": "Education Requirements",
                    "start_date": "2024-01",
                    "degree": "Bachelor's in Computer Science",
                    "details": "Or equivalent experience"
                }]
            )
        )
        self.mock_openai_service_instance.analyze_document.return_value = mock_jd_analysis

        # Create a test message
        message = FileProcessingRequest(
            filename="test_jd.pdf",
            type=FileType.JD,
            id=uuid4(),
            url="https://example.com/test_jd.pdf",
            user_id="test_user"
        )

        # Create queue message
        msg = MagicMock()
        msg.get_json.return_value = json.loads(message.model_dump_json())
        msg.get_body.return_value = message.model_dump_json().encode('utf-8')

        # Get the function from the blueprint
        func_call = process_file.build().get_user_function()

        # Call the function
        func_call(msg)

        # Verify OpenAI service was called
        self.mock_openai_service_instance.analyze_document.assert_called_once()
        call_args = self.mock_openai_service_instance.analyze_document.call_args[1]
        self.assertEqual(call_args['text'], "extracted text")

        # Verify file metadata was saved with analysis results
        saved_metadata = self.mock_files_repository_instance.upsert_file.call_args[0][0]
        self.assertEqual(saved_metadata['type'], FileType.JD)
        self.assertEqual(saved_metadata['filename'], "test_jd.pdf")
        self.assertEqual(saved_metadata['user_id'], "test_user")

    def test_process_file_openai_error(self):
        """Test handling of OpenAI service errors"""
        # Configure OpenAI service to raise an error
        self.mock_openai_service_instance.analyze_document.side_effect = Exception("OpenAI API error")

        # Create a test message
        message = FileProcessingRequest(
            filename="test.pdf",
            type=FileType.CV,
            id=uuid4(),
            url="https://example.com/test.pdf",
            user_id="test_user"
        )

        # Create queue message
        msg = MagicMock()
        msg.get_json.return_value = json.loads(message.model_dump_json())
        msg.get_body.return_value = message.model_dump_json().encode('utf-8')

        # Get the function from the blueprint
        func_call = process_file.build().get_user_function()

        # Call the function - it should raise an exception
        with self.assertRaises(Exception) as context:
            func_call(msg)

        self.assertIn("OpenAI API error", str(context.exception))

        # Verify the error was logged
        log_output = self.log_stream.getvalue()
        self.assertIn("Error processing document: OpenAI API error", log_output)

        # Verify no message was sent to the matching queue
        self.mock_queue_service_instance.send_message.assert_not_called()

