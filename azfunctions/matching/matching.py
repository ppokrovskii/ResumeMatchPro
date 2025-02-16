import logging
import azure.functions as func
from pydantic import ValidationError

from shared.matching_results_repository import MatchingResultsRepository
from shared.files_repository import FilesRepository
from shared.user_repository import UserRepository
from shared.db_service import get_cosmos_db_client
from shared.openai_service.openai_service import OpenAIService
from matching.schemas import FileModel, FileType, MatchingRequestMessage, MatchingResultModel

# create blueprint with Queue trigger
matching_bp = func.Blueprint()

@matching_bp.queue_trigger(arg_name="msg", queue_name="matching-queue",
                                  connection="AzureWebJobsStorage")
def match_resume(msg: func.QueueMessage):
    logging.info(f"matching function called with a message: {msg.get_body().decode('utf-8')}")
    # validate message
    try:
        matching_request = MatchingRequestMessage(**msg.get_json())
    except ValidationError as e:
        raise ValueError(f"Invalid message: {e}")
    # fetch text from db
    cosmos_db_client = get_cosmos_db_client()
    files_repository = FilesRepository(cosmos_db_client)
    user_repository = UserRepository(cosmos_db_client)
    
    file_metadata_db = files_repository.get_file_by_id(matching_request.user_id, matching_request.id)
    if not file_metadata_db:
        raise ValueError(f"File with id {matching_request.id} not found in db")
    if not file_metadata_db.text:
        raise ValueError(f"File with id {matching_request.id} has no text. Was not processed yet?")
    # delete exising matching results for file with same user_id and file name
    matching_results_repository = MatchingResultsRepository(cosmos_db_client)
    matching_results_repository.delete_matching_results_by_file(file_metadata_db.user_id, file_metadata_db.filename)
    # find files from the same user but another file type from db
    search_files_type = FileType.CV if file_metadata_db.type == FileType.JD else FileType.JD
    files_from_db = files_repository.get_files_from_db(file_metadata_db.user_id, search_files_type)
    # call openai api to compare skills file by file and store matching result in db
    
    for file_from_db in files_from_db:
        # call openai api
        openai_service = OpenAIService()
        matching_result = openai_service.match_cv_and_jd(cv_text=file_metadata_db.text, jd_text=file_from_db.text)
        if search_files_type == FileType.CV:
            cv = file_from_db
            jd = file_metadata_db
        else:
            cv = file_metadata_db
            jd = file_from_db
        matching_result_db = MatchingResultModel(
            user_id=file_metadata_db.user_id,
            cv=FileModel(**cv.model_dump(mode="json")),
            jd=FileModel(**jd.model_dump(mode="json")),
            jd_requirements=matching_result.jd_requirements.model_dump(mode="json"),
            candidate_capabilities=matching_result.candidate_capabilities.model_dump(mode="json"),
            cv_match=matching_result.cv_match.model_dump(mode="json"),
            overall_match_percentage=matching_result.overall_match_percentage
        )
        # store result in db
        matching_results_repository.upsert_result(matching_result_db.model_dump(mode="json"))
        # increment matching count for user
        user_repository.increment_matching_count(file_metadata_db.user_id)