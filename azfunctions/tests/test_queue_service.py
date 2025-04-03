import base64
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from azure.storage.queue import QueueServiceClient
from dotenv import load_dotenv

# add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))
load_dotenv(Path(__file__).parent / ".env.test")

from shared.queue_service import QueueService
from tests.test_base import BaseIntegrationTest

# Load test environment variables


class TestQueueService(BaseIntegrationTest):
    def setUp(self):
        super().setUp()
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.queue_name = "test-queue"
        self.queue_service = QueueService(self.connection_string)

    def tearDown(self):
        # Clean up any queues created during tests
        try:
            self.queue_service.delete_queue("test-queue")
        except:
            pass

    def test_create_queue(self):
        # Create queue
        self.queue_service.create_queue_if_not_exists(self.queue_name)

        # Verify queue exists
        self.assertTrue(self.queue_service.exists(self.queue_name))

        # Cleanup
        self.queue_service.delete_queue(self.queue_name)

    def test_delete_queue(self):
        # Create queue first
        self.queue_service.create_queue_if_not_exists(self.queue_name)

        # Delete queue
        self.queue_service.delete_queue(self.queue_name)

        # Verify queue is deleted
        self.assertFalse(self.queue_service.exists(self.queue_name))

    def test_send_message(self):
        # Create queue first
        self.queue_service.create_queue_if_not_exists(self.queue_name)

        # Send message
        message = "test message"
        self.queue_service.send_message(self.queue_name, message)

        # Verify message was sent
        queue_service_client = QueueServiceClient.from_connection_string(
            self.connection_string
        )
        queue_client = queue_service_client.get_queue_client(self.queue_name)
        messages = list(queue_client.receive_messages())
        self.assertEqual(len(messages), 1)
        received_message = base64.b64decode(messages[0].content).decode("utf-8")
        self.assertEqual(received_message, message)

        # Cleanup
        queue_client.delete_queue()


if __name__ == "__main__":
    unittest.main()
