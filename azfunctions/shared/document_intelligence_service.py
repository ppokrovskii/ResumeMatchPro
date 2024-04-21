# import libraries
import base64
import os
from azure.core.credentials import AzureKeyCredential
# from azure.ai.documentintelligence import DocumentIntelligenceClient
# from azure.ai.documentintelligence.models import AnalyzeResult
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential


class DocumentIntelligenceService:
    def __init__(self, key, endpoint):
        self.key = key  # "55ea103663564ddab3dc9f920eabf870"
        self.endpoint = endpoint  # "https://docintpavelpweurope.cognitiveservices.azure.com/"
        self.credential = AzureKeyCredential(key=key)
        self.client = DocumentAnalysisClient(endpoint=endpoint, credential=self.credential)
        
    def get_text_from_pdf(self, content):
        poller = self.client.begin_analyze_document("prebuilt-read", document=content)
        result = poller.result()
        result_content = result.content
        return result_content

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
