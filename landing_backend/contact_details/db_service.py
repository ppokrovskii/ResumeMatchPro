import os
from azure.cosmos import CosmosClient, PartitionKey

def get_cosmos_db_client():
    # read url and key from environment variables
    url = os.environ.get("COSMOS_URL")
    cosmos_key = os.environ.get("COSMOS_KEY")
    db_name = os.environ.get("COSMOS_DB_NAME")
    # create a CosmosClient
    client = CosmosClient(url=url, credential=(cosmos_key))
    # create db if not exists
    client.create_database_if_not_exists(db_name)
    return client.get_database_client(db_name)
