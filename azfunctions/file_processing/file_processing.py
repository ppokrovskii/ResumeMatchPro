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
        logging.error("Invalid fields: " + ", ".join(err["loc"] for err in e.errors()))
        raise ValueError(f"Invalid message: {e}")
    except Exception as e:
        logging.error(f"Error parsing message: {str(e)}")
        logging.error(f"Raw message content: {msg.get_body().decode('utf-8')}")
        raise
    
    try:
        logging.info("Creating FilesBlobService...")
        blob_service = FilesBlobService()
        logging.info(f"Blob service container name: {blob_service.container_name}")
        
        logging.info(f"Getting file content for {file_processing_request.filename}...")
        content = blob_service.get_file_content(blob_service.container_name, file_processing_request.filename)
        if not content:
            logging.error(f"Failed to get content for file {file_processing_request.filename}")
            raise ValueError(f"File content is empty or file not found: {file_processing_request.filename}")
        logging.info(f"Got file content, length: {len(content)} bytes")
        
        logging.info("Initializing Document Intelligence service...")
        document_intelligence_service = DocumentIntelligenceService(
            key=os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY"),
            endpoint=os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
        )
        
        # Process document based on type
        try:
            if file_processing_request.filename.endswith(".docx"):
                logging.info("Processing DOCX file...")
                structured_info = DocxService.get_text_from_docx(content)
            else:
                logging.info("Processing PDF file...")
                structured_info = document_intelligence_service.get_text_from_pdf(content)
            
            if not structured_info.get('text'):
                logging.warning("No text was extracted from the document")
            
            logging.info(f"Extracted text length: {len(structured_info['text']) if structured_info.get('text') else 0} characters")
            logging.info(f"Extracted {len(structured_info.get('pages', [])) if structured_info.get('pages') else 0} pages")
            logging.info(f"Extracted {len(structured_info.get('tables', [])) if structured_info.get('tables') else 0} tables")
            
            # Create file metadata with structured information
            logging.info("Creating file metadata with structured information...")
            file_metadata_db = FileMetadataDb(
                **file_processing_request.model_dump(),
                **structured_info
            )
            
            # Save metadata to database
            logging.info("Saving metadata to Cosmos DB...")
            cosmos_db_client = get_cosmos_db_client()
            files_repository = FilesRepository(cosmos_db_client)
            files_repository.upsert_file(file_metadata_db.model_dump(mode="json"))
            logging.info("Successfully saved metadata to Cosmos DB")
            
            # Send message to matching-queue queue with full text
            logging.info("Sending message to matching-queue...")
            file_processing_output_queue_message = FileProcessingOutputQueueMessage(
                text=structured_info['text'],
                **file_processing_request.model_dump()
            )
            queue_service = QueueService(connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
            queue_service.create_queue_if_not_exists("matching-queue")
            queue_service.send_message("matching-queue", file_processing_output_queue_message.model_dump_json())
            logging.info("Successfully sent message to matching-queue")
            
        except Exception as e:
            logging.error(f"Error processing document {file_processing_request.filename}: {str(e)}")
            logging.error(f"Document type: {'DOCX' if file_processing_request.filename.endswith('.docx') else 'PDF'}")
            logging.error(f"File size: {len(content)} bytes")
            logging.exception("Full traceback:")
            raise  # Re-raise the exception to trigger Azure Functions retry mechanism
            
    except Exception as e:
        logging.error(f"Fatal error in process_file: {str(e)}")
        logging.error(f"File: {getattr(file_processing_request, 'filename', 'unknown')}")
        logging.error(f"User ID: {getattr(file_processing_request, 'user_id', 'unknown')}")
        logging.exception("Full traceback:")
        raise  # Re-raise the exception to trigger Azure Functions retry mechanism
    
    