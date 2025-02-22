# import libraries
import base64
import os
from azure.core.credentials import AzureKeyCredential
# from azure.ai.documentintelligence import DocumentIntelligenceClient
# from azure.ai.documentintelligence.models import AnalyzeResult
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from typing import Dict, List, Optional
import logging

from shared.models import DocumentPage, DocumentStyle, FileMetadataDb

class DocumentIntelligenceService:
    def __init__(self, key, endpoint):
        self.key = key  # "55ea103663564ddab3dc9f920eabf870"
        self.endpoint = endpoint  # "https://docintpavelpweurope.cognitiveservices.azure.com/"
        self.credential = AzureKeyCredential(key=key)
        self.client = DocumentAnalysisClient(endpoint=endpoint, credential=self.credential)
        
    def get_text_from_pdf(self, content) -> dict:
        try:
            logging.info("Starting PDF analysis with Document Intelligence service")
            poller = self.client.begin_analyze_document("prebuilt-layout", document=content)
            try:
                # Wait for the operation to complete with a timeout of 300 seconds (5 minutes)
                logging.info("Waiting for Document Intelligence analysis to complete (timeout: 300s)")
                result = poller.result(timeout=300)
                logging.info("Document Intelligence analysis completed successfully")
            except Exception as e:
                logging.error(f"Error waiting for Document Intelligence result: {str(e)}")
                logging.error(f"Operation ID (if available): {getattr(poller, 'operation_id', 'N/A')}")
                logging.error(f"Operation status (if available): {getattr(poller, 'status', 'N/A')}")
                raise
            
            # Initialize structured data containers
            pages = []
            paragraphs = []
            tables = []
            styles = {}
            
            # Process each page
            total_pages = len(result.pages)
            logging.info(f"Processing {total_pages} pages from the document")
            
            for page in result.pages:
                try:
                    page_tables = []
                    page_lines = []
                    
                    # Extract tables on this page
                    table_count = len(page.tables)
                    logging.debug(f"Processing {table_count} tables on page {page.page_number}")
                    
                    for table_id in page.tables:
                        try:
                            table = result.tables[table_id]
                            table_data = []
                            for row_idx in range(table.row_count):
                                row_data = []
                                for col_idx in range(table.column_count):
                                    cell = table.cells.get((row_idx, col_idx))
                                    cell_text = cell.content if cell else ""
                                    row_data.append(cell_text)
                                table_data.append(row_data)
                            page_tables.append(table_data)
                            tables.append(table_data)
                        except Exception as e:
                            logging.error(f"Error processing table {table_id} on page {page.page_number}: {str(e)}")
                            continue
                    
                    # Extract lines and their styles
                    line_count = len(page.lines)
                    logging.debug(f"Processing {line_count} lines on page {page.page_number}")
                    
                    for line in page.lines:
                        try:
                            line_text = line.content
                            page_lines.append(line_text)
                            
                            # Extract style information if available
                            if hasattr(line, 'appearance'):
                                style_name = f"style_{len(styles)}"
                                styles[style_name] = DocumentStyle(
                                    name=style_name,
                                    font_name=line.appearance.style.font_family if hasattr(line.appearance.style, 'font_family') else None,
                                    font_size=float(line.appearance.style.font_size) if hasattr(line.appearance.style, 'font_size') else None,
                                    is_bold=line.appearance.style.is_bold if hasattr(line.appearance.style, 'is_bold') else None,
                                    is_italic=line.appearance.style.is_italic if hasattr(line.appearance.style, 'is_italic') else None,
                                    is_underline=line.appearance.style.is_underline if hasattr(line.appearance.style, 'is_underline') else None
                                )
                        except Exception as e:
                            logging.error(f"Error processing line on page {page.page_number}: {str(e)}")
                            continue
                    
                    # Create DocumentPage object
                    pages.append(DocumentPage(
                        page_number=page.page_number,
                        content=page.content,
                        lines=page_lines,
                        tables=page_tables
                    ))
                    
                    # Add to paragraphs if content exists
                    if page.content.strip():
                        paragraphs.extend([p for p in page.content.split('\n') if p.strip()])
                        
                    logging.info(f"Successfully processed page {page.page_number} with {len(page_lines)} lines and {len(page_tables)} tables")
                except Exception as e:
                    logging.error(f"Error processing page {page.page_number}: {str(e)}")
                    continue
            
            # Create structured document info
            structured_info = {
                'text': result.content,
                'pages': pages,
                'paragraphs': paragraphs,
                'tables': tables,
                'styles': styles,
                'headers': None,  # PDF doesn't have explicit headers/footers
                'footers': None
            }
            
            logging.info(f"Document processing completed. Extracted {len(pages)} pages, {len(paragraphs)} paragraphs, {len(tables)} tables, and {len(styles)} styles")
            return structured_info
            
        except Exception as e:
            logging.error(f"Fatal error in get_text_from_pdf: {str(e)}")
            logging.exception("Full traceback:")
            raise

    def analyze_layout_from_file(self, file_path):
        with open(file_path, "rb") as f:
            content = f.read()
        return self.get_text_from_pdf(content)

#    def analyze_layout_from_blob(self, container_name, blob_name):
        # blob_service = FilesBlobService()
        # content = blob_service.get_file_content(container_name, blob_name)
        # return self.analyze_layout(content)

    def analyze_layout_from_base64(self, base64_str):
        content = base64.b64decode(base64_str)
        return self.get_text_from_pdf(content)

# helper functions

# def get_words(page, line):
#     result = []
#     for word in page.words:
#         if _in_span(word, line.spans):
#             result.append(word)
#     return result


# def _in_span(word, spans):
#     for span in spans:
#         if word.span.offset >= span.offset and (
#             word.span.offset + word.span.length
#         ) <= (span.offset + span.length):
#             return True
#     return False


# def analyze_layout(content):
#     # sample document
#     # formUrl = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-layout.pdf"
    
#     document_analysis_client = DocumentAnalysisClient(
#         endpoint=endpoint, credential=AzureKeyCredential(key)
#     )
#     # or prebuilt-document? prebuilt-layout?
#     poller = document_analysis_client.begin_analyze_document("prebuilt-read", document=content)
#     result = poller.result()
#     result_content = result.content
#     # useful vars: result.pages, result.tables, result.key_value_pairs, result.document_relations, result.styles, result.document_properties

#     return result_content
