from uuid import UUID, uuid4
from azure.cosmos import DatabaseProxy, PartitionKey
from shared.models import FileMetadataDb
import shared.db_service as db_service


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
    
    def delete_file(self, **kwargs):
         if 'user_id' in kwargs and 'filename' in kwargs:
             return self._delete_file_by_user_id_and_filename(kwargs['user_id'], kwargs['filename'])
         elif 'file_id' in kwargs:
            return self._delete_file_by_id(kwargs['file_id'])
        
    def _delete_file_by_user_id_and_filename(self, user_id: UUID, filename: str):
        query = "SELECT * FROM c WHERE c.user_id = @user_id AND c.filename = @filename"
        parameters = [
            {"name": "@user_id", "value": str(user_id)},
            {"name": "@filename", "value": filename}
        ]
        items = list(self.container.query_items(query, parameters=parameters))
        if items:
            self.container.delete_item(items[0], partition_key=user_id)
            return True
        return False
    
    def _delete_file_by_id(self, file_id):
        raise NotImplementedError
    
    def get_file_by_id(self, user_id, file_id) -> FileMetadataDb:
        if isinstance(file_id, UUID):
            file_id = str(file_id)
        if isinstance(user_id, UUID):
            user_id = str(user_id)
        query = "SELECT * FROM c WHERE c.user_id = @user_id AND c.id = @id"
        parameters = [
            {"name": "@user_id", "value": user_id},
            {"name": "@id", "value": file_id}
        ]
        items = list(self.container.query_items(query, parameters=parameters))
        if items:
            return FileMetadataDb(**items[0])
        return None