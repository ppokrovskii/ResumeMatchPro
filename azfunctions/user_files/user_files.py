import os
import json
import azure.functions as func
import logging
from pydantic import ValidationError

from shared.db_service import get_cosmos_db_client
from shared.files_repository import FilesRepository
from shared.blob_service import FilesBlobService
from user_files.models import UserFilesRequest, UserFilesResponse

# create blueprint
user_files_bp = func.Blueprint()

@user_files_bp.route(route="files", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_files(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('get_files function processed a request.')
    try:
        cosmos_db_client = get_cosmos_db_client()
        files_repository = FilesRepository(cosmos_db_client)
        response = _get_files(req, files_repository)
        return response
    except Exception as e:
        logging.error(f"Error in get_files wrapper: {str(e)}")
        return func.HttpResponse(
            body=json.dumps({"error": "Internal Server Error"}),
            mimetype="application/json",
            status_code=500
        )


def _get_files(req: func.HttpRequest, files_repository: FilesRepository) -> func.HttpResponse:
    try:
        if not req.params.get('user_id'):
            return func.HttpResponse(
                body=json.dumps({"error": "user_id is required"}),
                mimetype="application/json",
                status_code=400
            )
        request = UserFilesRequest(**req.params)
        files_metadata_db = files_repository.get_files_from_db(request.user_id, request.type)
        response = UserFilesResponse(files=[file_metadata.model_dump(mode="json") for file_metadata in files_metadata_db])
        return func.HttpResponse(
            body=response.model_dump_json(),
            mimetype="application/json",
            status_code=200
        )
    except ValidationError as e:
        logging.error(f"Validation error: {str(e)}")
        return func.HttpResponse(
            body=json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=400
        )
    except Exception as e:
        logging.error(f"Error getting files: {str(e)}")
        return func.HttpResponse(
            body=json.dumps({"error": "Internal Server Error"}),
            mimetype="application/json",
            status_code=500
        )


@user_files_bp.route(route="files/{file_id}", methods=["DELETE"], auth_level=func.AuthLevel.ANONYMOUS)
def delete_file(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Delete file function processed a request.')
    try:
        files_blob_service = FilesBlobService()
        cosmos_db_client = get_cosmos_db_client()
        files_repository = FilesRepository(cosmos_db_client)
        response = _delete_file(req, files_blob_service, files_repository)
        return response
    except Exception as e:
        logging.error(f"Error in delete_file wrapper: {str(e)}")
        return func.HttpResponse(
            body=json.dumps({"error": "Internal Server Error"}),
            mimetype="application/json",
            status_code=500
        )


def _delete_file(req: func.HttpRequest, files_blob_service: FilesBlobService, files_repository: FilesRepository) -> func.HttpResponse:
    # Get file_id from route parameters and user_id from token claims
    file_id = req.route_params.get('file_id')
    if not file_id:
        return func.HttpResponse(
            body=json.dumps({"error": "file_id is required"}),
            mimetype="application/json",
            status_code=400
        )
    
    try:
        # Get user_id from token claims
        token_claims = req.get_claims()
        if not token_claims or 'sub' not in token_claims:
            return func.HttpResponse(
                body=json.dumps({"error": "Unauthorized - Missing user ID in token"}),
                mimetype="application/json",
                status_code=401
            )
        user_id = token_claims['sub']
        
        # Get file metadata from database
        file_metadata = files_repository.get_file_by_id(user_id, file_id)
        if not file_metadata:
            return func.HttpResponse(
                body=json.dumps({"error": "File not found"}),
                mimetype="application/json",
                status_code=404
            )
        
        # Verify file ownership
        if file_metadata.user_id != user_id:
            return func.HttpResponse(
                body=json.dumps({"error": "Unauthorized - You don't have permission to delete this file"}),
                mimetype="application/json",
                status_code=403
            )
        
        # Delete file from blob storage
        files_blob_service.delete_blob(
            container_name="resume-match-pro-files",
            filename=file_metadata.filename
        )
        
        # Delete file metadata from database
        files_repository.delete_file(user_id=user_id, file_id=file_id)
        
        return func.HttpResponse(
            body="",
            status_code=204
        )
        
    except Exception as e:
        logging.error(f"Error deleting file: {str(e)}")
        return func.HttpResponse(
            body=json.dumps({"error": "Internal Server Error"}),
            mimetype="application/json",
            status_code=500
        )