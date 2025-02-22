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

        # Start the patches and configure returns
        self.mock_blob_service = self.blob_service_patcher.start()
        self.mock_doc_intelligence = self.doc_intelligence_patcher.start()
        self.mock_queue_service = self.queue_service_patcher.start()
        self.mock_get_cosmos_db_client = self.get_cosmos_db_client_patcher.start()
        self.mock_files_repository = self.files_repository_patcher.start()
        self.mock_docx_service = self.docx_service_patcher.start()

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

    def tearDown(self):
        # Stop all patches
        self.blob_service_patcher.stop()
        self.doc_intelligence_patcher.stop()
        self.queue_service_patcher.stop()
        self.get_cosmos_db_client_patcher.stop()
        self.files_repository_patcher.stop()
        self.docx_service_patcher.stop()

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

class TestStructuredDocumentProcessing(TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a test DOCX file with various formatting
        cls.docx_path = os.path.join(tempfile.gettempdir(), "test_document.docx")
        doc = Document()
        
        # Add a header
        header = doc.sections[0].header
        header.paragraphs[0].text = "Test Document Header"
        
        # Add a footer
        footer = doc.sections[0].footer
        footer.paragraphs[0].text = "Test Document Footer"
        
        # Add different styles of text
        heading = doc.add_heading('Test Document Title', level=1)
        doc.add_paragraph('This is a normal paragraph.')
        
        # Add bold and italic text
        p = doc.add_paragraph()
        p.add_run('This is bold text.').bold = True
        p.add_run(' This is italic text.').italic = True
        
        # Add a table
        table = doc.add_table(rows=2, cols=2)
        table.style = 'Table Grid'
        cell_data = [['Header 1', 'Header 2'], ['Data 1', 'Data 2']]
        for i in range(2):
            for j in range(2):
                table.cell(i, j).text = cell_data[i][j]
        
        # Save the document
        doc.save(cls.docx_path)
        
        # Read the document content
        with open(cls.docx_path, 'rb') as f:
            cls.docx_content = f.read()
    
    @classmethod
    def tearDownClass(cls):
        # Clean up the test file
        if os.path.exists(cls.docx_path):
            os.remove(cls.docx_path)
    
    def test_docx_structured_processing(self):
        """Test structured information extraction from DOCX file"""
        # Process the document
        structured_info = DocxService.get_text_from_docx(self.docx_content)
        
        # Verify basic structure
        self.assertIsInstance(structured_info, dict)
        self.assertIn('text', structured_info)
        self.assertIn('pages', structured_info)
        self.assertIn('paragraphs', structured_info)
        self.assertIn('tables', structured_info)
        self.assertIn('styles', structured_info)
        self.assertIn('headers', structured_info)
        self.assertIn('footers', structured_info)
        
        # Verify content
        self.assertGreater(len(structured_info['text']), 0)
        self.assertEqual(len(structured_info['pages']), 1)  # DOCX doesn't provide page info
        self.assertGreater(len(structured_info['paragraphs']), 0)
        self.assertEqual(len(structured_info['tables']), 1)
        self.assertGreater(len(structured_info['styles']), 0)
        
        # Verify table content
        self.assertEqual(len(structured_info['tables'][0]), 2)  # 2 rows
        self.assertEqual(len(structured_info['tables'][0][0]), 2)  # 2 columns
        self.assertEqual(structured_info['tables'][0][0][0].text, 'Header 1')
        self.assertEqual(structured_info['tables'][0][0][1].text, 'Header 2')
        self.assertEqual(structured_info['tables'][0][1][0].text, 'Data 1')
        self.assertEqual(structured_info['tables'][0][1][1].text, 'Data 2')
        
        # Verify header and footer
        self.assertIn('Test Document Header', structured_info['headers'][0])
        self.assertIn('Test Document Footer', structured_info['footers'][0])
    
    @pytest.mark.skipif(
        not os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY") or not os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"),
        reason="Azure Document Intelligence credentials not available"
    )
    def test_pdf_structured_processing(self):
        """Test structured information extraction from PDF file using Azure Document Intelligence"""
        # Create a PDF file from our DOCX for testing
        from subprocess import run
        pdf_path = self.docx_path.replace('.docx', '.pdf')
        
        try:
            # Try to convert DOCX to PDF using LibreOffice (if available)
            result = run(['soffice', '--headless', '--convert-to', 'pdf', self.docx_path, '--outdir', os.path.dirname(pdf_path)])
            
            if result.returncode == 0 and os.path.exists(pdf_path):
                # Read the PDF content
                with open(pdf_path, 'rb') as f:
                    pdf_content = f.read()
                
                # Process the PDF
                document_intelligence_service = DocumentIntelligenceService(
                    key=os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY"),
                    endpoint=os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
                )
                structured_info = document_intelligence_service.get_text_from_pdf(pdf_content)
                
                # Verify basic structure
                self.assertIsInstance(structured_info, dict)
                self.assertIn('text', structured_info)
                self.assertIn('pages', structured_info)
                self.assertIn('paragraphs', structured_info)
                self.assertIn('tables', structured_info)
                self.assertIn('styles', structured_info)
                
                # Verify content
                self.assertGreater(len(structured_info['text']), 0)
                self.assertGreater(len(structured_info['pages']), 0)
                self.assertGreater(len(structured_info['paragraphs']), 0)
                
                # Clean up
                os.remove(pdf_path)
            else:
                pytest.skip("LibreOffice not available for PDF conversion")
        except FileNotFoundError:
            pytest.skip("LibreOffice not available for PDF conversion") 