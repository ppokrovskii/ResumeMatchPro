import json
import logging
import os
from pydoc import doc

from dotenv import load_dotenv
from openai import AzureOpenAI
from shared.openai_service.models import (
    CVStructure,
    CVStructureLoose,
    DocumentAnalysis,
    JDStructure,
    JDStructureLoose,
    MatchingResultModel,
)

load_dotenv()


class OpenAIService:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.model = "gpt-4o"

    def analyze_document(
        self, text: str, pages: list, paragraphs: list
    ) -> DocumentAnalysis:
        """
        Analyze a document to determine its type (CV or Job Description) and extract structured information.
        """
        prompt = f"""Analyze the provided document to determine if it's a CV (resume) or a Job Description (JD), and extract structured information.
        The document content is provided as text, pages, and paragraphs extracted from pdf with OCR.
        If the source document was a docx, pages and paragraphs might be empty.

        Instructions:
        1. First, determine if this is a CV or JD based on the content and structure.
        2. Based on type call store_cv or store_jd tool providing valid json structure.
        3. For CVs, ensure to include education information in the following format:
           - title: Name of the educational institution (required)
           - start_date: Start date of education (required)
           - end_date: End date of education (optional)
           - degree: Degree obtained (optional)
           - details: Additional details about the education (optional)
           - city: City where the education took place (optional)
           If no education information is found, provide an empty list.

        Document Text: {text}
        Pages: {pages}
        Paragraphs: {paragraphs}
        """

        messages = [{"role": "user", "content": prompt}]
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "store_cv",
                    "description": "Store the analysis of a CV/Resume document structure",
                    "parameters": CVStructure.model_json_schema(),  # Use strict schema for LLM
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "store_jd",
                    "description": "Store the analysis of a Job Description document structure",
                    "parameters": JDStructure.model_json_schema(),  # Use strict schema for LLM
                },
            },
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=2048,
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            if not tool_calls:
                logging.error(f"No tool calls in response. Full response: {response}")
                raise ValueError("No tool calls received in the response")

            tool_call = tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            # Log the function call details
            logging.info(f"Function called: {function_name}")
            logging.info(f"Function arguments: {json.dumps(function_args, indent=2)}")

            # Use loose validation when processing the response
            if function_name == "store_cv":
                cv_structure = CVStructureLoose(**function_args)
                return DocumentAnalysis(document_type="CV", structure=cv_structure)
            else:
                jd_structure = JDStructureLoose(**function_args)  # Use loose validation
                return DocumentAnalysis(document_type="JD", structure=jd_structure)

        except Exception as e:
            logging.error(f"Error analyzing document: {str(e)}")
            raise ValueError(f"Error analyzing document: {str(e)}")

    def match_cv_and_jd(self, cv_text: str, jd_text: str):
        # Parse CV and JD text if they are JSON strings
        try:
            cv_data = json.loads(cv_text.replace("'", '"'))
            jd_data = json.loads(jd_text.replace("'", '"'))

            # Format CV data for better readability
            cv_formatted = f"""
CV Details:
Name: {next((detail["text"] for detail in cv_data.get("personal_details", []) if detail["type"] == "Name"), "Not specified")}
Professional Summary: {cv_data.get("professional_summary", "Not specified")}
Skills: {", ".join(cv_data.get("skills", []))}
Experience: {"; ".join(f"{exp.get('title', '')}: {', '.join(exp.get('lines', []))}" for exp in cv_data.get("experience", []))}
Education: {"; ".join(f"{edu.get('title', '')} ({edu.get('start_date', '')}-{edu.get('end_date', 'Present')})" for edu in cv_data.get("education", []))}
Additional Information: {", ".join(cv_data.get("additional_information", []))}
"""

            # Format JD data for better readability
            jd_formatted = f"""
Job Description:
Title: {jd_data.get("job_title", "Not specified")}
Role Summary: {jd_data.get("role_summary", "Not specified")}
Required Skills: {", ".join(jd_data.get("required_skills", []))}
Experience Requirements: {", ".join(jd_data.get("experience_requirements", []))}
Education Requirements: {", ".join(jd_data.get("education_requirements", []) if jd_data.get("education_requirements") else ["Not specified"])}
Additional Information: {", ".join(jd_data.get("additional_information", []) if jd_data.get("additional_information") else ["Not specified"])}
"""
        except json.JSONDecodeError:
            # If parsing fails, use the raw text
            cv_formatted = cv_text
            jd_formatted = jd_text

        prompt = f"""Analyze the provided CV and JD to determine the suitability of the candidate for the specified job position. 
        you MUST call store_matching_result function to store the result.
        
        Instructions:
        1. Extract and List Key Requirements from the JD: Identify and categorize the essential qualifications, skills, and experience levels mentioned in the job description. This should include, but not be limited to, technical skills, soft skills, education requirements, and years of relevant experience.
        
        2. Analyze the Candidate's CV: Review the candidate's CV to extract pertinent information regarding their educational background, skill set, professional experience, and any other qualifications relevant to the job description.
        
        3. Match Analysis:
           - Skills Match: Compare the skills listed in the candidate's CV against those required by the job description. Note any direct matches, related or transferable skills, and any skills gaps.
           - Experience Match: Evaluate the candidate's professional experience against the experience requirements specified in the JD. Consider the relevance, duration, and level of the positions previously held by the candidate.
           - Education Match: Assess the candidate's educational qualifications in relation to the educational requirements mentioned in the JD.
        
        4. Calculate overall_match_percentage: Based on the analysis, estimate the percentage match between the candidate's profile and the job requirements. Consider weighting the importance of skills, experience, and education based on the priorities indicated in the JD.
           - overall_match_percentage MUST be a float between 0 and 100
           - Example: if candidate has 3 skills out of 5 required skills, overall_match_percentage should be 60.0
        
        5. You MUST provide ALL of these fields in your response:
           - jd_requirements (with skills, experience, and education lists)
           - candidate_capabilities (with skills, experience, and education lists)
           - cv_match (with skills_match, experience_match, education_match, and gaps lists)
           - overall_match_percentage (as a float between 0 and 100)
        
        CV: {cv_formatted} 
        
        JD: {jd_formatted}"""

        messages = [{"role": "user", "content": prompt}]
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "store_matching_result",
                    "description": "Store result of matching cv and jd",
                    "parameters": MatchingResultModel.model_json_schema(),
                },
            }
        ]

        try:
            # First attempt
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=1024,
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            if not tool_calls:
                raise ValueError(
                    f"No tool calls received in the response: {response_message}"
                )

            if len(tool_calls) > 1:
                raise ValueError(
                    f"Expected only one tool call but got {len(tool_calls)} in response: {response_message}"
                )

            tool_call = tool_calls[0]
            function_args = tool_call.function.arguments

            if not function_args:
                raise ValueError(
                    f"Expected function_args in tool call but got {function_args} in response: {response_message}"
                )

            # Add the first response to messages, handling null content
            messages.append(
                {
                    "role": "assistant",
                    "content": response_message.content
                    or "Processing the matching request...",
                }
            )

            try:
                result = MatchingResultModel.from_json(function_args)
                return result
            except Exception as e:
                # Add the validation error to messages
                messages.append(
                    {
                        "role": "user",
                        "content": f"Error validating the response: {str(e)}. Please ensure the response matches the required schema and all fields are properly formatted. You MUST include: jd_requirements, candidate_capabilities, cv_match, and overall_match_percentage.",
                    }
                )

                # Second attempt with full message history
                response = self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    max_tokens=1024,
                )

                response_message = response.choices[0].message
                tool_calls = response_message.tool_calls

                if not tool_calls:
                    raise ValueError(
                        f"No tool calls received in the retry response: {response_message}"
                    )

                tool_call = tool_calls[0]
                function_args = tool_call.function.arguments

                if not function_args:
                    raise ValueError(
                        f"Expected function_args in retry tool call but got {function_args} in response: {response_message}"
                    )

                result = MatchingResultModel.from_json(function_args)
                return result

        except Exception as e:
            logging.error(f"Error matching CV and JD: {str(e)}")
            raise
