
import os
import azure.functions as func
import logging

from shared.db_service import get_cosmos_db_client
from shared.files_repository import FilesRepository
from user_files.models import UserFilesRequest, UserFilesResponse


user_files_bp = func.Blueprint("user_files", __name__)

@user_files_bp.route(route="files", methods=["GET"])
def get_files(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('get_files function processed a request.')
    request = UserFilesRequest(**req.params)
    cosmos_db_client = get_cosmos_db_client()
    files_repository = FilesRepository(cosmos_db_client)
    files_metadata_db = files_repository.get_files_from_db(request.user_id, request.type)
    response = UserFilesResponse(files=[file_metadata.model_dump(mode="json") for file_metadata in files_metadata_db])
    return func.HttpResponse(response.model_dump_json(), mimetype="application/json")