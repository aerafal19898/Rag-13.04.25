#!/usr/bin/env python
"""
Test script for user feedback API.
"""

import os
import sys
import json
import requests
from pathlib import Path

print("Testing User Feedback API")
print("-------------------------------------")

# Define API endpoints
base_url = "http://localhost:5000"
chat_endpoint = f"{base_url}/api/chats"
feedback_endpoint = f"{base_url}/api/feedback"

# 1. Create a new chat
print("1. Creating a new chat...")
create_response = requests.post(
    chat_endpoint,
    json={"title": "Test Feedback Chat", "dataset": "EU-Sanctions"}
)

if create_response.status_code != 200:
    print(f"Error creating chat: {create_response.text}")
    sys.exit(1)

chat_id = create_response.json()["id"]
print(f"Created chat with ID: {chat_id}")

# 2. Add a message to get a response we can provide feedback on
print("\n2. Sending a test message...")
test_query = "What are the penalties for violations of EU sanctions?"
print(f"Query: {test_query}")

message_response = requests.post(
    f"{chat_endpoint}/{chat_id}/messages",
    json={"message": test_query, "dataset": "EU-Sanctions"}
)

if message_response.status_code != 200:
    print(f"Error sending message: {message_response.text}")
    sys.exit(1)

# 3. Get the chat to find the assistant message ID
print("\n3. Retrieving chat to get message ID...")
chat_response = requests.get(f"{chat_endpoint}/{chat_id}")

if chat_response.status_code != 200:
    print(f"Error getting chat: {chat_response.text}")
    sys.exit(1)

chat_data = chat_response.json()
messages = chat_data.get("messages", [])

# Find the most recent assistant message
assistant_message = None
for msg in reversed(messages):
    if msg.get("role") == "assistant":
        assistant_message = msg
        break

if not assistant_message:
    print("No assistant message found to provide feedback on.")
    sys.exit(1)

message_id = assistant_message.get("id")
print(f"Found assistant message with ID: {message_id}")

# 4. Submit feedback
print("\n4. Submitting feedback...")
feedback_types = ["helpful", "not_helpful", "inaccurate"]

for feedback_type in feedback_types:
    print(f"\nSubmitting '{feedback_type}' feedback...")
    
    feedback_data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "feedback_type": feedback_type,
        "feedback_text": f"Test feedback of type: {feedback_type}"
    }
    
    feedback_response = requests.post(
        feedback_endpoint,
        json=feedback_data
    )
    
    if feedback_response.status_code == 200:
        print(f"Successfully submitted '{feedback_type}' feedback!")
    else:
        print(f"Error submitting feedback: {feedback_response.text}")

# 5. Check if feedback was stored
print("\n5. Checking if feedback was stored...")
chat_response = requests.get(f"{chat_endpoint}/{chat_id}")

if chat_response.status_code != 200:
    print(f"Error getting chat: {chat_response.text}")
    sys.exit(1)

chat_data = chat_response.json()
messages = chat_data.get("messages", [])

# Find the assistant message again
assistant_message = None
for msg in messages:
    if msg.get("id") == message_id:
        assistant_message = msg
        break

if assistant_message and assistant_message.get("metadata", {}).get("feedback"):
    feedback = assistant_message["metadata"]["feedback"]
    print(f"Found {len(feedback)} feedback entries:")
    for i, fb in enumerate(feedback):
        print(f"  {i+1}. Type: {fb.get('type')}, Text: {fb.get('text')}")
else:
    print("No feedback found in the message metadata.")

print("\nDone.")