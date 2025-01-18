import os
import azure.functions as func
import logging

from pydantic import ValidationError

from shared.db_service import get_cosmos_db_client
from shared.files_repository import FilesRepository
from shared.queue_service import QueueService
from file_upload.schemas import FileUploadOutputQueueMessage, FileUploadRequest, FileUploadResponse, FileUploadResponses
from shared.blob_service import FilesBlobService
from shared.models import FileMetadataDb

# create blueprint
file_upload_bp = func.Blueprint()

@file_upload_bp.route(route="files/upload", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def files_upload(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    files_blob_service = FilesBlobService()
    cosmos_db_client = get_cosmos_db_client()
    files_repository = FilesRepository(cosmos_db_client)
    return _files_upload(req, files_blob_service, files_repository)

def _files_upload(req: func.HttpRequest, files_blob_service: FilesBlobService, files_repository: FilesRepository) -> func.HttpResponse:
    # validate request
    if not req.files:
        return func.HttpResponse(
            "No files in request",
            status_code=400
        )
    file_upload_responses = FileUploadResponses()
    # iterate over all files from the request
    for input_file in req.files.getlist('content'):
        try:
            request_dict = {
                "user_id": req.form.get("user_id"),
                "type": req.form.get("type"),
                "filename": input_file.filename,
                "content": input_file.stream.read()
            }
            file_upload_request = FileUploadRequest(**request_dict)
        except ValidationError as e:
            return func.HttpResponse(
                "Invalid request: " + str(e),
                status_code=400
            )
    
        # upload file to blob storage
        blob_url = files_blob_service.upload_blob(
            container_name="resume-match-pro-files", 
            filename=file_upload_request.filename, 
            content=file_upload_request.content
        )
        # Save file metadata to database
        try:
            file_metadata = FileMetadataDb(
                filename=file_upload_request.filename,
                type=file_upload_request.type,
                user_id=file_upload_request.user_id,
                url=blob_url
            )
            file_metadata = files_repository.upsert_file(file_metadata.model_dump(mode="json"))
        except ValidationError as e:
            return func.HttpResponse(
                "Internal Server Error!",
                status_code=500
            )        
        # send to queue 'processing-queue'
        queue_service = QueueService(connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
        queue_service.create_queue_if_not_exists("processing-queue")
        file_upload_queue_message = FileUploadOutputQueueMessage(**file_metadata.model_dump())
        msg = file_upload_queue_message.model_dump_json()
        queue_service.send_message("processing-queue", msg)
        #
        file_upload_response = FileUploadResponse(**file_metadata.model_dump())
        file_upload_responses.files.append(file_upload_response)
    return func.HttpResponse(
        file_upload_responses.model_dump_json(),
        status_code=200
    )