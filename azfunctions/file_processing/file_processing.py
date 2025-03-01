import logging
import os
import azure.functions as func
import traceback
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
    try:
        logging.debug("DEBUG: process_file function called")
        logging.debug(f"DEBUG: Message type: {type(msg)}")
        logging.debug(f"DEBUG: Message content: {msg.get_body().decode('utf-8') if hasattr(msg, 'get_body') else 'No get_body method'}")
        
        # Step 1: Parse the queue message
        logging.debug("DEBUG: About to parse queue message")
        file_processing_request = _parse_queue_message(msg)
        logging.debug(f"DEBUG: Parsed request: {file_processing_request}")
        
        # Step 2: Create services
        logging.debug("DEBUG: About to create blob service")
        blob_service = FilesBlobService()
        logging.debug(f"DEBUG: Created blob service: {blob_service}")
        logging.debug(f"DEBUG: Blob service type: {type(blob_service)}")
        logging.debug(f"DEBUG: Blob service class: {blob_service.__class__}")
        logging.debug(f"DEBUG: Blob service module: {blob_service.__class__.__module__}")
        logging.debug(f"DEBUG: Blob service container name: {blob_service.container_name}")
        logging.debug("DEBUG: About to create document intelligence service")
        document_intelligence_service = DocumentIntelligenceService()
        logging.debug(f"DEBUG: Created document intelligence service: {document_intelligence_service}")
        logging.debug("DEBUG: About to create OpenAI service")
        openai_service = OpenAIService()
        logging.debug(f"DEBUG: Created OpenAI service: {openai_service}")
        
        # Step 3: Get file content
        logging.debug(f"DEBUG: About to get file content from {blob_service.container_name}/{file_processing_request.filename}")
        content = blob_service.get_file_content(file_processing_request.filename)
        logging.debug(f"DEBUG: Got file content, length: {len(content) if content else 'None'}")
        if not content:
            raise ValueError(f"File content is empty or file not found: {file_processing_request.filename}")
        
        # Step 4: Extract text from the document
        # Use different methods based on file type
        file_extension = os.path.splitext(file_processing_request.filename)[1].lower()
        logging.debug("DEBUG: About to extract document content")
        structured_info = _extract_document_content(
            content, 
            file_processing_request.filename,
            document_intelligence_service
        )
        logging.debug(f"DEBUG: Extracted document content: {structured_info.keys()}")
        
        # Step 5: Analyze the document using OpenAI
        logging.debug("DEBUG: About to analyze document with OpenAI")
        document_analysis = openai_service.analyze_document(
            text=structured_info['text'],
            pages=structured_info.get('pages', []),
            paragraphs=structured_info.get('paragraphs', [])
        )
        logging.debug(f"DEBUG: Document analysis result: {document_analysis}")
        
        # Step 6: Determine file type
        file_type = file_processing_request.type or document_analysis.document_type
        logging.debug(f"DEBUG: Determined file type: {file_type}")
        
        # Step 7: Create file metadata
        logging.debug("DEBUG: About to create file metadata")
        file_metadata = _create_file_metadata(file_processing_request, document_analysis)
        logging.debug("DEBUG: About to get repository")
        repository = FilesRepository(get_cosmos_db_client())
        logging.debug(f"DEBUG: Got repository: {repository}")
        logging.debug("DEBUG: About to upsert file")
        repository.upsert_file(file_metadata)
        logging.debug(f"DEBUG: Saved metadata to database")
        
        # Step 8: Queue for matching if needed
        logging.debug("DEBUG: About to queue for matching")
        _queue_for_matching(file_processing_request, file_type)
        logging.debug(f"DEBUG: Queued file for matching")
        
        return func.HttpResponse(f"File processed successfully. ID: {file_processing_request.id}.", status_code=200)
        
    except Exception as e:
        logging.error(f"ERROR in process_file: {str(e)}")
        logging.error(f"ERROR type: {type(e)}")
        # Print traceback for debugging
        logging.error(f"ERROR traceback: {traceback.format_exc()}")
        return func.HttpResponse(f"Error processing file: {str(e)}", status_code=500)


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
    
    