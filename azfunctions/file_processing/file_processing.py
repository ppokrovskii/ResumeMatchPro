import logging
import os
import traceback
from typing import Any, Dict, List, Optional

import azure.functions as func
from file_processing.schemas import (
    FileProcessingOutputQueueMessage,
    FileProcessingRequest,
)
from pydantic import BaseModel, ValidationError
from shared.blob_service import FilesBlobService
from shared.db_service import get_cosmos_db_client
from shared.document_intelligence_service import DocumentIntelligenceService
from shared.docx_service import DocxService
from shared.files_repository import FilesRepository
from shared.models import FileMetadataDb, FileStatus
from shared.openai_service.openai_service import OpenAIService
from shared.queue_service import QueueService

# create blueprint with Queue trigger
file_processing_bp = func.Blueprint()

# Constants
MATCHING_QUEUE_NAME = "matching-queue"


class DocumentContent(BaseModel):
    """
    Represents the structured content extracted from a document.
    """

    text: str
    pages: List[Any] = []
    paragraphs: List[str] = []
    tables: List[Any] = []
    styles: Dict[str, Any] = {}
    headers: Optional[Any] = None
    footers: Optional[Any] = None
    languages: Optional[List[str]] = None


class FileProcessor:
    """
    Handles the file processing workflow.
    This class is stateless - file processing state is maintained only within the process method.
    Services are injected via constructor for better testability.
    """

    def __init__(
        self,
        repository: FilesRepository,
        blob_service: FilesBlobService,
        document_intelligence_service: DocumentIntelligenceService,
        openai_service: OpenAIService,
        queue_service: QueueService,
    ):
        # Initialize services from parameters
        self.repository = repository
        self.blob_service = blob_service
        self.document_intelligence_service = document_intelligence_service
        self.openai_service = openai_service
        self.queue_service = queue_service

    @staticmethod
    def create_with_default_services():
        """
        Factory method to create a FileProcessor with default services.
        This simplifies instantiation when you don't need custom service implementations.
        """
        repository = FilesRepository(get_cosmos_db_client())
        blob_service = FilesBlobService()
        document_intelligence_service = DocumentIntelligenceService(
            key=os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY"),
            endpoint=os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"),
        )
        openai_service = OpenAIService()
        queue_service = QueueService(os.environ.get("AZURE_STORAGE_CONNECTION_STRING"))

        return FileProcessor(
            repository=repository,
            blob_service=blob_service,
            document_intelligence_service=document_intelligence_service,
            openai_service=openai_service,
            queue_service=queue_service,
        )

    def update_status(
        self,
        file_metadata: FileMetadataDb,
        status: FileStatus,
        status_message: str,
        **additional_fields,
    ) -> FileMetadataDb:
        """
        Update the file metadata status and persist it to the database.
        Returns the updated metadata.
        """
        file_metadata.status = status
        file_metadata.status_message = status_message

        # Update any additional fields
        for key, value in additional_fields.items():
            setattr(file_metadata, key, value)

        # Persist to database
        self.repository.upsert_file(file_metadata.model_dump(mode="json"))

        return file_metadata

    def get_file_content(self, filename: str) -> bytes:
        """
        Get the file content from blob storage.
        """
        content = self.blob_service.get_file_content(
            self.blob_service.container_name, filename
        )
        if not content:
            raise ValueError(f"File content is empty or file not found: {filename}")
        return content

    def extract_text(self, content: bytes, filename: str) -> DocumentContent:
        """
        Extract text from the document based on file type.
        """
        if filename.endswith(".docx"):
            raw_info = DocxService.get_text_from_docx(content)
        else:
            raw_info = self.document_intelligence_service.get_text_from_pdf(content)

        return DocumentContent(**raw_info)

    def analyze_document(self, structured_info: DocumentContent):
        """
        Analyze the document content using OpenAI.
        """
        return self.openai_service.analyze_document(
            text=structured_info.text,
            pages=structured_info.pages,
            paragraphs=structured_info.paragraphs,
        )

    def queue_for_matching(
        self, file_id, user_id, document_type: str, filename: str, url: str
    ):
        """
        Queue the processed file for matching.
        """
        self.queue_service.create_queue_if_not_exists(MATCHING_QUEUE_NAME)
        message = FileProcessingOutputQueueMessage(
            file_id=file_id,
            user_id=user_id,
            type=document_type,
            filename=filename,
            url=url,
        )
        self.queue_service.send_message(
            MATCHING_QUEUE_NAME,
            message.model_dump_json(),
        )
        logging.info(f"File {file_id} queued for matching")
        return message

    def process(
        self, request: FileProcessingRequest
    ) -> FileProcessingOutputQueueMessage:
        """
        Process the file through the complete workflow.
        All file metadata state is maintained within this method.
        Returns the final file metadata after processing.
        """
        # Initialize file metadata from the request
        file_metadata = FileMetadataDb(**request.model_dump())

        try:
            # Start processing
            file_metadata = self.update_status(
                file_metadata, FileStatus.PROCESSING, "File processing started"
            )

            # Get file content
            try:
                content = self.get_file_content(file_metadata.filename)
            except ValueError as e:
                file_metadata = self.update_status(
                    file_metadata,
                    FileStatus.ERROR,
                    f"File content error: {str(e)}",
                )
                raise e

            # Extract text
            try:
                file_metadata = self.update_status(
                    file_metadata,
                    FileStatus.EXTRACTING_TEXT,
                    "Extracting text from document",
                )
                structured_info = self.extract_text(content, file_metadata.filename)
            except Exception as e:
                file_metadata = self.update_status(
                    file_metadata,
                    FileStatus.ERROR,
                    f"Text extraction error: {str(e)}",
                )
                raise e

            # Analyze document
            try:
                file_metadata = self.update_status(
                    file_metadata, FileStatus.ANALYZING, "Analyzing document content"
                )
                document_analysis = self.analyze_document(structured_info)
                file_metadata = self.update_status(
                    file_metadata,
                    FileStatus.COMPLETED,
                    "File processing completed",
                    type=file_metadata.type or document_analysis.document_type,
                    document_type=str(document_analysis.document_type.value),
                    structure=document_analysis.structure.model_dump(mode="json"),
                )

                # Queue for matching
                try:
                    return self.queue_for_matching(
                        file_id=file_metadata.id,
                        user_id=file_metadata.user_id,
                        document_type=document_analysis.document_type,
                        filename=file_metadata.filename,
                        url=file_metadata.url,
                    )
                except Exception as e:
                    logging.error(f"Error queuing for matching: {str(e)}")
                    return file_metadata
            except Exception as e:
                file_metadata = self.update_status(
                    file_metadata,
                    FileStatus.ERROR,
                    f"Document analysis error: {str(e)}",
                )
                raise e
        except ValidationError as e:
            error_msg = f"Validation error: {str(e)}"
            logging.error(error_msg)
            logging.error(
                f"Invalid fields: {', '.join(str(err['loc']) for err in e.errors())}"
            )
            # Update file status to ERROR
            file_metadata = self.update_status(
                file_metadata, FileStatus.ERROR, error_msg
            )
            raise
        except Exception as e:
            error_msg = f"Error processing file: {str(e)}"
            logging.error(error_msg)
            logging.error(f"Error type: {type(e)}")
            logging.error(f"Error traceback: {traceback.format_exc()}")
            # Update file status to ERROR
            file_metadata = self.update_status(
                file_metadata, FileStatus.ERROR, error_msg
            )
            raise


@file_processing_bp.queue_trigger(
    arg_name="msg",
    queue_name="processing-queue",
    connection="AzureWebJobsStorage",
    maxDequeueCount=1,
)
def process_file_function(msg: func.QueueMessage) -> None:
    """
    Azure Function trigger for processing files.
    Takes a message from the queue and delegates processing to FileProcessor.
    """
    try:
        message_body = msg.get_json()
        request = FileProcessingRequest(**message_body)

        # Create processor using the factory method
        processor = FileProcessor.create_with_default_services()

        # Process the request
        processor.process(request)

        logging.info("File processed successfully")

    except Exception as e:
        logging.error(f"Error in process_file_function: {str(e)}")
