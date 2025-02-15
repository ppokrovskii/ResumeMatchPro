import json
import os
import azure.functions as func
import pytest
import logging
import io
from uuid import uuid4
from azure.cosmos import CosmosClient
from pydantic import ValidationError
from unittest import TestCase
from unittest.mock import patch, MagicMock, call

from file_processing.file_processing import process_file
from file_processing.schemas import FileProcessingRequest, FileType
from file_upload.schemas import FileUploadOutputQueueMessage

class TestFileProcessing(TestCase):
    def setUp(self):
        # Set up logging
        self.log_stream = io.StringIO()
        self.log_handler = logging.StreamHandler(self.log_stream)
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.INFO)

        # Set up environment variables
        os.environ["AZURE_DOCUMENT_INTELLIGENCE_KEY"] = "test-key"
        os.environ["AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"] = "test-endpoint"
        os.environ["AZURE_STORAGE_CONNECTION_STRING"] = "test-connection-string"

        # Create mock instances
        self.mock_blob_service_instance = MagicMock()
        self.mock_doc_intelligence_instance = MagicMock()
        self.mock_queue_service_instance = MagicMock()
        self.mock_files_repository_instance = MagicMock()
        self.mock_cosmos_db_instance = MagicMock()

        # Configure mock instances
        self.mock_blob_service_instance.container_name = "test-container"
        self.mock_blob_service_instance.get_file_content.return_value = b"test content"
        self.mock_doc_intelligence_instance.get_text_from_pdf.return_value = "extracted text"
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
        self.mock_docx_service.get_text_from_docx.return_value = "extracted text from docx"

    def tearDown(self):
        # Clean up environment variables
        del os.environ["AZURE_DOCUMENT_INTELLIGENCE_KEY"]
        del os.environ["AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"]
        del os.environ["AZURE_STORAGE_CONNECTION_STRING"]

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

        # Verify that the text was extracted
        self.mock_doc_intelligence_instance.get_text_from_pdf.assert_called_once_with(b"test content")

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