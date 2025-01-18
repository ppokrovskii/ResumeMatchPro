import os
import sys
from pathlib import Path

# add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from shared.queue_service import QueueService
from tests.test_base import BaseIntegrationTest

class TestQueueService(BaseIntegrationTest):
    def setUp(self):
        super().setUp()
        self.queue_service = QueueService(os.environ.get("AZURE_STORAGE_CONNECTION_STRING"))

    def tearDown(self):
        # Clean up any queues created during tests
        try:
            self.queue_service.delete_queue('test-queue')
        except:
            pass

    def test_create_queue(self):
        queue_name = 'test-queue'
        self.queue_service.create_queue_if_not_exists(queue_name)
        self.assertTrue(self.queue_service.exists(queue_name))

    def test_delete_queue(self):
        queue_name = 'test-queue'
        self.queue_service.create_queue_if_not_exists(queue_name)
        self.queue_service.delete_queue(queue_name)
        self.assertFalse(self.queue_service.exists(queue_name))

    def test_send_message(self):
        queue_name = 'test-queue'
        self.queue_service.create_queue_if_not_exists(queue_name)
        message = 'test-message'
        self.queue_service.send_message(queue_name, message)
        # result_message = self.queue_service.receive_message(queue_name)
        # self.assertEqual(result_message, message)

    # def test_dequeue_message(self):
    #     queue_name = 'test-queue'
    #     self.queue_service.create_queue_if_not_exists(queue_name)
    #     message = 'test-message'
    #     self.queue_service.send_message(queue_name, message)
    #     result_message = self.queue_service.receive_message(queue_name)
    #     self.assertEqual(result_message, message)
    #     self.queue_service.dequeue_message(queue_name, messages[0].id)
    #     messages = self.queue_service.get_messages(queue_name)
    #     self.assertEqual(len(messages), 0)

    # def test_get_messages(self):
    #     queue_name = 'test-queue'
    #     self.queue_service.create_queue_if_not_exists(queue_name)
    #     message = 'test-message'
    #     self.queue_service.enqueue_message(queue_name, message)
    #     messages = self.queue_service.get_messages(queue_name)
    #     self.assertEqual(messages[0].content, message)

    # def test_get_message(self):
    #     queue_name = 'test-queue'
    #     self.queue_service.create_queue_if_not_exists(queue_name)
    #     message = 'test-message'
    #     self.queue_service.enqueue_message(queue_name, message)
    #     messages = self.queue_service.get_messages(queue_name)
    #     self.assertEqual(messages[0].content, message)
    #     message = self.queue_service.get_message(queue_name, messages[0].id)
    #     self.assertEqual(message.content, message)
    #
    # def test_peek_messages(self):
    #     queue_name = 'test-queue'
    #     self.queue_service.create_queue_if_not_exists(queue_name)
    #     message = 'test-message'
    #     self.queue_service.enqueue_message(queue_name, message)
    #     messages = self.queue_service.peek_messages(queue_name)
    #     self.assertEqual(messages[0].content, message)

    # def test_peek_message(self):
    #     queue_name = 'test-queue'
    #     self.queue_service.create_queue_if_not_exists(queue_name)
    #     message = 'test-message'
    #     self.queue_service.enqueue_message(queue_name, message)
    #     messages = self.queue_service.peek_messages(queue_name)
    #     self.assertEqual(messages[0].content, message)
    #     message = self.queue_service.peek_message(queue_name, messages[0].id)
    #     self.assertEqual(message.content, message)
        