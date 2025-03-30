"""
Client for interacting with the DeepSeek API.
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional, Union

class DeepSeekClient:
    """Client for the DeepSeek API."""
    
    def __init__(
        self, 
        api_key: str,
        api_base: str = "https://api.deepseek.com/v1",
        model: str = "deepseek-ai/deepseek-coder-33b-instruct",
        timeout: int = 120
    ):
        """Initialize the DeepSeek client.
        
        Args:
            api_key: DeepSeek API key
            api_base: Base URL for the DeepSeek API
            model: Model to use for completions
            timeout: Timeout for API requests in seconds
        """
        self.api_key = api_key
        self.api_base = api_base
        self.model = model
        self.timeout = timeout
        
        if not api_key:
            raise ValueError("DeepSeek API key is required")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Generate a chat completion using the DeepSeek API.
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum number of tokens to generate
            stream: Whether to stream the response
            
        Returns:
            API response
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        response = requests.post(
            f"{self.api_base}/chat/completions",
            headers=headers,
            json=payload,
            timeout=self.timeout,
            stream=stream
        )
        
        if stream:
            return response
        
        if response.status_code != 200:
            raise Exception(f"Error from DeepSeek API: {response.text}")
        
        return response.json()
    
    def generate_with_rag(
        self,
        query: str,
        context: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> str:
        """Generate a response with RAG context.
        
        Args:
            query: User query
            context: Retrieved context text
            chat_history: Previous conversation history
            temperature: Sampling temperature (0.1-1.0)
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Generated response text
        """
        if chat_history is None:
            chat_history = []
        
        # Use the context directly (system message now handled in main.py)
        system_message = context
        
        messages = [
            {"role": "system", "content": system_message},
            *chat_history,
            {"role": "user", "content": query}
        ]
        
        response = self.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response["choices"][0]["message"]["content"]
    
    def process_streaming_response(self, response):
        """Process a streaming response from the DeepSeek API.
        
        Args:
            response: Streaming response from the API
            
        Yields:
            Text chunks as they become available
        """
        if response.status_code != 200:
            raise Exception(f"Error from DeepSeek API: {response.text}")
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    json_data = line[6:]  # Remove 'data: ' prefix
                    if json_data.strip() == "[DONE]":
                        break
                    
                    try:
                        data = json.loads(json_data)
                        chunk = data["choices"][0]["delta"].get("content", "")
                        if chunk:
                            yield chunk
                    except json.JSONDecodeError:
                        print(f"Error parsing JSON: {json_data}")
                        continue