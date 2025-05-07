#!/usr/bin/env python
"""
Test script for streaming API using unittest and TestClient.
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

class TestStreamingAPI(unittest.TestCase):
    # Use setUpClass to initialize the client once
    @classmethod
    def setUpClass(cls):
        # Revert to standard TestClient initialization
        cls.client = TestClient(app)
        cls.chat_id = None
        # Use relative paths for API calls within tests
        # Use the singular chat endpoint defined in the gateway
        cls.base_chat_url = "/api/chat"

    # Ensure tearDownClass to close the client transport
    @classmethod
    def tearDownClass(cls):
        pass # Assume TestClient handles cleanup

    def test_1_create_chat(self):
        """Test creating a new chat session needed for streaming."""
        print("\nTesting: Create Chat (Streaming)")
        # Use relative path defined in setUpClass
        chat_endpoint = self.base_chat_url # Use singular endpoint
        response = self.client.post(
            chat_endpoint,
            json={"title": "Test Streaming Chat", "dataset": "EU-Sanctions"}
        )
        self.assertEqual(response.status_code, 200, f"Error creating chat: {response.text}")
        response_data = response.json()
        self.__class__.chat_id = response_data.get("id")
        self.assertIsNotNone(self.chat_id, "Chat ID was not returned.")
        print(f"Created chat with ID: {self.chat_id}")

    def test_2_streaming_message(self):
        """Test sending a message via the streaming endpoint."""
        print("\nTesting: Streaming Message")
        self.assertIsNotNone(self.chat_id, "Chat ID not set, cannot test streaming.")

        # Use relative path for the streaming URL, based on singular chat endpoint
        streaming_url = f"{self.base_chat_url}/{self.chat_id}/messages/stream"
        test_query = "What are the penalties for sanctions violations?"
        print(f"Query: {test_query}")

        full_response_content = ""
        received_done = False
        received_error = None

        try:
            # Use the client's stream method, which now uses the configured httpx client
            with self.client.stream(
                "POST",
                streaming_url, # Now relative, TestClient prepends base_url
                json={"message": test_query, "dataset": "EU-Sanctions"}
            ) as response:
                self.assertEqual(response.status_code, 200, f"Error status code {response.status_code} from streaming endpoint.")

                print("\nStreaming response:")
                print("-" * 50)

                for line in response.iter_lines():
                    if line.startswith('data: '):
                        data_str = line[len('data: '):]
                        if data_str.strip():
                            try:
                                data = json.loads(data_str)
                                if 'chunk' in data:
                                    chunk = data['chunk']
                                    full_response_content += chunk
                                    print(chunk, end='', flush=True)
                                if 'done' in data and data['done']:
                                    received_done = True
                                    print("\n\n(Received done signal)")
                                if 'error' in data:
                                    received_error = data['error']
                                    print(f"\n(Received error: {received_error})")
                            except json.JSONDecodeError:
                                print(f"\nError parsing JSON: {data_str}")
                                self.fail(f"Failed to parse JSON data from stream: {data_str}")

                print("\n" + "-" * 50)

        except Exception as e:
            self.fail(f"Exception during streaming test: {str(e)}")

        self.assertTrue(received_done, "Did not receive the 'done: true' signal in the stream.")
        self.assertIsNone(received_error, f"Received an error during streaming: {received_error}")
        self.assertTrue(len(full_response_content) > 0, "Streaming response content was empty.")
        print(f"\nFull response length: {len(full_response_content)} characters. Streaming test passed.")

if __name__ == '__main__':
    unittest.main()

# Old code removed:
# print("Testing Streaming API")
# print("-------------------------------------")
# ... (rest of the old script) ...