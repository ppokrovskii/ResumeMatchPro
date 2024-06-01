from azure.cosmos import DatabaseProxy, PartitionKey

from contact_details.models import ContactDetailsDbModelResponse

class ContactDetailsRepository:
    def __init__(self, db_client: DatabaseProxy):
        container_id = "contact_details"
        unique_key_policy = {
            'uniqueKeys': [
                {'paths': ['/email']}
            ]
        }
        particion_key = PartitionKey(path="/email")
        self.container = db_client.create_container_if_not_exists(
            id=container_id,
            unique_key_policy=unique_key_policy,
            partition_key=particion_key
        )

    def upsert_contact_details(self, contact_details: dict) -> dict:
        # Validate that email exists in the contact details
        if "email" not in contact_details:
            raise ValueError("The 'email' field is required in contact details")

        # Log the input data for debugging
        print("Upserting contact details:", contact_details)
        # Query to check if a document with the same email exists
        query = "SELECT * FROM c WHERE c.email = @email"
        parameters = [
            {"name": "@email", "value": contact_details["email"]}
        ]
        items = list(self.container.query_items(query, parameters=parameters))
        if items:
            # Update the existing document
            contact_details["id"] = items[0]["id"]
        result = self.container.upsert_item(contact_details)
        return ContactDetailsDbModelResponse(**result)
    
    def get_contact_details_from_db(self, email: str) -> ContactDetailsDbModelResponse:
        query = "SELECT * FROM c WHERE c.email = @email"
        parameters = [
            {"name": "@email", "value": email}
        ]
        items = list(self.container.query_items(query, parameters=parameters))
        if items:
            return ContactDetailsDbModelResponse(**items[0])
        return None
    
    def delete_all(self):
        items = list(self.container.read_all_items())
        for item in items:
            self.container.delete_item(item, partition_key=item["email"])
            
    def get_all_contact_details(self) -> list[ContactDetailsDbModelResponse]:
        items = list(self.container.read_all_items())
        return [ContactDetailsDbModelResponse(**item) for item in items]