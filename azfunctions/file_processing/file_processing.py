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
from shared.models import FileMetadataDb
from shared.queue_service import QueueService

# create blueprint with Queue trigger
file_processing_bp = func.Blueprint()

@file_processing_bp.queue_trigger(arg_name="msg", queue_name="processing-queue", connection="AzureWebJobsStorage")
def process_file(msg: func.QueueMessage):
    logging.info(f"file_processing function called with a message: {msg.get_body().decode('utf-8')}")
    try:
        file_processing_request = FileProcessingRequest(**msg.get_json())
        logging.info(f"Created FileProcessingRequest: {file_processing_request.model_dump_json()}")
    except ValidationError as e:
        logging.error(f"Validation error creating FileProcessingRequest: {e}")
        raise ValueError(f"Invalid message: {e}")
    
    logging.info("Creating FilesBlobService...")
    blob_service = FilesBlobService()
    logging.info(f"Blob service container name: {blob_service.container_name}")
    
    # TODO move container name to config
    logging.info(f"Getting file content for {file_processing_request.filename}...")
    content = blob_service.get_file_content(blob_service.container_name, file_processing_request.filename)
    logging.info(f"Got file content, length: {len(content) if content else 0} bytes")
    
    document_intelligence_service = DocumentIntelligenceService(key=os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY"),
                                                                endpoint=os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"))
    if file_processing_request.filename.endswith(".docx"):
        logging.info("Processing DOCX file...")
        text = DocxService.get_text_from_docx(content)
    else:
        logging.info("Processing PDF file...")
        text = document_intelligence_service.get_text_from_pdf(content)
    logging.info(f"Extracted text length: {len(text) if text else 0} characters")
    
    # save metadata to database
    file_metadata_db = FileMetadataDb(text=text, **file_processing_request.model_dump())
    cosmos_db_client = get_cosmos_db_client()
    files_repository = FilesRepository(cosmos_db_client)
    files_repository.upsert_file(file_metadata_db.model_dump(mode="json"))
    
    # send message to matching-queue queue
    file_processing_output_queue_message = FileProcessingOutputQueueMessage(text=text, **file_processing_request.model_dump())
    queue_service = QueueService(connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
    queue_service.create_queue_if_not_exists("matching-queue")
    queue_service.send_message("matching-queue", file_processing_output_queue_message.model_dump_json())
    
    