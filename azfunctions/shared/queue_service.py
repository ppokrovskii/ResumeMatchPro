import base64
from azure.storage.queue import QueueServiceClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError

class QueueService:
    def __init__(self, connection_string):
        # self.connection_string = connection_string
        # default_credential = DefaultAzureCredential()
        self.queue_service_client = QueueServiceClient.from_connection_string(connection_string)

    def create_queue_if_not_exists(self, queue_name):
        # check if queue exists
        queue_client = self.queue_service_client.get_queue_client(queue_name)
        try:
            queue_client.create_queue()
        except ResourceExistsError:
            pass
        

    def send_message(self, queue_name, message):
        queue_client = self.queue_service_client.get_queue_client(queue_name)
        message = base64.b64encode(message.encode('utf-8')).decode('utf-8')
        queue_client.send_message(message)

    # def receive_message(self, queue_name):
    #     queue_client = self.queue_service_client.get_queue_client(queue_name)
    #     messages = queue_client.receive_messages()

    def delete_queue(self, queue_name):
        queue_client = self.queue_service_client.get_queue_client(queue_name)
        queue_client.delete_queue()
        
    def exists(self, queue_name):
        queue_client = self.queue_service_client.get_queue_client(queue_name)
        try:
            queue_client.get_queue_properties()
        except ResourceNotFoundError:
            return False
        return True