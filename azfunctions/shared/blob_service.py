import os
from azure.storage.blob import BlobServiceClient


class FilesBlobService:
    def __init__(self) -> None:
        self.blob_service_client = self.create_files_blob_service_client()
        self.container_name = "resume-match-pro-files"
        
    def create_files_blob_service_client(self):
        # Azure Blob Storage info
        connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        return blob_service_client

    def upload_blob(self, container_name, filename, content):
        # create container if doesn't exist
        container_client = self.blob_service_client.get_container_client(container_name)
        if not container_client.exists():
            container_client.create_container()
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=filename)
        blob_client.upload_blob(content, overwrite=True)
        return blob_client.url
    
    def delete_blob(self, container_name, filename):
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=filename)
        blob_client.delete_blob()

    def blob_exists(self, container_name, filename):
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=filename)
        return blob_client.exists()
    
    def get_file_content(self, container_name, filename):
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=filename)
        return blob_client.download_blob().readall()
    
    def get_file_content_by_url(self, blob_url: str):
        blob_client = self.blob_service_client.get_blob_client(blob_url)
        return blob_client.download_blob().readall()