import logging
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import json


from shared.openai_service.models import (
    MatchingResultModel,
    DocumentAnalysis
)

load_dotenv()

class OpenAIService:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
            api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.model = 'gpt-35-turbo-16k'

    def analyze_document(self, text: str, pages: list, paragraphs: list) -> DocumentAnalysis:
        """
        Analyze a document to determine its type (CV or JD) and extract structured information.
        """
        prompt = f"""Analyze the provided document to determine if it's a CV (resume) or a Job Description (JD), and extract structured information.
        The document content is provided as text, pages, and paragraphs.

        Instructions:
        1. First, determine if this is a CV or JD based on the content and structure.
        2. Extract structured information according to the document type:

        For CVs:
        - Personal details (name, email, phone, location, etc.)
        - Professional summary/objective
        - Skills (technical, soft skills, languages, etc.)
        - Professional experience (with dates, titles, and responsibilities)
        - Education (with dates, degrees, and institutions)
        - Any additional sections (certifications, awards, etc.)

        For JDs:
        - Company/position details
        - Role summary/overview
        - Required skills and qualifications
        - Experience requirements
        - Education requirements
        - Additional information (benefits, company culture, etc.)

        Document Text: {text}
        Pages: {pages}
        Paragraphs: {paragraphs}
        """

        messages = [{"role": "user", "content": prompt}]
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "store_document_analysis",
                    "description": "Store the analysis of the document structure",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "document_type": {
                                "type": "string",
                                "enum": ["CV", "JD"],
                                "description": "The type of document"
                            },
                            "structure": {
                                "type": "object",
                                "properties": {
                                    "personal_details": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "type": {"type": "string"},
                                                "text": {"type": "string"}
                                            },
                                            "required": ["type", "text"]
                                        }
                                    },
                                    "professional_summary": {"type": "string"},
                                    "skills": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "experience": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "title": {"type": "string"},
                                                "start_date": {"type": "string"},
                                                "end_date": {"type": "string"},
                                                "lines": {
                                                    "type": "array",
                                                    "items": {"type": "string"}
                                                }
                                            },
                                            "required": ["title", "start_date", "lines"]
                                        }
                                    },
                                    "education": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "title": {"type": "string"},
                                                "start_date": {"type": "string"},
                                                "end_date": {"type": "string"},
                                                "degree": {"type": "string"},
                                                "details": {"type": "string"},
                                                "city": {"type": "string"}
                                            },
                                            "required": ["title", "start_date"]
                                        }
                                    },
                                    "additional_information": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    }
                                },
                                "required": ["personal_details", "professional_summary", "skills", "experience", "education"]
                            }
                        },
                        "required": ["document_type", "structure"]
                    }
                }
            }
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=2048
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            if not tool_calls:
                raise ValueError("No tool calls received in the response")

            tool_call = tool_calls[0]
            function_args = json.loads(tool_call.function.arguments)
            
            return DocumentAnalysis(**function_args)

        except Exception as e:
            logging.error(f"Error analyzing document: {str(e)}")
            raise

    def match_cv_and_jd(self, cv_text: str, jd_text: str):
        messages = [{"role": "user", "content": self._create_matching_prompt(cv_text, jd_text)}]
        tools = [self._get_matching_tool()]
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=1024
            )
            
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            
            if not tool_calls:
                raise ValueError("No tool calls received in the response")
                
            if len(tool_calls) > 1:
                raise ValueError(f"Expected only one tool call but got {len(tool_calls)}")
                
            tool_call = tool_calls[0]
            function_args = tool_call.function.arguments
            
            if not function_args:
                raise ValueError(f"Expected function_args in tool call but got {function_args}")
                
            return MatchingResultModel.from_json(function_args)
            
        except Exception as e:
            logging.error(f"Error matching CV and JD: {str(e)}")
            raise

    def _create_matching_prompt(self, cv_text: str, jd_text: str) -> str:
        return f"""Analyze the provided CV and JD to determine the suitability of the candidate for the specified job position. 
        call store_matching_result function to store the result.
        
        Instructions:
        Extract and List Key Requirements from the JD: Identify and categorize the essential qualifications, skills, and experience levels mentioned in the job description. This should include, but not be limited to, technical skills, soft skills, education requirements, and years of relevant experience.
        
        Analyze the Candidate's CV: Review the candidate's CV to extract pertinent information regarding their educational background, skill set, professional experience, and any other qualifications relevant to the job description.
        
        Match Analysis:
        Skills Match: Compare the skills listed in the candidate's CV against those required by the job description. Note any direct matches, related or transferable skills, and any skills gaps.
        Experience Match: Evaluate the candidate's professional experience against the experience requirements specified in the JD. Consider the relevance, duration, and level of the positions previously held by the candidate.
        Education Match: Assess the candidate's educational qualifications in relation to the educational requirements mentioned in the JD.
        Calculate Overall Suitability Percentage: Based on the analysis, estimate the percentage match between the candidate's profile and the job requirements. Consider weighting the importance of skills, experience, and education based on the priorities indicated in the JD.
        
        CV: {cv_text} 
        JD: {jd_text}"""

    def _get_matching_tool(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "store_matching_result",
                "description": "Store or process the CV and JD matching result",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "jd_requirements": {
                            "type": "object",
                            "properties": {
                                "skills": {"type": "array", "items": {"type": "string"}},
                                "experience": {"type": "array", "items": {"type": "string"}},
                                "education": {"type": "array", "items": {"type": "string"}}
                            }
                        },
                        "candidate_capabilities": {
                            "type": "object",
                            "properties": {
                                "skills": {"type": "array", "items": {"type": "string"}},
                                "experience": {"type": "array", "items": {"type": "string"}},
                                "education": {"type": "array", "items": {"type": "string"}}
                            }
                        },
                        "cv_match": {
                            "type": "object",
                            "properties": {
                                "skills_match": {"type": "array", "items": {"type": "string"}},
                                "experience_match": {"type": "array", "items": {"type": "string"}},
                                "education_match": {"type": "array", "items": {"type": "string"}},
                                "gaps": {"type": "array", "items": {"type": "string"}}
                            }
                        },
                        "overall_match_percentage": {"type": "number"}
                    },
                    "required": ["jd_requirements", "candidate_capabilities", "cv_match", "overall_match_percentage"]
                }
            }
        }
