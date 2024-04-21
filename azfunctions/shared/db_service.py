from azure.cosmos import CosmosClient, PartitionKey

def get_cosmos_db_client():
    # Your connection string logic here
    client = CosmosClient(
            url="https://localhost:8081",
                credential=(
                    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
                ),
        )
    return client.get_database_client("resumematchpro")
    
def create_db_container_if_not_exists(self, container_id, unique_key_policy, partition_key: PartitionKey):
        db_client = get_cosmos_db_client()
        files_container = db_client.create_container_if_not_exists(
            id=container_id,
            partition_key=partition_key,
            unique_key_policy=unique_key_policy
        )
        return files_container
