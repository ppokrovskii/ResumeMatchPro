"""
Tests for schema compatibility between different modules.

These tests ensure that the data structures used to communicate between
different parts of the system are compatible, preventing issues like the one
where file_processing was sending file_id while match_resume was expecting id.
"""
import json
import pytest
import uuid
import logging
import os
import sys
from pathlib import Path

# Add the parent directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
azfunctions_dir = os.path.dirname(current_dir)
sys.path.insert(0, azfunctions_dir)  # Add the azfunctions directory to path

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the schemas
from file_processing.schemas import FileProcessingOutputQueueMessage, FileType
from matching.schemas import MatchingRequestMessage

class MockQueueMessage:
    """Mock Azure Queue Message for testing."""
    def __init__(self, message_body):
        self.message_body = message_body
    
    def get_body(self):
        if isinstance(self.message_body, str):
            return self.message_body.encode('utf-8')
        return self.message_body
    
    def get_json(self):
        """Parse the message body as JSON."""
        if isinstance(self.message_body, str):
            return json.loads(self.message_body)
        return json.loads(self.message_body.decode('utf-8'))

def test_file_processing_to_matching_compatibility():
    """
    Test that messages produced by file_processing can be consumed by the matching function.
    
    This test verifies that the field names and structure match between:
    - FileProcessingOutputQueueMessage (producer)
    - MatchingRequestMessage (consumer)
    """
    test_file_id = uuid.uuid4()
    test_user_id = "test-user-id"
    test_filename = "test-file.pdf"
    test_url = "https://example.com/test-file.pdf"
    
    # Create a message as file_processing would
    processing_message = FileProcessingOutputQueueMessage(
        file_id=test_file_id,
        user_id=test_user_id,
        type=FileType.CV,
        filename=test_filename,
        url=test_url
    )
    
    # Convert to JSON as it would be sent to queue
    message_json = processing_message.model_dump_json()
    logger.info(f"Output message JSON: {message_json}")
    
    # Parse the message as match_resume would
    queue_message = MockQueueMessage(message_json)
    matching_request = MatchingRequestMessage(**queue_message.get_json())
    
    # Verify the fields were correctly mapped
    assert str(matching_request.file_id) == str(test_file_id), "file_id field was not correctly mapped"
    assert matching_request.user_id == test_user_id, "user_id field was not correctly mapped"
    assert matching_request.filename == test_filename, "filename field was not correctly mapped"
    assert matching_request.url == test_url, "url field was not correctly mapped"
    assert matching_request.type == FileType.CV, "type field was not correctly mapped"
    
    logger.info("✅ Schema compatibility test passed")

def test_matching_validates_required_fields():
    """
    Test that the matching schema properly validates required fields.
    
    This test ensures that if any required fields are missing, validation will fail.
    """
    # Test with missing required fields
    # Note: file_id seems to have a default value in the BaseModel, so we'll test user_id, filename, and url instead
    
    # Test for user_id field (required)
    incomplete_data = {
        "file_id": str(uuid.uuid4()),
        "filename": "test.pdf",
        "type": "CV",
        "url": "https://example.com/test.pdf"
    }
    # user_id is missing from the data
    
    with pytest.raises(Exception):
        MatchingRequestMessage(**incomplete_data)
    
    # Test for filename field (required)
    incomplete_data = {
        "file_id": str(uuid.uuid4()),
        "user_id": "test-user",
        "type": "CV",
        "url": "https://example.com/test.pdf"
    }
    
    with pytest.raises(Exception):
        MatchingRequestMessage(**incomplete_data)
    
    # Test for type field (required)
    incomplete_data = {
        "file_id": str(uuid.uuid4()),
        "user_id": "test-user",
        "filename": "test.pdf",
        "url": "https://example.com/test.pdf"
    }
    
    with pytest.raises(Exception):
        MatchingRequestMessage(**incomplete_data)
    
    logger.info("✅ Field validation test passed")

if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 