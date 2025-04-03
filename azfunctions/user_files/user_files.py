# ruff: noqa: F401
import base64
import json
import logging
import uuid

import azure.functions as func
from pydantic import ValidationError as PydanticValidationError
from shared.blob_service import FilesBlobService
from shared.db_service import get_cosmos_db_client
from shared.files_repository import FilesRepository
from shared.models import FileType
from user_files.exceptions import (
    BlobStorageError,
    FileNotFoundError,
    PermissionDeniedError,
    UnauthorizedError,
    ValidationError,
    create_error_response,
    get_logger_with_context,
    get_request_id,
)
from user_files.models import (
    File,
    ResumeStructure,
    UserFilesRequest,
    UserFilesResponse,
)


def _extract_user_id(req: func.HttpRequest) -> str:
    """Extract and validate user ID from request"""
    client_principal = req.headers.get("X-MS-CLIENT-PRINCIPAL")
    if not client_principal:
        raise UnauthorizedError("Missing user claims")

    try:
        claims_json = base64.b64decode(client_principal).decode("utf-8")
        claims = json.loads(claims_json)
        user_id = next(
            (
                claim["val"]
                for claim in claims["claims"]
                if claim["typ"]
                == "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier"
            ),
            None,
        )

        if not user_id:
            raise UnauthorizedError("Missing user ID in claims")

        return user_id

    except (ValueError, json.JSONDecodeError) as e:
        raise UnauthorizedError(f"Invalid claims format: {str(e)}")


def _get_files(
    req: func.HttpRequest, files_repository: FilesRepository
) -> func.HttpResponse:
    """Implementation of getting files logic"""
    user_id = _extract_user_id(req)
    request = UserFilesRequest(user_id=user_id, type=req.params.get("type"))

    files_metadata_db = files_repository.get_files_from_db(
        request.user_id, request.type
    )

    files_response = []
    for file_metadata in files_metadata_db:
        try:
            file_json = file_metadata.model_dump(mode="json")

            if (
                hasattr(file_metadata, "document_analysis")
                and file_metadata.document_analysis
                and hasattr(file_metadata.document_analysis, "structure")
                and file_metadata.document_analysis.structure
            ):
                structure = file_metadata.document_analysis.structure
                file_type = getattr(file_metadata, "type", None)

                if file_type == FileType.CV:
                    if (
                        hasattr(structure, "personal_details")
                        and structure.personal_details
                    ):
                        for detail in structure.personal_details:
                            if (
                                hasattr(detail, "type")
                                and detail.type
                                and detail.type.lower() == "name"
                            ):
                                file_json["name"] = detail.text
                                break

                if hasattr(structure, "job_title") and structure.job_title:
                    file_json["job_title"] = structure.job_title

            files_response.append(file_json)
        except PydanticValidationError as e:
            raise ValidationError(f"Invalid file metadata format: {str(e)}")
        except Exception as e:
            raise BlobStorageError(f"Failed to process file metadata: {str(e)}")

    response = UserFilesResponse(files=files_response)
    return func.HttpResponse(
        body=response.model_dump_json(),
        mimetype="application/json",
        status_code=200,
    )


def _delete_file(
    req: func.HttpRequest,
    files_blob_service: FilesBlobService,
    files_repository: FilesRepository,
) -> func.HttpResponse:
    """Implementation of file deletion logic"""
    file_id = req.route_params.get("file_id")
    if not file_id:
        raise ValidationError("file_id is required")

    user_id = _extract_user_id(req)

    file_metadata = files_repository.get_file_by_id(user_id, file_id)
    if not file_metadata:
        raise FileNotFoundError(f"File with ID {file_id} not found")

    if file_metadata.user_id != user_id:
        raise PermissionDeniedError("You don't have permission to delete this file")

    try:
        files_blob_service.delete_blob(
            container_name="resume-match-pro-files", filename=file_metadata.filename
        )
        files_repository.delete_file(user_id=user_id, file_id=file_id)
        return func.HttpResponse(body="", status_code=204)
    except Exception as e:
        raise BlobStorageError(f"Failed to delete file: {str(e)}")


def _get_file(
    req: func.HttpRequest, files_repository: FilesRepository
) -> func.HttpResponse:
    """Implementation of getting single file logic"""
    user_id = _extract_user_id(req)
    file_id = req.route_params.get("file_id")
    if not file_id:
        raise ValidationError("file_id is required")

    file_db = files_repository.get_file_by_id(user_id, file_id)
    if not file_db:
        raise FileNotFoundError(f"File with ID {file_id} not found")

    file_response = File(
        id=str(file_db.id),
        filename=file_db.filename,
        type=file_db.type,
        user_id=file_db.user_id,
        url=file_db.url,
    )

    if file_db.structure:
        structure_dict = file_db.structure
        if isinstance(structure_dict, dict):
            file_response.structure = ResumeStructure(**structure_dict)
            structure = file_response.structure
        else:
            file_response.structure = structure_dict
            structure = structure_dict

        if structure:
            if (
                file_db.type == FileType.CV
                and hasattr(structure, "personal_details")
                and structure.personal_details
            ):
                for detail in structure.personal_details:
                    if hasattr(detail, "type") and detail.type.lower() == "name":
                        file_response.name = detail.text
                        break

            if hasattr(structure, "job_title") and structure.job_title:
                file_response.job_title = structure.job_title

    return func.HttpResponse(
        body=file_response.model_dump_json(),
        mimetype="application/json",
        status_code=200,
    )


def _download_file(
    req: func.HttpRequest,
    files_blob_service: FilesBlobService,
    files_repository: FilesRepository,
) -> func.HttpResponse:
    """Implementation of file download logic"""
    user_id = _extract_user_id(req)
    file_id = req.route_params.get("file_id")
    if not file_id:
        raise ValidationError("File ID is required")

    file = files_repository.get_file_by_id(user_id, file_id)
    if not file:
        raise FileNotFoundError(f"File with ID {file_id} not found")

    try:
        file_content = files_blob_service.get_file_content(
            container_name=files_blob_service.container_name,
            filename=file.filename,
        )

        return func.HttpResponse(
            body=file_content,
            mimetype=file.content_type or "application/octet-stream",
            status_code=200,
            headers={
                "Content-Disposition": f'attachment; filename="{file.filename}"',
                "Content-Type": file.content_type or "application/octet-stream",
            },
        )
    except Exception as e:
        raise BlobStorageError(f"Failed to retrieve file content: {str(e)}")


# create blueprint
user_files_bp = func.Blueprint()


@user_files_bp.route(route="files", methods=["GET"])
def get_files(req: func.HttpRequest) -> func.HttpResponse:
    """Top-level API endpoint for getting files"""
    request_id = get_request_id(req)
    logger = get_logger_with_context(request_id)

    try:
        cosmos_db_client = get_cosmos_db_client()
        files_repository = FilesRepository(cosmos_db_client)
        response = _get_files(req, files_repository)
        return response
    except (UnauthorizedError, ValidationError) as e:
        logger.exception("Authorization or validation error", exc_info=True)
        error_body, status = create_error_response(e)
        return func.HttpResponse(
            body=json.dumps(error_body),
            mimetype="application/json",
            status_code=status,
        )
    except Exception as e:
        logger.exception("Unexpected error getting files", exc_info=True)
        error_body, status = create_error_response(e)
        return func.HttpResponse(
            body=json.dumps(error_body),
            mimetype="application/json",
            status_code=status,
        )


@user_files_bp.route(route="files/{file_id}", methods=["DELETE"])
def delete_file(req: func.HttpRequest) -> func.HttpResponse:
    """Top-level API endpoint for deleting files"""
    request_id = get_request_id(req)
    logger = get_logger_with_context(request_id)

    try:
        files_blob_service = FilesBlobService()
        cosmos_db_client = get_cosmos_db_client()
        files_repository = FilesRepository(cosmos_db_client)
        response = _delete_file(req, files_blob_service, files_repository)
        return response
    except (
        UnauthorizedError,
        ValidationError,
        FileNotFoundError,
        PermissionDeniedError,
    ) as e:
        logger.exception(
            "Authorization, validation, or permission error", exc_info=True
        )
        error_body, status = create_error_response(e)
        return func.HttpResponse(
            body=json.dumps(error_body),
            mimetype="application/json",
            status_code=status,
        )
    except Exception as e:
        logger.exception("Unexpected error deleting file", exc_info=True)
        error_body, status = create_error_response(e)
        return func.HttpResponse(
            body=json.dumps(error_body),
            mimetype="application/json",
            status_code=status,
        )


@user_files_bp.route(route="files/{file_id}", methods=["GET"])
def get_file(req: func.HttpRequest) -> func.HttpResponse:
    """Top-level API endpoint for getting a single file"""
    request_id = get_request_id(req)
    logger = get_logger_with_context(request_id)

    try:
        cosmos_db_client = get_cosmos_db_client()
        files_repository = FilesRepository(cosmos_db_client)
        response = _get_file(req, files_repository)
        return response
    except (
        UnauthorizedError,
        ValidationError,
        FileNotFoundError,
        PermissionDeniedError,
    ) as e:
        logger.exception(
            "Authorization, validation, or permission error", exc_info=True
        )
        error_body, status = create_error_response(e)
        return func.HttpResponse(
            body=json.dumps(error_body),
            mimetype="application/json",
            status_code=status,
        )
    except Exception as e:
        logger.exception("Unexpected error getting file", exc_info=True)
        error_body, status = create_error_response(e)
        return func.HttpResponse(
            body=json.dumps(error_body),
            mimetype="application/json",
            status_code=status,
        )


@user_files_bp.route(route="files/{file_id}/download", methods=["GET"])
def download_file(req: func.HttpRequest) -> func.HttpResponse:
    """Top-level API endpoint for downloading files"""
    request_id = get_request_id(req)
    logger = get_logger_with_context(request_id)

    try:
        files_blob_service = FilesBlobService()
        cosmos_db_client = get_cosmos_db_client()
        files_repository = FilesRepository(cosmos_db_client)
        response = _download_file(req, files_blob_service, files_repository)
        return response
    except (
        UnauthorizedError,
        ValidationError,
        FileNotFoundError,
        PermissionDeniedError,
        BlobStorageError,
    ) as e:
        logger.exception("Authorization, validation, or storage error", exc_info=True)
        error_body, status = create_error_response(e)
        return func.HttpResponse(
            body=json.dumps(error_body),
            mimetype="application/json",
            status_code=status,
        )
    except Exception as e:
        logger.exception("Unexpected error downloading file", exc_info=True)
        error_body, status = create_error_response(e)
        return func.HttpResponse(
            body=json.dumps(error_body),
            mimetype="application/json",
            status_code=status,
        )
