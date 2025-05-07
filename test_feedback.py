#!/usr/bin/env python
"""
Test script for user feedback API using unittest and TestClient.
"""

import unittest
import os
import json
from fastapi.testclient import TestClient
import httpx # Import httpx
# Assuming your FastAPI app instance is defined in app.main
# Adjust the import if your app instance is located elsewhere
try:
    # Import the specific FastAPI app instance used by the gateway service
    from app.services.api_gateway import app
except ImportError as e:
    print(f"Error importing FastAPI app from api_gateway: {e}")
    # Fallback for parsing, though tests will likely fail if primary import fails
    from fastapi import FastAPI
    app = FastAPI()


class TestFeedbackAPI(unittest.TestCase):
    # Use setUpClass to initialize the client once for all tests in this class
    @classmethod
    def setUpClass(cls):
        # Revert to standard TestClient initialization
        cls.client = TestClient(app)
        cls.chat_id = None
        cls.message_id = None
        # Use relative paths for API calls within tests, TestClient handles the base_url
        # Use the singular chat endpoint defined in the gateway
        cls.base_chat_url = "/api/chat"
        cls.base_feedback_url = "/api/feedback"

    # Ensure tearDownClass to close the client transport
    @classmethod
    def tearDownClass(cls):
        # Cleanup might involve closing client if needed, but usually TestClient handles it
        pass

    def test_1_create_chat(self):
        """Test creating a new chat session."""
        print("\nTesting: Create Chat")
        chat_endpoint = self.base_chat_url # Use singular endpoint
        response = self.client.post(
            chat_endpoint,
            json={"title": "Test Feedback Chat", "dataset": "EU-Sanctions"}
        )
        self.assertEqual(response.status_code, 200, f"Error creating chat: {response.text}")
        response_data = response.json()
        self.__class__.chat_id = response_data.get("id")
        self.assertIsNotNone(self.chat_id, "Chat ID was not returned.")
        print(f"Created chat with ID: {self.chat_id}")

    def test_2_send_message(self):
        """Test sending a message to the created chat."""
        print("\nTesting: Send Message")
        self.assertIsNotNone(self.chat_id, "Chat ID not set, cannot send message.")
        message_endpoint = f"{self.base_chat_url}/{self.chat_id}/messages"
        test_query = "What are the penalties for violations of EU sanctions?"
        response = self.client.post(
            message_endpoint,
            json={"message": test_query, "dataset": "EU-Sanctions"}
        )
        self.assertEqual(response.status_code, 200, f"Error sending message: {response.text}")
        print(f"Sent message to chat {self.chat_id}")

    def test_3_get_message_id(self):
        """Test retrieving the chat and finding the assistant message ID."""
        print("\nTesting: Get Message ID")
        self.assertIsNotNone(self.chat_id, "Chat ID not set, cannot retrieve chat.")
        chat_endpoint = f"{self.base_chat_url}/{self.chat_id}"
        response = self.client.get(chat_endpoint)
        self.assertEqual(response.status_code, 200, f"Error getting chat: {response.text}")

        chat_data = response.json()
        messages = chat_data.get("messages", [])
        assistant_message = None
        for msg in reversed(messages):
            if msg.get("role") == "assistant":
                assistant_message = msg
                break

        self.assertIsNotNone(assistant_message, "No assistant message found in chat.")
        self.__class__.message_id = assistant_message.get("id")
        self.assertIsNotNone(self.message_id, "Assistant message ID not found.")
        print(f"Found assistant message with ID: {self.message_id}")

    def test_4_submit_feedback(self):
        """Test submitting feedback for the assistant message."""
        print("\nTesting: Submit Feedback")
        self.assertIsNotNone(self.chat_id, "Chat ID not set, cannot submit feedback.")
        self.assertIsNotNone(self.message_id, "Message ID not set, cannot submit feedback.")
        feedback_endpoint = self.base_feedback_url # Feedback endpoint likely separate
        feedback_types = ["helpful", "not_helpful", "inaccurate"]

        for feedback_type in feedback_types:
            print(f"Submitting '{feedback_type}' feedback...")
            feedback_data = {
                "chat_id": self.chat_id,
                "message_id": self.message_id,
                "feedback_type": feedback_type,
                "feedback_text": f"Test feedback of type: {feedback_type}"
            }
            response = self.client.post(feedback_endpoint, json=feedback_data)
            self.assertEqual(response.status_code, 200, f"Error submitting {feedback_type} feedback: {response.text}")
            print(f"Successfully submitted '{feedback_type}' feedback.")

    def test_5_check_feedback_stored(self):
        """Test checking if the submitted feedback was stored correctly."""
        print("\nTesting: Check Feedback Stored")
        self.assertIsNotNone(self.chat_id, "Chat ID not set, cannot check feedback.")
        self.assertIsNotNone(self.message_id, "Message ID not set, cannot check feedback.")
        chat_endpoint = f"{self.base_chat_url}/{self.chat_id}"
        response = self.client.get(chat_endpoint)
        self.assertEqual(response.status_code, 200, f"Error getting chat: {response.text}")

        chat_data = response.json()
        messages = chat_data.get("messages", [])
        assistant_message = None
        for msg in messages:
            if msg.get("id") == self.message_id:
                assistant_message = msg
                break

        self.assertIsNotNone(assistant_message, f"Could not find message with ID {self.message_id} after submitting feedback.")
        feedback_list = assistant_message.get("metadata", {}).get("feedback")
        self.assertIsNotNone(feedback_list, "Feedback list not found in message metadata.")
        self.assertIsInstance(feedback_list, list, "Feedback metadata is not a list.")
        self.assertEqual(len(feedback_list), 3, f"Expected 3 feedback entries, found {len(feedback_list)}.")
        print(f"Found {len(feedback_list)} feedback entries as expected.")

# Remove the old procedural script code below this line

if __name__ == '__main__':
    unittest.main()

# Old code removed:
# print("Testing User Feedback API")
# print("-------------------------------------")
# ... (rest of the old script) ...