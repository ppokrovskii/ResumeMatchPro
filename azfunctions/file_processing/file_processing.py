import logging
import os
import azure.functions as func
from pydantic import ValidationError

from shared.db_service import get_cosmos_db_client
from shared.files_repository import FilesRepository
from file_processing.schemas import FileProcessingOutputQueueMessage, FileProcessingRequest
from shared.blob_service import FilesBlobService
from shared.document_intelligence_service import DocumentIntelligenceService
from shared.docx_service import DocxService
from shared.models import FileMetadataDb, FileType
from shared.queue_service import QueueService
from shared.openai_service.openai_service import OpenAIService

# create blueprint with Queue trigger
file_processing_bp = func.Blueprint()

@file_processing_bp.queue_trigger(arg_name="msg", queue_name="processing-queue", connection="AzureWebJobsStorage")
def process_file(msg: func.QueueMessage):
    """
    Process a file uploaded by a user.
    1. Extract text and structure from the file.
    2. Analyze the document to determine its type (CV/Resume or Job Description).
    3. Store the structured data in the database.
    4. Queue the file for matching.
    """
    logging.info("Processing new file from queue")
    
    try:
        # Parse queue message
        file_processing_request = _parse_queue_message(msg)
        
        # Get necessary services
        blob_service = FilesBlobService()
        document_intelligence_service = _get_document_intelligence_service()
        openai_service = OpenAIService()
        
        # Get file content
        content = blob_service.get_file_content(blob_service.container_name, file_processing_request.filename)
        if not content:
            raise ValueError(f"File content is empty or file not found: {file_processing_request.filename}")
        
        # Process document based on file type
        structured_info = _extract_document_content(
            content, 
            file_processing_request.filename, 
            document_intelligence_service
        )
        
        # Analyze document structure with OpenAI
        document_analysis = openai_service.analyze_document(
            text=structured_info['text'],
            pages=structured_info.get('pages', []),
            paragraphs=structured_info.get('paragraphs', [])
        )
        
        # Determine file type based on document analysis
        file_type = FileType.CV if document_analysis.document_type == "CV" else FileType.JD
        
        # Save metadata to database
        file_metadata_db = _create_file_metadata(file_processing_request, structured_info, file_type, document_analysis)
        repository = _get_repository()
        repository.upsert_file(file_metadata_db.model_dump(mode="json"))
        
        # Queue file for matching
        _queue_for_matching(file_processing_request.id, file_processing_request.user_id, file_type)
        
        logging.info(f"Successfully processed file {file_processing_request.filename}")
        
    except Exception as e:
        logging.error(f"Error processing file: {str(e)}", exc_info=True)
        raise


def _parse_queue_message(msg: func.QueueMessage) -> FileProcessingRequest:
    """Parse the queue message into a FileProcessingRequest object."""
    try:
        message_body = msg.get_json()
        return FileProcessingRequest(**message_body)
    except ValidationError as e:
        logging.error(f"Validation error creating FileProcessingRequest: {e}")
        logging.error("Invalid fields: " + ", ".join(str(err["loc"]) for err in e.errors()))
        raise ValueError(f"Invalid message: {e}")
    except Exception as e:
        logging.error(f"Error parsing message: {str(e)}")
        logging.error(f"Raw message content: {msg.get_body().decode('utf-8')}")
        raise


def _get_document_intelligence_service() -> DocumentIntelligenceService:
    """Initialize and return Document Intelligence service."""
    return DocumentIntelligenceService(
        key=os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY"),
        endpoint=os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    )


def _get_repository() -> FilesRepository:
    """Initialize and return Files Repository."""
    cosmos_db_client = get_cosmos_db_client()
    return FilesRepository(cosmos_db_client)


def _extract_document_content(content: bytes, filename: str, document_intelligence_service: DocumentIntelligenceService) -> dict:
    """Extract text and structure from the document based on its file type."""
    if filename.endswith(".docx"):
        return DocxService.get_text_from_docx(content)
    else:
        # Process PDF file using Document Intelligence
        try:
            client = document_intelligence_service.client
            poller = client.begin_analyze_document("prebuilt-layout", document=content)
            result = poller.result(timeout=300)
            return document_intelligence_service.process_analysis_result(result)
        except Exception as e:
            logging.error(f"Error processing PDF document: {str(e)}", exc_info=True)
            raise


def _create_file_metadata(
    request: FileProcessingRequest, 
    structured_info: dict, 
    file_type: FileType, 
    document_analysis
) -> FileMetadataDb:
    """Create file metadata object with structured information."""
    request_data = request.model_dump()
    request_data.pop('type')  # Remove type from request data
    return FileMetadataDb(
        **request_data,
        **structured_info,
        type=file_type,
        document_analysis=document_analysis
    )


def _queue_for_matching(file_id: str, user_id: str, file_type: FileType):
    """Send file to matching queue for further processing."""
    queue_message = FileProcessingOutputQueueMessage(
        file_id=file_id,
        user_id=user_id,
        type=file_type
    )
    
    queue_service = QueueService(connection_string=os.getenv("AzureWebJobsStorage"))
    queue_service.create_queue_if_not_exists("matching-queue")
    queue_service.send_message("matching-queue", queue_message.model_dump_json())
    logging.info(f"File {file_id} queued for matching")
    
    