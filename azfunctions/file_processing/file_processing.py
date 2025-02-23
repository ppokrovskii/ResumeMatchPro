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
from shared.openai_service.openai_service import OpenAIService

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
                try:
                    logging.info("Calling Document Intelligence service with PDF content...")
                    logging.info(f"Document Intelligence Key length: {len(os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY', ''))}")
                    logging.info(f"Document Intelligence Endpoint: {os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')}")
                    logging.info(f"PDF content length: {len(content)} bytes")
                    
                    try:
                        # Initialize the client
                        logging.info("Creating DocumentAnalysisClient...")
                        client = document_intelligence_service.client
                        logging.info("DocumentAnalysisClient created successfully")
                        
                        # Begin analysis
                        logging.info("Beginning document analysis...")
                        poller = client.begin_analyze_document("prebuilt-layout", document=content)
                        logging.info("Document analysis started, waiting for result...")
                        
                        # Wait for the result
                        result = poller.result(timeout=300)
                        logging.info("Document analysis completed successfully")
                        
                        # Process the result
                        structured_info = document_intelligence_service.process_analysis_result(result)
                        logging.info("Successfully processed Document Intelligence result")
                    except Exception as e:
                        logging.error(f"Error in document analysis: {str(e)}")
                        logging.error(f"Error type: {type(e)}")
                        logging.exception("Full traceback:")
                        raise
                except Exception as e:
                    logging.error(f"Error in document_intelligence_service.get_text_from_pdf: {str(e)}")
                    logging.error(f"Document Intelligence Key: {os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')}")
                    logging.error(f"Document Intelligence Endpoint: {os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')}")
                    raise
            
            if not structured_info.get('text'):
                logging.warning("No text was extracted from the document")
            
            logging.info(f"Extracted text length: {len(structured_info['text']) if structured_info.get('text') else 0} characters")
            logging.info(f"Extracted {len(structured_info.get('pages', [])) if structured_info.get('pages') else 0} pages")
            logging.info(f"Extracted {len(structured_info.get('tables', [])) if structured_info.get('tables') else 0} tables")
            
            # Analyze document structure using OpenAI
            logging.info("Analyzing document structure with OpenAI...")
            openai_service = OpenAIService()
            document_analysis = openai_service.analyze_document(
                text=structured_info['text'],
                pages=structured_info.get('pages', []),
                paragraphs=structured_info.get('paragraphs', [])
            )
            logging.info(f"Document analyzed as {document_analysis.document_type}")
            
            # Create file metadata with structured information
            logging.info("Creating file metadata with structured information...")
            file_metadata_db = FileMetadataDb(
                **file_processing_request.model_dump(),
                **structured_info
            )
            
            # Save metadata to database
            logging.info("Getting Cosmos DB client...")
            cosmos_db_client = get_cosmos_db_client()
            logging.info("Creating FilesRepository...")
            repository = FilesRepository(cosmos_db_client)
            
            logging.info("Saving metadata to Cosmos DB...")
            try:
                repository.upsert_file(file_metadata_db.model_dump(mode="json"))
                logging.info("Successfully saved metadata to Cosmos DB")
            except Exception as e:
                logging.error(f"Error saving metadata to Cosmos DB: {str(e)}")
                raise
            
            # Create queue message
            logging.info("Creating queue message...")
            queue_message = FileProcessingOutputQueueMessage(
                file_id=file_processing_request.id,
                user_id=file_processing_request.user_id,
                type=file_processing_request.type
            )
            
            # Send message to queue
            logging.info("Initializing QueueService...")
            queue_service = QueueService()
            logging.info("Creating queue if not exists...")
            queue_service.create_queue_if_not_exists("matching-queue")
            logging.info("Sending message to queue...")
            queue_service.send_message("matching-queue", queue_message.model_dump_json())
            logging.info("Successfully sent message to queue")
            
        except Exception as e:
            logging.error(f"Error processing document: {str(e)}")
            raise
        
    except Exception as e:
        logging.error(f"Error in process_file: {str(e)}")
        raise
    
    