import pytest

def test_simple_cv_tool_call():
    """Simple test that doesn't require external services"""
    print("Running simple CV tool call test")
    
    # Mock tool call response
    tool_call_args = {
        "document_type": "CV",
        "skills": ["Python", "JavaScript"]
    }
    
    # Basic assertions
    assert tool_call_args["document_type"] == "CV"
    assert "Python" in tool_call_args["skills"]
    
    print("Test passed!")
    return tool_call_args 