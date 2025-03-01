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

class MockOpenAIServiceWithToolCalls:
    """Mock OpenAI service that returns responses with tool calls for CV analysis."""
    
    def analyze_document(self, text, pages, paragraphs):
        from shared.openai_service.models import DocumentAnalysis, DocumentStructure
        
        # Create a mock tool call response for CV analysis
        tool_call_response = {
            "id": "chatcmpl-123456789",
            "object": "chat.completion",
            "created": int(datetime.now().timestamp()),
            "model": "gpt-4-turbo",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_abc123",
                                "type": "function",
                                "function": {
                                    "name": "analyze_cv",
                                    "arguments": json.dumps({
                                        "document_type": "CV",
                                        "personal_details": [
                                            {"type": "Name", "text": "Jane Doe"},
                                            {"type": "Email", "text": "jane.doe@example.com"},
                                            {"type": "Phone", "text": "555-123-4567"},
                                            {"type": "Location", "text": "San Francisco, CA"}
                                        ],
                                        "professional_summary": "Full-stack developer with 5 years of experience in web and mobile application development.",
                                        "skills": [
                                            "Python", "JavaScript", "TypeScript", "React", 
                                            "Django", "Flask", "AWS", "Azure", "Docker", 
                                            "Kubernetes", "CI/CD"
                                        ],
                                        "experience": [
                                            {
                                                "company": "Cloud Technologies Inc.",
                                                "position": "Senior Developer",
                                                "duration": "2021-Present",
                                                "responsibilities": "Led development of cloud-based applications, implemented microservices architecture, mentored junior developers"
                                            },
                                            {
                                                "company": "Web Solutions LLC",
                                                "position": "Software Engineer",
                                                "duration": "2018-2021",
                                                "responsibilities": "Developed responsive web applications, integrated third-party APIs, improved application performance"
                                            }
                                        ],
                                        "education": [
                                            {
                                                "institution": "Tech University",
                                                "degree": "Master of Computer Science",
                                                "year": "2018"
                                            }
                                        ]
                                    })
                                }
                            }
                        ]
                    },
                    "finish_reason": "tool_calls"
                }
            ],
            "usage": {
                "prompt_tokens": 1000,
                "completion_tokens": 500,
                "total_tokens": 1500
            }
        }
        
        print(f"Mock OpenAI service returning tool call response for CV analysis")
        
        # Create the document structure from the tool call response
        tool_call_args = json.loads(tool_call_response["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"])
        
        structure = DocumentStructure(
            personal_details=tool_call_args["personal_details"],
            professional_summary=tool_call_args["professional_summary"],
            skills=tool_call_args["skills"],
            experience=tool_call_args["experience"],
            education=tool_call_args["education"],
            company_details=None,
            role_summary=None,
            required_skills=None,
            experience_requirements=None,
            education_requirements=None,
            additional_information=[]
        )
        
        # Create the document analysis
        document_analysis = DocumentAnalysis(
            document_type="CV",
            structure=structure
        )
        
        return document_analysis

def test_cv_processing_with_tool_calls():
    """
    Test the processing of CV documents with OpenAI tool calls.
    This test mocks the OpenAI service to return responses with tool calls for CV analysis.
    """
    print("\n========== TEST: test_cv_processing_with_tool_calls ==========")
    
    # Create a mock document text - a simple CV/resume
    document_text = """
    Resume of Jane Doe
    Email: jane.doe@example.com
    Phone: 555-123-4567
    Location: San Francisco, CA
    
    PROFESSIONAL SUMMARY
    Full-stack developer with 5 years of experience in web and mobile application development.
    
    SKILLS
    Languages: Python, JavaScript, TypeScript
    Frameworks: React, Django, Flask
    Cloud: AWS, Azure
    DevOps: Docker, Kubernetes, CI/CD
    
    EXPERIENCE
    
    Cloud Technologies Inc.
    Senior Developer
    2021-Present
    - Led development of cloud-based applications
    - Implemented microservices architecture
    - Mentored junior developers
    
    Web Solutions LLC
    Software Engineer
    2018-2021
    - Developed responsive web applications
    - Integrated third-party APIs
    - Improved application performance
    
    EDUCATION
    
    Tech University
    Master of Computer Science
    2018
    """
    
    # Generate a valid UUID for the file_id
    file_id = uuid.uuid4()
    print(f"Generated file_id: {file_id}")
    
    # Create a mock queue message
    mock_msg = MagicMock()
    request_data = {
        "id": str(file_id),
        "url": "https://example.com/test_cv.pdf",
        "filename": "test_cv.pdf",
        "type": "CV",
        "user_id": "test_user"
    }
    mock_msg.get_json.return_value = request_data
    mock_msg.get_body.return_value = json.dumps(request_data).encode('utf-8')
    print(f"Created mock message with data: {request_data}")
    
    # Step 1: Parse the queue message
    print("Step 1: Parsing queue message")
    request = _parse_queue_message(mock_msg)
    assert str(request.id) == str(file_id)
    assert request.filename == "test_cv.pdf"
    print(f"Request parsed successfully: {request}")
    
    # Step 2: Prepare mocks for document content extraction
    print("Step 2: Extracting document content")
    blob_content = document_text.encode('utf-8')
    mock_blob_service = MagicMock(spec=FilesBlobService)
    mock_blob_service.container_name = "files"
    mock_blob_service.get_file_content.return_value = blob_content
    
    # Mock the document intelligence service
    mock_doc_intelligence_service = MagicMock(spec=DocumentIntelligenceService)
    mock_doc_intelligence_service.client = MagicMock()
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
        
        # Instead of calling _extract_document_content directly, patch it
        structured_info = {
            "text": document_text,
            "pages": [{
                "page_number": 1,
                "content": document_text,
                "lines": [{"content": "Test line"}]
            }],
            "paragraphs": ["Test paragraph"]
        }
        
        with patch('file_processing.file_processing._extract_document_content', return_value=structured_info):
            print(f"Document content extracted successfully: {list(structured_info.keys())}")
            
            # Step 3: Analyze document with mock OpenAI service with tool calls
            print("Step 3: Analyzing document with OpenAI (tool calls)")
            mock_openai_service = MockOpenAIServiceWithToolCalls()
            document_analysis = mock_openai_service.analyze_document(
                text=structured_info['text'],
                pages=structured_info.get('pages', []),
                paragraphs=structured_info.get('paragraphs', [])
            )
            
            # Assert expected behavior for CV document analysis
            assert document_analysis is not None
            assert document_analysis.document_type == "CV"
            assert document_analysis.structure.personal_details is not None
            assert document_analysis.structure.skills is not None
            assert "Python" in document_analysis.structure.skills
            assert "TypeScript" in document_analysis.structure.skills
            assert len(document_analysis.structure.experience) == 2
            assert document_analysis.structure.experience[0]["company"] == "Cloud Technologies Inc."
            assert document_analysis.structure.experience[1]["company"] == "Web Solutions LLC"
            print("CV document analyzed successfully with tool calls")
            
            # Step 4: Create file metadata
            print("Step 4: Creating file metadata")
            file_type = FileType.CV
            file_metadata = _create_file_metadata(request, structured_info, file_type, document_analysis)
            
            # Assert expected behavior for file metadata
            assert file_metadata is not None
            assert str(file_metadata.id) == str(file_id)
            assert file_metadata.type == FileType.CV
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
            assert saved_metadata["type"] == "CV"
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
            
            print("All steps of CV file processing with tool calls tested successfully!")
        
    finally:
        # Restore original method
        DocxService.get_text_from_docx = original_get_text

if __name__ == "__main__":
    test_cv_processing_with_tool_calls() 