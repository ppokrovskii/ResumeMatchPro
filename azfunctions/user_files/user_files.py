import os
import json
import azure.functions as func
import logging
from pydantic import ValidationError
import base64

from shared.db_service import get_cosmos_db_client
from shared.files_repository import FilesRepository
from shared.blob_service import FilesBlobService
from user_files.models import UserFilesRequest, UserFilesResponse, File, ResumeStructure

# create blueprint
user_files_bp = func.Blueprint()

@user_files_bp.route(route="files", methods=["GET"])
def get_files(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('get_files function processed a request.')
    
    # Debug logging for headers
    auth_header = req.headers.get('Authorization', '')
    client_principal = req.headers.get('x-ms-client-principal', '')
    logging.info(f"Debug headers - Authorization: {auth_header}")
    logging.info(f"Debug headers - x-ms-client-principal: {client_principal}")
    
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
        # Get user_id from B2C claims
        client_principal = req.headers.get('X-MS-CLIENT-PRINCIPAL')
        if not client_principal:
            return func.HttpResponse(
                body=json.dumps({"error": "Unauthorized - Missing user claims"}),
                mimetype="application/json",
                status_code=401
            )

        claims_json = base64.b64decode(client_principal).decode('utf-8')
        claims = json.loads(claims_json)
        user_id = next((claim['val'] for claim in claims['claims'] 
                      if claim['typ'] == 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier'), None)

        if not user_id:
            return func.HttpResponse(
                body=json.dumps({"error": "Unauthorized - Missing user ID in claims"}),
                mimetype="application/json",
                status_code=401
            )

        # Use user_id from claims
        request = UserFilesRequest(user_id=user_id, type=req.params.get('type'))
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
    # Get file_id from route parameters
    file_id = req.route_params.get('file_id')
    if not file_id:
        return func.HttpResponse(
            body=json.dumps({"error": "file_id is required"}),
            mimetype="application/json",
            status_code=400
        )
    
    try:
        # Get user_id from B2C claims
        client_principal = req.headers.get('X-MS-CLIENT-PRINCIPAL')
        if not client_principal:
            return func.HttpResponse(
                body=json.dumps({"error": "Unauthorized - Missing user claims"}),
                mimetype="application/json",
                status_code=401
            )

        try:
            claims_json = base64.b64decode(client_principal).decode('utf-8')
            claims = json.loads(claims_json)
            user_id = next((claim['val'] for claim in claims['claims'] 
                          if claim['typ'] == 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier'), None)
            
            if not user_id:
                return func.HttpResponse(
                    body=json.dumps({"error": "Unauthorized - Missing user ID in claims"}),
                    mimetype="application/json",
                    status_code=401
                )
        except Exception as e:
            logging.error(f"Error decoding claims: {str(e)}")
            return func.HttpResponse(
                body=json.dumps({"error": "Unauthorized - Invalid claims format"}),
                mimetype="application/json",
                status_code=401
            )
        
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


@user_files_bp.route(route="files/{file_id}", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_file(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Get file function processed a request.')
    try:
        cosmos_db_client = get_cosmos_db_client()
        files_repository = FilesRepository(cosmos_db_client)
        response = _get_file(req, files_repository)
        return response
    except Exception as e:
        logging.error(f"Error in get_file wrapper: {str(e)}")
        return func.HttpResponse(
            body=json.dumps({"error": "Internal Server Error"}),
            mimetype="application/json",
            status_code=500
        )


def _get_file(req: func.HttpRequest, files_repository: FilesRepository) -> func.HttpResponse:
    # Get file_id from route parameters
    file_id = req.route_params.get('file_id')
    if not file_id:
        return func.HttpResponse(
            body=json.dumps({"error": "file_id is required"}),
            mimetype="application/json",
            status_code=400
        )
    
    try:
        # Get user_id from B2C claims
        client_principal = req.headers.get('X-MS-CLIENT-PRINCIPAL')
        if not client_principal:
            return func.HttpResponse(
                body=json.dumps({"error": "Unauthorized - Missing user claims"}),
                mimetype="application/json",
                status_code=401
            )

        try:
            claims_json = base64.b64decode(client_principal).decode('utf-8')
            claims = json.loads(claims_json)
            user_id = next((claim['val'] for claim in claims['claims'] 
                          if claim['typ'] == 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier'), None)
            
            if not user_id:
                return func.HttpResponse(
                    body=json.dumps({"error": "Unauthorized - Missing user ID in claims"}),
                    mimetype="application/json",
                    status_code=401
                )
        except Exception as e:
            logging.error(f"Error decoding claims: {str(e)}")
            return func.HttpResponse(
                body=json.dumps({"error": "Unauthorized - Invalid claims format"}),
                mimetype="application/json",
                status_code=401
            )
        
        try:
            # Get file using partition key
            file_metadata = files_repository.get_file_by_id(user_id, file_id)
            if not file_metadata:
                return func.HttpResponse(
                    body=json.dumps({"error": "File not found"}),
                    mimetype="application/json",
                    status_code=404
                )
            
            logging.info(f"Retrieved file metadata: {file_metadata.model_dump_json()}")
            
            # Convert to our response model
            file_response = File(
                id=file_metadata.id,
                filename=file_metadata.filename,
                type=file_metadata.type,
                user_id=file_metadata.user_id,
                url=file_metadata.url
            )

            # If document analysis exists, map it to our structure
            if hasattr(file_metadata, 'document_analysis') and file_metadata.document_analysis:
                logging.info(f"Document analysis found: {file_metadata.document_analysis}")
                if hasattr(file_metadata.document_analysis, 'structure'):
                    logging.info(f"Structure found in document analysis: {file_metadata.document_analysis.structure}")
                    file_response.structure = ResumeStructure(**file_metadata.document_analysis.structure.model_dump())
                else:
                    logging.warning("No structure found in document analysis")
            else:
                logging.info("No document analysis found in file metadata")
            
            # Create response with all structured information
            response_data = file_response.model_dump(mode="json", exclude_none=True)
            logging.info(f"Final response data: {response_data}")
            
            return func.HttpResponse(
                body=json.dumps(response_data),
                mimetype="application/json",
                status_code=200
            )
        except PermissionError as e:
            return func.HttpResponse(
                body=json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=403
            )
    except Exception as e:
        logging.error(f"Error getting file: {str(e)}")
        return func.HttpResponse(
            body=json.dumps({"error": "Internal Server Error"}),
            mimetype="application/json",
            status_code=500
        )


@user_files_bp.route(route="files/{file_id}/download", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def download_file(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Download file function processed a request.')
    try:
        cosmos_db_client = get_cosmos_db_client()
        files_repository = FilesRepository(cosmos_db_client)
        files_blob_service = FilesBlobService()
        response = _download_file(req, files_repository, files_blob_service)
        return response
    except Exception as e:
        logging.error(f"Error in download_file wrapper: {str(e)}")
        return func.HttpResponse(
            body=json.dumps({"error": "Internal Server Error"}),
            mimetype="application/json",
            status_code=500
        )


def _download_file(req: func.HttpRequest, files_repository: FilesRepository, files_blob_service: FilesBlobService) -> func.HttpResponse:
    # Get file_id from route parameters
    file_id = req.route_params.get('file_id')
    if not file_id:
        return func.HttpResponse(
            body=json.dumps({"error": "file_id is required"}),
            mimetype="application/json",
            status_code=400
        )
    
    try:
        # Get user_id from B2C claims
        client_principal = req.headers.get('X-MS-CLIENT-PRINCIPAL')
        if not client_principal:
            return func.HttpResponse(
                body=json.dumps({"error": "Unauthorized - Missing user claims"}),
                mimetype="application/json",
                status_code=401
            )

        try:
            claims_json = base64.b64decode(client_principal).decode('utf-8')
            claims = json.loads(claims_json)
            user_id = next((claim['val'] for claim in claims['claims'] 
                          if claim['typ'] == 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier'), None)
            
            if not user_id:
                return func.HttpResponse(
                    body=json.dumps({"error": "Unauthorized - Missing user ID in claims"}),
                    mimetype="application/json",
                    status_code=401
                )
        except Exception as e:
            logging.error(f"Error decoding claims: {str(e)}")
            return func.HttpResponse(
                body=json.dumps({"error": "Unauthorized - Invalid claims format"}),
                mimetype="application/json",
                status_code=401
            )
        
        try:
            # Get file metadata using partition key
            file_metadata = files_repository.get_file_by_id(user_id, file_id)
            if not file_metadata:
                return func.HttpResponse(
                    body=json.dumps({"error": "File not found"}),
                    mimetype="application/json",
                    status_code=404
                )
            
            # Get file from blob storage
            blob_data = files_blob_service.get_file_content(
                container_name="resume-match-pro-files",
                filename=file_metadata.filename
            )
            
            if not blob_data:
                return func.HttpResponse(
                    body=json.dumps({"error": "File content not found"}),
                    mimetype="application/json",
                    status_code=404
                )
            
            # Return file with proper headers
            headers = {
                'Content-Disposition': f'attachment; filename="{file_metadata.filename}"',
                'Content-Type': 'application/octet-stream'
            }
            return func.HttpResponse(
                body=blob_data,
                headers=headers,
                status_code=200
            )
            
        except PermissionError as e:
            return func.HttpResponse(
                body=json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=403
            )
    except Exception as e:
        logging.error(f"Error downloading file: {str(e)}")
        return func.HttpResponse(
            body=json.dumps({"error": "Internal Server Error"}),
            mimetype="application/json",
            status_code=500
        )