import logging
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import json

from pydantic import ValidationError

from shared.openai_service.models import MatchingResultModel

load_dotenv()

class OpenAIService:
    def match_cv_and_jd(self, cv_text: str, jd_text: str):
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
            api_version="2024-02-01",
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            )
            
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        model = 'gpt-35-turbo-16k'
        prompt = f"""Analyze the provided CV and JD to determine the suitability of the candidate for the specified job position. 
        call store_matching_result function to store the result.
        Instructions:
        Extract and List Key Requirements from the JD: Identify and categorize the essential qualifications, skills, and experience levels mentioned in the job description. This should include, but not be limited to, technical skills, soft skills, education requirements, and years of relevant experience.
        Analyze the Candidate's CV: Review the candidate's CV to extract pertinent information regarding their educational background, skill set, professional experience, and any other qualifications relevant to the job description.
        Match Analysis:
        Skills Match: Compare the skills listed in the candidate's CV against those required by the job description. Note any direct matches, related or transferable skills, and any skills gaps.
        Experience Match: Evaluate the candidate's professional experience against the experience requirements specified in the JD. Consider the relevance, duration, and level of the positions previously held by the candidate.
        Education Match: Assess the candidate's educational qualifications in relation to the educational requirements mentioned in the JD.
        Calculate Overall Suitability Percentage: Based on the analysis, estimate the percentage match between the candidate’s profile and the job requirements. Consider weighting the importance of skills, experience, and education based on the priorities indicated in the JD.
        CV: {cv_text} 
        JD: {jd_text}"""
        messages = [{"role": "user", "content": prompt}]
        tools = [
            {
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
        ]
        
        response = client.chat.completions.create(
            model=deployment_name, 
            messages=messages,
            tools=tools,
            tool_choice="auto",  # auto is default, but we'll be explicit here
            max_tokens=1024,
            # deployment_name=deployment_name
            )
        # result = response.choices[0].message.content
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        logging.info(f"tool_calls: {tool_calls}")
        if tool_calls:
            if len(tool_calls) > 1:
                raise ValueError(f"Expected only one tool call but got {len(tool_calls)}")
            tool_call = tool_calls[0]
            function_args = tool_call.function.arguments
            if not function_args:
                raise ValueError(f"Expected function_args in tool call but got {function_args}")
            return MatchingResultModel.from_json(function_args)
        return None


# def str_to_matching_result_model(json_str: str):
#     try:
#         # clean text and convert to lowercase
#         json_str = json_str.replace("\n", " ").replace("\t", " ").replace("\r", " ").replace("'", '"').replace("\'", "'")
#         result_dict = json.loads(json_str)
#         return MatchingResultModel.from_json(result_dict)
#     except json.JSONDecodeError as e:
#             raise ValueError(f"Can't parse str result: {json_str}")
#     except ValidationError as e:
#         raise ValueError(f"Can't convert dict to MatchingResultModel: {e}")
