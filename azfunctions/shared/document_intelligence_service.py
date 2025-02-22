# import libraries
import base64
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from typing import Dict, List, Optional
import logging

from shared.models import DocumentPage, DocumentStyle, FileMetadataDb, TableCell, Line, Point

class DocumentIntelligenceService:
    def __init__(self, key, endpoint):
        self.key = key
        self.endpoint = endpoint
        self.credential = AzureKeyCredential(key=key)
        self.client = DocumentAnalysisClient(endpoint=endpoint, credential=self.credential)
        
    def process_analysis_result(self, result) -> dict:
        try:
            logging.info("Processing Document Intelligence analysis result")
            
            # Initialize structured data containers
            pages = []
            tables = []
            styles = {}
            
            # Debug log the result object structure
            logging.info(f"Result object has {len(result.pages)} pages")
            for idx, page in enumerate(result.pages):
                logging.info(f"Page {idx + 1} attributes:")
                logging.info(f"  - page_number: {page.page_number}")
                logging.info(f"  - lines count: {len(page.lines) if hasattr(page, 'lines') else 0}")
                logging.info(f"  - width: {page.width if hasattr(page, 'width') else 'N/A'}")
                logging.info(f"  - height: {page.height if hasattr(page, 'height') else 'N/A'}")
                logging.info(f"  - unit: {page.unit if hasattr(page, 'unit') else 'N/A'}")
            
            # Extract paragraphs directly from result
            paragraphs = []
            if hasattr(result, 'paragraphs'):
                for para in result.paragraphs:
                    if para.content.strip():
                        paragraphs.append(para.content)
            else:
                # Fallback to content splitting if paragraphs not available
                if result.content.strip():
                    paragraphs.extend([p for p in result.content.split('\n\n') if p.strip()])
            
            logging.info(f"Extracted {len(paragraphs)} paragraphs from document")
            
            # Process each page
            total_pages = len(result.pages)
            logging.info(f"Processing {total_pages} pages from the document")
            
            # First, process all tables in the document
            for table in result.tables:
                try:
                    table_data = []
                    for row_idx in range(table.row_count):
                        row_data = []
                        for col_idx in range(table.column_count):
                            cell = table.cells.get((row_idx, col_idx))
                            if cell:
                                cell_info = TableCell(
                                    text=cell.content,
                                    polygon=[Point(x=p.x, y=p.y) for p in cell.bounding_regions[0].polygon] if hasattr(cell, 'bounding_regions') else None
                                )
                                row_data.append(cell_info)
                            else:
                                row_data.append(TableCell(text=""))
                        table_data.append(row_data)
                    tables.append(table_data)
                except Exception as e:
                    logging.error(f"Error processing table: {str(e)}")
                    continue
            
            # Then process each page
            for page in result.pages:
                try:
                    # Debug logging
                    logging.info(f"Processing page {page.page_number}")
                    
                    page_lines = []
                    
                    # Extract lines
                    if not hasattr(page, 'lines'):
                        logging.warning(f"Page {page.page_number} has no lines attribute")
                        continue
                        
                    for line in page.lines:
                        try:
                            if not hasattr(line, 'content'):
                                logging.warning(f"Line in page {page.page_number} has no content attribute")
                                continue
                                
                            line_info = Line(
                                content=line.content,
                                polygon=[Point(x=p.x, y=p.y) for p in line.polygon] if hasattr(line, 'polygon') else None
                            )
                            page_lines.append(line_info)
                            
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
                    
                    # Create page content from lines
                    page_content = "\n".join(line.content for line in page.lines)
                    
                    # Create DocumentPage object with enhanced information
                    page_obj = DocumentPage(
                        page_number=page.page_number,
                        content=page_content,
                        lines=page_lines,
                        tables=tables,  # Pass all tables to each page for now
                        angle=page.angle if hasattr(page, 'angle') else None,
                        width=page.width if hasattr(page, 'width') else None,
                        height=page.height if hasattr(page, 'height') else None,
                        unit=page.unit if hasattr(page, 'unit') else None
                    )
                    pages.append(page_obj)
                    logging.info(f"Successfully processed page {page.page_number} with {len(page_lines)} lines")
                    
                except Exception as e:
                    logging.error(f"Error processing page {page.page_number}: {str(e)}")
                    logging.exception("Full traceback:")
                    continue
            
            # Create structured document info
            structured_info = {
                'text': result.content,
                'pages': pages,
                'paragraphs': paragraphs,
                'tables': tables,
                'styles': styles,
                'headers': None,  # PDF doesn't have explicit headers/footers
                'footers': None,
                'languages': result.languages if hasattr(result, 'languages') else None
            }
            
            logging.info(f"Document processing completed. Extracted {len(pages)} pages, {len(paragraphs)} paragraphs, {len(tables)} tables, and {len(styles)} styles")
            return structured_info
            
        except Exception as e:
            logging.error(f"Fatal error in process_analysis_result: {str(e)}")
            logging.exception("Full traceback:")
            raise
        
    def get_text_from_pdf(self, content) -> dict:
        try:
            logging.info("Starting PDF analysis with Document Intelligence service")
            poller = self.client.begin_analyze_document("prebuilt-layout", document=content)
            try:
                # Wait for the operation to complete with a timeout of 300 seconds (5 minutes)
                logging.info("Waiting for Document Intelligence analysis to complete (timeout: 300s)")
                result = poller.result(timeout=300)
                logging.info("Document Intelligence analysis completed successfully")
                return self.process_analysis_result(result)
            except Exception as e:
                logging.error(f"Error waiting for Document Intelligence result: {str(e)}")
                logging.error(f"Operation ID (if available): {getattr(poller, 'operation_id', 'N/A')}")
                logging.error(f"Operation status (if available): {getattr(poller, 'status', 'N/A')}")
                raise
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
