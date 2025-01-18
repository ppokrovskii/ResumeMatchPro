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
    except ValidationError as e:
        raise ValueError(f"Invalid message: {e}")
    blob_service = FilesBlobService()
    # TODO move container name to config
    content = blob_service.get_file_content(blob_service.container_name, file_processing_request.filename)
    document_intelligence_service = DocumentIntelligenceService(key=os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY"),
                                                                endpoint=os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"))
    if file_processing_request.filename.endswith(".docx"):
        text = DocxService.get_text_from_docx(content)
    else:
        text = document_intelligence_service.get_text_from_pdf(content)
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
    
    