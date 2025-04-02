import json
import logging
import os
from pydoc import doc

from dotenv import load_dotenv
from openai import AzureOpenAI
from shared.openai_service.models import (
    CVStructure,
    DocumentAnalysis,
    JDStructure,
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
                    "parameters": CVStructure.model_json_schema(),
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "store_jd",
                    "description": "Store the analysis of a Job Description document structure",
                    "parameters": JDStructure.model_json_schema(),
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

            # Determine document type based on which tool was called
            if function_name == "store_cv":
                return DocumentAnalysis(
                    document_type="CV", structure=CVStructure(**function_args)
                )
            else:
                return DocumentAnalysis(
                    document_type="JD", structure=JDStructure(**function_args)
                )
        except Exception as e:
            logging.error(
                f"Error analyzing document. Full response: {response if 'response' in locals() else 'No response'}"
            )
            raise ValueError(f"Error analyzing document: {str(e)}")

    def match_cv_and_jd(self, cv_text: str, jd_text: str):
        prompt = f"""Analyze the provided CV and JD to determine the suitability of the candidate for the specified job position. 
        you MUST call store_matching_result function to store the result.
        
        Instructions:
        Extract and List Key Requirements from the JD: Identify and categorize the essential qualifications, skills, and experience levels mentioned in the job description. This should include, but not be limited to, technical skills, soft skills, education requirements, and years of relevant experience.
        
        Analyze the Candidate's CV: Review the candidate's CV to extract pertinent information regarding their educational background, skill set, professional experience, and any other qualifications relevant to the job description.
        
        Match Analysis:
        Skills Match: Compare the skills listed in the candidate's CV against those required by the job description. Note any direct matches, related or transferable skills, and any skills gaps.
        Experience Match: Evaluate the candidate's professional experience against the experience requirements specified in the JD. Consider the relevance, duration, and level of the positions previously held by the candidate.
        Education Match: Assess the candidate's educational qualifications in relation to the educational requirements mentioned in the JD.
        Calculate overall_match_percentage: Based on the analysis, estimate the percentage match between the candidate's profile and the job requirements. Consider weighting the importance of skills, experience, and education based on the priorities indicated in the JD.
        overall_match_percentage is mandatory field and should be a float between 0 and 100. For example if candidate has 3 skills out of 5 required skills, overall_match_percentage should be 60.0
        
        CV: {cv_text} 
        JD: {jd_text}"""
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
            try:
                result = MatchingResultModel.from_json(function_args)
            except KeyError as ke:
                logging.warning(
                    f"Error converting json: {function_args} to MatchingResultModel: {str(ke)}"
                )
                # add error message to messages and call self.client.chat.completions.create again
                messages.append(
                    {
                        "role": "user",
                        "content": f"Error converting function_args json to MatchingResultModel: {str(ke)}",
                    }
                )
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
                    raise ValueError("No tool calls received in the response")
                tool_call = tool_calls[0]
                function_args = tool_call.function.arguments
                result = MatchingResultModel.from_json(function_args)
            except Exception as e:
                raise ValueError(
                    f"Error matching CV and JD: {str(e)} in response: {response_message}"
                )
            return result

        except Exception as e:
            logging.error(f"Error matching CV and JD: {str(e)}")
            raise
