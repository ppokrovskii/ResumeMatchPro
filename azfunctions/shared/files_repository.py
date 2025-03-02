from uuid import UUID, uuid4
from azure.cosmos import DatabaseProxy, PartitionKey
from shared.models import FileMetadataDb
import shared.db_service as db_service
import logging
from typing import Optional


class FilesRepository:
    def __init__(self, db_client: DatabaseProxy):
        container_id = "files"
        unique_key_policy = {
            'uniqueKeys': [
                {'paths': ['/user_id', '/filename']}
            ]
        }
        partition_key = PartitionKey(path="/user_id")
        self.container = db_client.create_container_if_not_exists(
            id=container_id,
            unique_key_policy=unique_key_policy,
            partition_key=partition_key
        )
        
    def upsert_file(self, file: dict):
        # Query to check if a document with the same user_id and filename exists
        query = "SELECT * FROM c WHERE c.user_id = @user_id AND c.filename = @filename"
        parameters = [
            {"name": "@user_id", "value": file["user_id"]},
            {"name": "@filename", "value": file["filename"]}
        ]
        items = list(self.container.query_items(query, parameters=parameters))
        if items:
            # Update the existing document
            file["id"] = items[0]["id"]
            result = self.container.upsert_item(file)
        else:
            # Create a new document
            result = self.container.upsert_item(file)
        return FileMetadataDb(**result)
            
            
    def get_files_from_db(self, user_id, file_type=None) -> list[FileMetadataDb]:
        query = "SELECT * FROM c"
        parameters = []
        if user_id:
            query += " WHERE c.user_id = @user_id"
            parameters.append({"name": "@user_id", "value": user_id})
        if file_type:
            if user_id:
                query += " AND c.type = @file_type"
            else:
                query += " WHERE c.type = @file_type"
            parameters.append({"name": "@file_type", "value": file_type})
        items = list(self.container.query_items(query, parameters=parameters))
        items = [FileMetadataDb(**item) for item in items]
        return items
    
    def delete_all(self):
        items = list(self.container.read_all_items())
        for item in items:
            self.container.delete_item(item, partition_key=item["user_id"])
    
    def delete_file(self, user_id: str, file_id: str = None, filename: str = None):
        """Delete a file from the database by user_id and either file_id or filename."""
        if file_id:
            file = self.get_file_by_id(user_id, file_id)
        elif filename:
            query = "SELECT * FROM c WHERE c.user_id = @user_id AND c.filename = @filename"
            parameters = [
                {"name": "@user_id", "value": user_id},
                {"name": "@filename", "value": filename}
            ]
            items = list(self.container.query_items(query, parameters=parameters))
            file = FileMetadataDb(**items[0]) if items else None
        else:
            raise ValueError("Either file_id or filename must be provided")

        if file:
            self.container.delete_item(item=str(file.id), partition_key=user_id)
            return True
        return False
    
    def get_file_by_id(self, user_id: str, file_id: str | UUID):
        """Get a file by user_id and file_id."""
        if isinstance(file_id, UUID):
            file_id = str(file_id)
        try:
            # First check if file exists for any user
            query = "SELECT * FROM c WHERE c.id = @file_id"
            parameters = [{"name": "@file_id", "value": file_id}]
            items = list(self.container.query_items(query, parameters=parameters, enable_cross_partition_query=True))
            if not items:
                return None
            
            file = FileMetadataDb(**items[0])
            if file.user_id != user_id:
                raise PermissionError("You don't have permission to access this file")
            
            return file
        except PermissionError:
            raise
        except Exception as e:
            logging.error(f"Error getting file by ID: {str(e)}")
            return None

    def get_file(self, file_id: str, user_id: str) -> Optional[FileMetadataDb]:
        """Get a file by ID and verify the user has access to it."""
        try:
            # Query for the file with the given ID
            query = "SELECT * FROM c WHERE c.id = @file_id"
            parameters = [{"name": "@file_id", "value": file_id}]
            items = list(self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            # If no file found, return None
            if not items:
                return None
            
            file = FileMetadataDb(**items[0])
            
            # Check if the user has access to this file
            if file.user_id != user_id:
                logging.error("Error getting file by ID: You don't have permission to access this file")
                raise PermissionError("You don't have permission to access this file")
            
            return file
            
        except PermissionError as e:
            raise
        except Exception as e:
            logging.error(f"Error getting file by ID: {str(e)}")
            return None