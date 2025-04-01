import logging
from typing import Dict, List

import azure.functions as func
from matching.schemas import (
    FileModel,
    FileType,
    MatchingRequestMessage,
    MatchingResultModel,
)
from pydantic import ValidationError
from shared.db_service import get_cosmos_db_client
from shared.files_repository import FilesRepository
from shared.matching_results_repository import MatchingResultsRepository
from shared.openai_service.openai_service import OpenAIService
from shared.user_repository import UserRepository

# create blueprint with Queue trigger
matching_bp = func.Blueprint()


class MatchProcessor:
    """
    Handles the matching workflow.
    This class is stateless - matching state is maintained only within the match method.
    Services are injected via constructor for better testability.
    """

    def __init__(
        self,
        files_repository: FilesRepository,
        matching_results_repository: MatchingResultsRepository,
        user_repository: UserRepository,
        openai_service: OpenAIService,
    ):
        # Initialize services from parameters
        self.files_repository = files_repository
        self.matching_results_repository = matching_results_repository
        self.user_repository = user_repository
        self.openai_service = openai_service

    @staticmethod
    def create_with_default_services():
        """
        Factory method to create a MatchProcessor with default services.
        This simplifies instantiation when you don't need custom service implementations.
        """
        cosmos_db_client = get_cosmos_db_client()
        files_repository = FilesRepository(cosmos_db_client)
        matching_results_repository = MatchingResultsRepository(cosmos_db_client)
        user_repository = UserRepository(cosmos_db_client)
        openai_service = OpenAIService()

        return MatchProcessor(
            files_repository=files_repository,
            matching_results_repository=matching_results_repository,
            user_repository=user_repository,
            openai_service=openai_service,
        )

    def match(self, matching_request: MatchingRequestMessage) -> List[Dict]:
        """
        Process matching request and find matching files.
        Returns the matching results.
        """
        logging.info(f"Starting match process for file {matching_request.file_id}")

        # Get file metadata from db
        file_metadata_db = self.files_repository.get_file_by_id(
            matching_request.user_id, matching_request.file_id
        )

        if not file_metadata_db:
            logging.error(f"File {matching_request.file_id} not found")
            raise ValueError(f"File {matching_request.file_id} not found")

        logging.info(f"Found file metadata: {file_metadata_db}")

        # Find files from the same user but another file type from db
        search_files_type = (
            FileType.CV if file_metadata_db.type == FileType.JD else FileType.JD
        )
        logging.info(f"Searching for files of type: {search_files_type}")

        # Get all files of the opposite type for this user
        files_from_db = self.files_repository.get_files_from_db(
            user_id=file_metadata_db.user_id, file_type=search_files_type
        )
        logging.info(f"Found {len(files_from_db)} files of type {search_files_type}")

        if not files_from_db:
            logging.warning(
                f"No files of type {search_files_type} found for user {file_metadata_db.user_id}"
            )
            return []

        matching_results = []

        # Process each matching pair
        for file_from_db in files_from_db:
            logging.info(f"Processing file {file_from_db.id} for matching")
            # Determine which file is CV and which is JD
            if search_files_type == FileType.CV:
                cv = file_from_db
                jd = file_metadata_db
            else:
                cv = file_metadata_db
                jd = file_from_db

            logging.info(f"CV file ID: {cv.id}")
            logging.info(f"JD file ID: {jd.id}")

            logging.info("Calling OpenAI service for matching")
            # Call openai api to get matching result
            matching_result = self.openai_service.match_cv_and_jd(
                cv_text=str(cv.structure), jd_text=str(jd.structure)
            )

            # Create matching result model
            matching_result_db = MatchingResultModel(
                user_id=file_metadata_db.user_id,
                cv=FileModel(**cv.model_dump(mode="json")),
                jd=FileModel(**jd.model_dump(mode="json")),
                jd_requirements=matching_result.jd_requirements.model_dump(mode="json"),
                candidate_capabilities=matching_result.candidate_capabilities.model_dump(
                    mode="json"
                ),
                cv_match=matching_result.cv_match.model_dump(mode="json"),
                overall_match_percentage=matching_result.overall_match_percentage,
            )

            # Store result in db
            self.matching_results_repository.upsert_result(
                matching_result_db.model_dump(mode="json")
            )

            # Increment matching count for user
            self.user_repository.increment_matching_count(file_metadata_db.user_id)

            # Add to results list
            matching_results.append(matching_result_db.model_dump(mode="json"))
            logging.info(
                f"Added matching result to list. Total results: {len(matching_results)}"
            )

        logging.info(f"Match process completed. Found {len(matching_results)} results")
        return matching_results


@matching_bp.queue_trigger(
    arg_name="msg",
    queue_name="matching-queue",
    connection="AzureWebJobsStorage",
    maxDequeueCount=1,
)
def match_resume_function(msg: func.QueueMessage) -> List[Dict]:
    """
    Azure Function trigger for matching files.
    Takes a message from the queue and delegates matching to MatchProcessor.
    Returns the matching results for synchronous processing.
    """
    try:
        logging.info(
            f"matching function called with a message: {msg.get_body().decode('utf-8')}"
        )
        # Validate message
        matching_request = MatchingRequestMessage(**msg.get_json())
        logging.info(f"Matching request: {matching_request}")

        # Create processor using the factory method
        processor = MatchProcessor.create_with_default_services()
        logging.info("Created processor")

        # Process the request and get results
        results = processor.match(matching_request)
        logging.info(f"Match results: {results}")

        logging.info("Matching completed successfully")

        # Ensure we always return a list
        if results is None:
            logging.warning("Results is None, returning empty list")
            final_results = []
        else:
            final_results = results

        logging.info(f"Final results: {final_results}")
        return final_results

    except ValidationError as e:
        error_msg = f"Invalid message: {e}"
        logging.error(error_msg)
        logging.exception(e)  # Log full stack trace
        # Return None to indicate error
        return None
    except Exception as e:
        error_msg = f"Error in match_resume_function: {str(e)}"
        logging.error(error_msg)
        logging.exception(e)  # Log full stack trace
        # Return None to indicate error
        return None
