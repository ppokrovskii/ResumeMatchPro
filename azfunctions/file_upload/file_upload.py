import os
import azure.functions as func
import logging
import json
import base64
import re
from uuid import uuid4

from pydantic import ValidationError

from shared.db_service import get_cosmos_db_client
from shared.files_repository import FilesRepository
from shared.queue_service import QueueService
from file_upload.schemas import FileUploadOutputQueueMessage, FileUploadRequest, FileUploadResponse, FileUploadResponses
from shared.blob_service import FilesBlobService
from shared.models import FileMetadataDb
from shared.user_repository import UserRepository

# create blueprint
file_upload_bp = func.Blueprint()

@file_upload_bp.route(route="files/upload", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def files_upload(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    files_blob_service = FilesBlobService()
    cosmos_db_client = get_cosmos_db_client()
    files_repository = FilesRepository(cosmos_db_client)
    user_repository = UserRepository(cosmos_db_client)
    return _files_upload(req, files_blob_service, files_repository, user_repository)

def _files_upload(req: func.HttpRequest, files_blob_service: FilesBlobService, files_repository: FilesRepository, user_repository: UserRepository) -> func.HttpResponse:
    try:
        # Log all headers for debugging
        logging.info("Request headers:")
        for header, value in req.headers.items():
            if header.lower() not in ['authorization', 'x-ms-client-principal']:
                logging.info(f"{header}: {value}")
            else:
                logging.info(f"{header}: [REDACTED]")

        # Log request details
        logging.info("Files list type: %s", type(req.files.get('content', [])))
        logging.info("Files list content: %s", req.files.get('content', []))
        logging.info("Form data: %s", req.form)
        logging.info("Files data: %s", req.files)

        # Retrieve file(s) from the request robustly
        if hasattr(req.files, 'getlist'):
            input_files = req.files.getlist('content')
        elif isinstance(req.files, list):
            input_files = req.files
        elif req.files:
            input_files = [req.files]
        else:
            input_files = []

        if not input_files:
            logging.error("No files found in request")
            return func.HttpResponse(
                json.dumps("Invalid request: No files provided"),
                status_code=400,
                mimetype="application/json"
            )
        
        # Get user_id from B2C claims
        client_principal = req.headers.get('X-MS-CLIENT-PRINCIPAL')
        if not client_principal:
            logging.error("Missing X-MS-CLIENT-PRINCIPAL header")
            return func.HttpResponse(
                json.dumps("Unauthorized - Missing user claims"),
                status_code=401,
                mimetype="application/json"
            )

        try:
            logging.info("Decoding client principal")
            claims_json = base64.b64decode(client_principal).decode('utf-8')
            claims = json.loads(claims_json)
            logging.info(f"Claims structure: {json.dumps(claims, indent=2)}")
            
            # Ensure user_id is always taken from the token
            user_id = next((claim['val'] for claim in claims['claims'] 
                        if claim['typ'] == 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier'), None)
            
            if not user_id:
                logging.error("No user ID found in claims")
                return func.HttpResponse(
                    json.dumps("Unauthorized - Missing user ID in claims"),
                    status_code=401,
                    mimetype="application/json"
                )
            
            logging.info(f"Found user_id: {user_id}")
            
        except Exception as e:
            logging.error(f"Error decoding claims: {str(e)}")
            logging.error(f"Raw client principal: {client_principal}")
            return func.HttpResponse(
                json.dumps("Unauthorized - Invalid claims format"),
                status_code=401,
                mimetype="application/json"
            )

        # Check if user can upload more files
        try:
            if not user_repository.can_upload_file(user_id):
                return func.HttpResponse(
                    json.dumps("File upload limit reached"),
                    status_code=403,
                    mimetype="application/json"
                )
        except ValueError as e:
            return func.HttpResponse(
                json.dumps(f"User not found: {str(e)}"),
                status_code=404,
                mimetype="application/json"
            )

        file_upload_responses = FileUploadResponses()
        # iterate over all files from the request
        files_list = req.files.get('content', [])
        if isinstance(files_list, dict):
            files_list = [files_list]
            
        # Log the files list for debugging
        logging.info(f"Files list type: {type(files_list)}")
        logging.info(f"Files list content: {files_list}")
        
        for input_file in input_files:
            try:
                # Log input file details for debugging
                logging.info(f"Input file type: {type(input_file)}")
                if hasattr(input_file, '__dict__'):
                    logging.info(f"Input file attributes: {input_file.__dict__}")

                # Handle each input_file
                if hasattr(input_file, 'filename') and input_file.filename:
                    filename = input_file.filename
                    content = input_file.read()
                elif isinstance(input_file, bytes):
                    # If the file is already bytes, try to get the filename from the original FileStorage
                    fs_obj = None
                    if hasattr(req.files, 'get'):
                        fs_obj = req.files.get('content')
                    if fs_obj and hasattr(fs_obj, 'filename') and fs_obj.filename:
                        filename = fs_obj.filename
                    else:
                        filename = None
                    content = input_file
                else:
                    # For other formats
                    filename = None
                    content = input_file
                    if hasattr(input_file, 'name'):
                        filename = input_file.name
                    elif 'filename' in req.form:
                        filename = req.form['filename']
                    elif hasattr(input_file, 'headers'):
                        content_disp = input_file.headers.get('Content-Disposition', '')
                        m = re.search('filename="([^"]+)"', content_disp)
                        if m:
                            filename = m.group(1)
                if not filename:
                    logging.error("No filename found in request")
                    logging.info(f"Form data: {req.form}")
                    logging.info(f"Files data: {req.files}")
                    return func.HttpResponse(
                        json.dumps("Invalid request: Filename not provided"),
                        status_code=400,
                        mimetype="application/json"
                    )
                    
                # Remove any user_id extraction from request payload or parameters
                request_dict = {
                    "user_id": user_id,  # Ensure user_id is from token
                    "type": req.form.get("type"),
                    "filename": filename,
                    "content": content
                }
                file_upload_request = FileUploadRequest(**request_dict)
            except ValidationError as e:
                return func.HttpResponse(
                    json.dumps("Invalid request: " + str(e)),
                    status_code=400,
                    mimetype="application/json"
                )
        
            # upload file to blob storage
            blob_url = files_blob_service.upload_blob(
                container_name=files_blob_service.container_name,
                filename=file_upload_request.filename, 
                content=file_upload_request.content
            )
            # Save file metadata to database
            try:
                file_metadata = FileMetadataDb(
                    id=uuid4(),
                    filename=file_upload_request.filename,
                    type=file_upload_request.type,
                    user_id=user_id,
                    url=blob_url
                )
                file_metadata = files_repository.upsert_file(file_metadata.model_dump(mode="json"))
                # Increment the user's file count after successful upload
                user_repository.increment_files_count(user_id)
            except ValidationError as e:
                logging.error(f"Validation error creating file metadata: {str(e)}")
                return func.HttpResponse(
                    json.dumps({"error": "Internal Server Error", "details": str(e)}),
                    status_code=500,
                    mimetype="application/json"
                )        
            # send to queue 'processing-queue'
            queue_service = QueueService(connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
            queue_service.create_queue_if_not_exists("processing-queue")
            file_upload_queue_message = FileUploadOutputQueueMessage(**file_metadata.model_dump())
            msg = file_upload_queue_message.model_dump_json()
            queue_service.send_message("processing-queue", msg)
            
            # Add response
            file_upload_responses.files.append(FileUploadResponse(
                filename=file_metadata.filename,
                url=file_metadata.url,
                type=file_metadata.type,
                user_id=file_metadata.user_id
            ))
        
        return func.HttpResponse(
            file_upload_responses.model_dump_json(),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Unexpected error in file upload: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": "Internal Server Error", "details": str(e)}),
            status_code=500,
            mimetype="application/json"
        )