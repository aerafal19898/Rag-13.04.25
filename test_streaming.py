#!/usr/bin/env python
"""
Test script for streaming API.
"""

import os
import sys
import json
import requests
from pathlib import Path

print("Testing Streaming API")
print("-------------------------------------")

# Define API endpoint for streaming
base_url = "http://localhost:5000"
chat_endpoint = f"{base_url}/api/chats"

# 1. Create a new chat
print("1. Creating a new chat...")
create_response = requests.post(
    chat_endpoint,
    json={"title": "Test Streaming Chat", "dataset": "EU-Sanctions"}
)

if create_response.status_code != 200:
    print(f"Error creating chat: {create_response.text}")
    sys.exit(1)

chat_id = create_response.json()["id"]
print(f"Created chat with ID: {chat_id}")

# 2. Send a test message using streaming endpoint
print("\n2. Testing streaming API...")
test_query = "What are the penalties for sanctions violations?"
print(f"Query: {test_query}")

try:
    # Use the streaming endpoint
    streaming_url = f"{chat_endpoint}/{chat_id}/messages/stream"
    
    print(f"\nSending streaming request to: {streaming_url}")
    
    # Send the request in streaming mode
    response = requests.post(
        streaming_url,
        json={"message": test_query, "dataset": "EU-Sanctions"},
        stream=True
    )
    
    if response.status_code != 200:
        print(f"Error with streaming request: {response.text}")
        sys.exit(1)
        
    print("\nStreaming response:")
    print("-" * 50)
    
    # Process the streaming response
    full_response = ""
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                data_str = line[6:]  # Remove 'data: ' prefix
                if data_str.strip():
                    try:
                        data = json.loads(data_str)
                        
                        # Handle chunk of text
                        if 'chunk' in data:
                            chunk = data['chunk']
                            full_response += chunk
                            print(chunk, end='', flush=True)
                            
                        # Handle completion
                        if 'done' in data and data['done']:
                            print("\n\nStreaming complete!")
                            
                        # Handle error
                        if 'error' in data:
                            print(f"\nError: {data['error']}")
                            
                    except json.JSONDecodeError:
                        print(f"Error parsing JSON: {data_str}")
    
    print("\n" + "-" * 50)
    print(f"\nFull response length: {len(full_response)} characters")
    
except Exception as e:
    print(f"Exception during streaming: {str(e)}")
    
print("\nDone.")