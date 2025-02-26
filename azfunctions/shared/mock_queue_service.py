class MockQueueService:
    def __init__(self, connection_string=None):
        self.messages = []

    def create_queue_if_not_exists(self, queue_name):
        pass

    def send_message(self, queue_name, message):
        self.messages.append((queue_name, message)) 