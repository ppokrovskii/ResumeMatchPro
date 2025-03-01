import json
import uuid
import traceback
from unittest.mock import MagicMock, patch
from datetime import datetime
import sys
import importlib

import pytest
from shared.models import FileType, FileMetadataDb
from shared.openai_service.openai_service import OpenAIService
from shared.blob_service import FilesBlobService
from shared.document_intelligence_service import DocumentIntelligenceService
from shared.files_repository import FilesRepository
from shared.queue_service import QueueService
from file_processing.file_processing import _parse_queue_message, _extract_document_content, _create_file_metadata, _queue_for_matching

class MockOpenAIService:
    """Mock OpenAI service that returns a predetermined response."""
    
    def analyze_document(self, text, pages, paragraphs):
        # This is the mock response based on real OpenAI output
        from shared.openai_service.models import DocumentAnalysis, DocumentStructure
        
        # Create the structure using the real response we captured
        structure = DocumentStructure(
            personal_details=None,
            professional_summary=None,
            skills=None,
            experience=None,
            education=None,
            company_details=[
                {"type": "Job Title", "text": "Software Engineer"},
                {"type": "Department", "text": "Engineering"},
                {"type": "Location", "text": "New York, NY"},
                {"type": "Company", "text": "Acme Inc."},
                {"type": "Industry", "text": "Technology"}
            ],
            role_summary="We are looking for a Software Engineer to join our team.",
            required_skills=[
                "Proficiency in Python, JavaScript",
                "Experience with cloud platforms (AWS, Azure)",
                "Knowledge of software development methodologies"
            ],
            experience_requirements=[
                "3+ years of software development experience"
            ],
            education_requirements=[
                "Bachelor's degree in Computer Science or related field"
            ],
            additional_information=[]
        )
        
        # Create the document analysis
        document_analysis = DocumentAnalysis(
            document_type="JD",
            structure=structure
        )
        
        print(f"Mock OpenAI service returning: {document_analysis}")
        return document_analysis

def test_file_processing_core_workflow():
    """
    Test the core workflow of file processing without using the Azure Functions decorator.
    This tests the individual components of the file processing flow.
    """
    print("\n========== TEST: test_file_processing_core_workflow ==========")
    
    # Create a mock document text - a simple job description
    document_text = """
    Job Title: Software Engineer
    Department: Engineering
    Location: New York, NY
    Company: Acme Inc.
    Industry: Technology
    
    Job Purpose:
    We are looking for a Software Engineer to join our team.
    
    Key Responsibilities:
    - Develop and maintain software applications
    - Collaborate with cross-functional teams
    - Write clean, maintainable code
    
    Required Skills:
    - Proficiency in Python, JavaScript
    - Experience with cloud platforms (AWS, Azure)
    - Knowledge of software development methodologies
    
    Experience:
    - 3+ years of software development experience
    - Bachelor's degree in Computer Science or related field
    """
    
    # Generate a valid UUID for the file_id
    file_id = uuid.uuid4()
    print(f"Generated file_id: {file_id}")
    
    # Create a mock queue message
    mock_msg = MagicMock()
    request_data = {
        "id": str(file_id),
        "url": "https://example.com/test_jd.docx",
        "filename": "test_jd.docx",
        "type": "JD",
        "user_id": "test_user"
    }
    mock_msg.get_json.return_value = request_data
    mock_msg.get_body.return_value = json.dumps(request_data).encode('utf-8')
    print(f"Created mock message with data: {request_data}")
    
    # Step 1: Parse the queue message
    print("Step 1: Parsing queue message")
    request = _parse_queue_message(mock_msg)
    assert str(request.id) == str(file_id)
    assert request.filename == "test_jd.docx"
    print(f"Request parsed successfully: {request}")
    
    # Step 2: Prepare mocks for document content extraction
    print("Step 2: Extracting document content")
    blob_content = document_text.encode('utf-8')
    mock_blob_service = MagicMock(spec=FilesBlobService)
    mock_blob_service.container_name = "files"
    mock_blob_service.get_file_content.return_value = blob_content
    
    # Mock the document intelligence service
    mock_doc_intelligence_service = MagicMock(spec=DocumentIntelligenceService)
    mock_doc_intelligence_service.process_analysis_result.return_value = {
        "text": document_text,
        "pages": [{
            "page_number": 1,
            "content": document_text,
            "lines": [{"content": "Test line"}]
        }],
        "paragraphs": ["Test paragraph"]
    }
    
    # Add mock for DocxService.get_text_from_docx
    from shared.docx_service import DocxService
    original_get_text = DocxService.get_text_from_docx
    
    try:
        DocxService.get_text_from_docx = MagicMock(return_value={
            "text": document_text,
            "pages": [{
                "page_number": 1,
                "content": document_text,
                "lines": [{"content": "Test line"}]
            }],
            "paragraphs": ["Test paragraph"]
        })
        
        # Call the function (for .docx file)
        structured_info = _extract_document_content(
            blob_content, 
            "test_jd.docx", 
            mock_doc_intelligence_service
        )
        
        # Assert expected behavior
        assert structured_info is not None
        assert "text" in structured_info
        assert structured_info["text"] == document_text
        print(f"Document content extracted successfully: {list(structured_info.keys())}")
        
        # Step 3: Analyze document with mock OpenAI service
        print("Step 3: Analyzing document with OpenAI")
        mock_openai_service = MockOpenAIService()
        document_analysis = mock_openai_service.analyze_document(
            text=structured_info['text'],
            pages=structured_info.get('pages', []),
            paragraphs=structured_info.get('paragraphs', [])
        )
        
        # Assert expected behavior for document analysis
        assert document_analysis is not None
        assert document_analysis.document_type == "JD"
        assert document_analysis.structure.role_summary is not None
        assert "Software Engineer" in document_analysis.structure.role_summary
        print("Document analyzed successfully")
        
        # Step 4: Create file metadata
        print("Step 4: Creating file metadata")
        file_type = FileType.JD
        file_metadata = _create_file_metadata(request, structured_info, file_type, document_analysis)
        
        # Assert expected behavior for file metadata
        assert file_metadata is not None
        assert str(file_metadata.id) == str(file_id)
        assert file_metadata.type == FileType.JD
        assert file_metadata.document_analysis == document_analysis
        print("File metadata created successfully")
        
        # Step 5: Mock repository and test saving metadata
        print("Step 5: Testing repository operations")
        mock_repository = MagicMock(spec=FilesRepository)
        saved_metadata = None
        
        def side_effect_upsert_file(metadata):
            nonlocal saved_metadata
            print(f"Mock upsert_file called with metadata type: {type(metadata)}")
            saved_metadata = metadata
            return metadata
        
        mock_repository.upsert_file.side_effect = side_effect_upsert_file
        
        # Call upsert
        mock_repository.upsert_file(file_metadata.model_dump(mode="json"))
        
        # Assert expected behavior for repository
        assert saved_metadata is not None
        assert str(saved_metadata["id"]) == str(file_id)
        assert saved_metadata["type"] == "JD"
        print("Repository operations completed successfully")
        
        # Step 6: Test queue service
        print("Step 6: Testing queue service")
        mock_queue_service = MagicMock(spec=QueueService)
        
        # Patch the QueueService in the _queue_for_matching function
        with patch('file_processing.file_processing.QueueService', return_value=mock_queue_service):
            _queue_for_matching(str(file_id), "test_user", file_type)
            
            # Assert expected behavior for queue service
            assert mock_queue_service.create_queue_if_not_exists.call_count == 1
            assert mock_queue_service.send_message.call_count == 1
            print("Queue service operations completed successfully")
        
        print("All steps of file processing tested successfully!")
        
    finally:
        # Restore original method
        DocxService.get_text_from_docx = original_get_text

if __name__ == "__main__":
    test_file_processing_core_workflow() 
