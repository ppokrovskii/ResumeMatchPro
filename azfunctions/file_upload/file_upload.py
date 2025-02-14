import os
import azure.functions as func
import logging
import json
import base64

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

        # Get file from request
        input_files = req.files.get('content', [])
        if not input_files:
            logging.error("No files found in request")
            return func.HttpResponse(
                json.dumps("Invalid request: No files provided"),
                status_code=400,
                mimetype="application/json"
            )
        
        # Ensure input_files is a list
        if not isinstance(input_files, list):
            input_files = [input_files]
        
        input_file = input_files[0]

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
        
        for input_file in files_list:
            try:
                # Log input file details for debugging
                logging.info(f"Input file type: {type(input_file)}")
                if hasattr(input_file, '__dict__'):
                    logging.info(f"Input file attributes: {input_file.__dict__}")

                # Handle FileStorage objects from form data
                if hasattr(input_file, 'filename') and input_file.filename:
                    filename = input_file.filename
                    content = input_file.read()
                else:
                    # For raw bytes or other formats
                    filename = None
                    content = input_file
                    # Try to get filename from various sources
                    if hasattr(input_file, 'name'):
                        filename = input_file.name
                    elif 'filename' in req.form:
                        filename = req.form['filename']
                    
                if not filename:
                    logging.error("No filename found in request")
                    logging.info(f"Form data: {req.form}")
                    logging.info(f"Files data: {req.files}")
                    return func.HttpResponse(
                        json.dumps("Invalid request: Filename not provided"),
                        status_code=400,
                        mimetype="application/json"
                    )
                    
                request_dict = {
                    "user_id": user_id,
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
                    filename=file_upload_request.filename,
                    type=file_upload_request.type,
                    user_id=file_upload_request.user_id,
                    url=blob_url
                )
                file_metadata = files_repository.upsert_file(file_metadata.model_dump(mode="json"))
                # Increment the user's file count after successful upload
                user_repository.increment_files_count(user_id)
            except ValidationError as e:
                return func.HttpResponse(
                    json.dumps("Internal Server Error!"),
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