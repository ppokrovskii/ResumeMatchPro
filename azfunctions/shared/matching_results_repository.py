from uuid import UUID, uuid4
from azure.cosmos import DatabaseProxy, PartitionKey
import shared.db_service as db_service

class MatchingResultsRepository:
    def __init__(self, db_client: DatabaseProxy):
        container_id = "matching-results"
        unique_key_policy = {
            'uniqueKeys': [
                {'paths': ['/user_id', '/cv/id', '/jd/id']}
            ]
        }
        partition_key = PartitionKey(path="/user_id")
        self.container = db_client.create_container_if_not_exists(
            id=container_id,
            unique_key_policy=unique_key_policy,
            partition_key=partition_key
        )

    # def add_result(self, matching_result: dict):
    #     self.container.create_item(matching_result)
        
    def upsert_result(self, matching_result: dict):
        # Query to check if a document with the same user_id, cv_id and jd_id exists
        query = "SELECT * FROM c WHERE c.user_id = @user_id AND c.cv.id = @cv_id AND c.jd.id = @jd_id"
        parameters = [
            {"name": "@user_id", "value": matching_result["user_id"]},
            {"name": "@cv_id", "value": matching_result["cv"]["id"]},
            {"name": "@jd_id", "value": matching_result["jd"]["id"]}
        ]
        items = list(self.container.query_items(query, parameters=parameters))
        if items:
            # Update the existing document
            matching_result["id"] = items[0]["id"]
            self.container.upsert_item(matching_result)
        else:
            # Create a new document
            self.container.upsert_item(matching_result)
            
    def delete_matching_results_by_file(self, user_id, file_id):
        if isinstance(user_id, UUID):
            user_id = str(user_id)
        if isinstance(file_id, UUID):
            file_id = str(file_id)
        query = "SELECT * FROM c WHERE c.user_id = @user_id AND (c.cv.id = @file_id OR c.jd.id = @file_id)"
        parameters = [{"name": "@user_id", "value": user_id}, {"name": "@file_id", "value": file_id}]
        items = list(self.container.query_items(query, parameters=parameters))
        for item in items:
            self.container.delete_item(item, partition_key=item["user_id"])
        
    def get_results_by_file_type_and_id(self, user_id, file_id, file_type):
        if file_type == "CV":
            return self.get_results_by_cv_id(user_id, file_id)
        elif file_type == "JD":
            return self.get_results_by_jd_id(user_id, file_id)
        else:
            raise ValueError("Invalid file type")

    def get_results_by_cv_id(self, user_id, cv_id):
        if isinstance(user_id, UUID):
            user_id = str(user_id)
        if isinstance(cv_id, UUID):
            # if the obj is uuid, we simply return the value of uuid
            cv_id = str(cv_id)
        #  order by overall_match_percentage desc
        query = "SELECT * FROM c WHERE c.user_id = @user_id AND c.cv.id = @cv_id order by c.overall_match_percentage desc"
        parameters = [{"name": "@user_id", "value": user_id}, {"name": "@cv_id", "value": cv_id}]
        items = list(self.container.query_items(query, parameters=parameters))
        return items
    
    def get_results_by_jd_id(self, user_id, jd_id):
        if isinstance(user_id, UUID):
            user_id = str(user_id)
        if isinstance(jd_id, UUID):
            # if the obj is uuid, we simply return the value of uuid
            jd_id = str(jd_id)
        query = "SELECT * FROM c WHERE c.user_id = @user_id AND c.jd.id = @jd_id order by c.overall_match_percentage desc"
        parameters = [{"name": "@user_id", "value": user_id}, {"name": "@jd_id", "value": jd_id}]
        items = list(self.container.query_items(query, parameters=parameters))
        return items
    
    def delete_all(self):
        items = list(self.container.read_all_items())
        for item in items:
            self.container.delete_item(item, partition_key=item["user_id"])
