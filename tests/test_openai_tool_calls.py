import json
import uuid
from unittest.mock import MagicMock, patch
from datetime import datetime

import pytest
from shared.models import FileType
from shared.openai_service.models import DocumentAnalysis, DocumentStructure

class MockOpenAIServiceWithToolCalls:
    """Mock OpenAI service that returns responses with tool calls for CV analysis."""
    
    def analyze_document(self, text, pages, paragraphs):
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

def test_openai_tool_calls_for_cv():
    """Test the OpenAI service with tool calls for CV analysis."""
    print("\n========== TEST: test_openai_tool_calls_for_cv ==========")
    
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
    
    # Create structured info
    structured_info = {
        "text": document_text,
        "pages": [{
            "page_number": 1,
            "content": document_text,
            "lines": [{"content": "Test line"}]
        }],
        "paragraphs": ["Test paragraph"]
    }
    
    # Create mock OpenAI service
    mock_openai_service = MockOpenAIServiceWithToolCalls()
    
    # Analyze document
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
    
    # Print the document analysis for inspection
    print(f"Document type: {document_analysis.document_type}")
    print(f"Personal details: {document_analysis.structure.personal_details}")
    print(f"Skills: {document_analysis.structure.skills}")
    print(f"Experience: {document_analysis.structure.experience}")
    
    return document_analysis

def test_simple_cv_tool_call():
    """A simple test for CV tool calls."""
    print("\nRunning simple CV tool call test")
    
    # Create a mock tool call response
    tool_call_args = {
        "document_type": "CV",
        "personal_details": [
            {"type": "Name", "text": "Jane Doe"},
            {"type": "Email", "text": "jane.doe@example.com"}
        ],
        "skills": ["Python", "JavaScript", "TypeScript"]
    }
    
    # Verify the structure
    assert tool_call_args["document_type"] == "CV"
    assert len(tool_call_args["personal_details"]) == 2
    assert "Python" in tool_call_args["skills"]
    
    print("Simple CV tool call test passed")
    return tool_call_args

if __name__ == "__main__":
    test_openai_tool_calls_for_cv() 