"""
Client for interacting with the OpenRouter API.
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional, Union

class OpenRouterClient:
    """Client for the OpenRouter API."""
    
    def __init__(
        self, 
        api_key: str,
        api_base: str = "https://openrouter.ai/api/v1",
        model: str = "deepseek/deepseek-r1-distill-llama-70b",
        timeout: int = 120
    ):
        """Initialize the OpenRouter client.
        
        Args:
            api_key: OpenRouter API key
            api_base: Base URL for the OpenRouter API
            model: Model to use for completions
            timeout: Timeout for API requests in seconds
        """
        self.api_key = api_key
        self.api_base = api_base
        self.model = model
        self.timeout = timeout
        
        if not api_key:
            raise ValueError("OpenRouter API key is required")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1500,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Generate a chat completion using the OpenRouter API.
        
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
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://legal-sanctions-rag.com",  # Use your domain here
            "X-Title": "Legal Sanctions RAG"  # Your app's name
        }
        
        # Debug the model parameter
        print(f"Using model: {self.model}")
        
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
            raise Exception(f"Error from OpenRouter API: {response.text}")
        
        return response.json()
    
    def generate_with_rag(
        self,
        query: str,
        context: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500,
        stream: bool = False
    ) -> Union[str, requests.Response]:
        """Generate a response with RAG context.
        
        Args:
            query: User query
            context: Context containing instructions and retrieved text
            chat_history: Previous conversation history
            temperature: Sampling temperature (0.1-1.0)
            max_tokens: Maximum number of tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Generated response text or streaming response object
        """
        if chat_history is None:
            chat_history = []
        
        # The context is actually a system message in this case
        system_message = context
        
        messages = [
            {"role": "system", "content": system_message},
            *chat_history,
            {"role": "user", "content": query}
        ]
        
        # For streaming, return the response object for processing by the caller
        if stream:
            return self.chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
        
        # For non-streaming, return the completed text
        response = self.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response["choices"][0]["message"]["content"]
        
    def stream_with_rag(
        self,
        query: str,
        context: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ):
        """Stream a response with RAG context.
        
        Args:
            query: User query
            context: Context containing instructions and retrieved text
            chat_history: Previous conversation history
            temperature: Sampling temperature (0.1-1.0)
            max_tokens: Maximum number of tokens to generate
            
        Yields:
            Text chunks as they are generated
        """
        # Get streaming response
        response = self.generate_with_rag(
            query=query,
            context=context,
            chat_history=chat_history,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        
        # Process the streaming response
        yield from self.process_streaming_response(response)
    
    def process_streaming_response(self, response):
        """Process a streaming response from the OpenRouter API.
        
        Args:
            response: Streaming response from the API
            
        Yields:
            Text chunks as they become available
        """
        if response.status_code != 200:
            raise Exception(f"Error from OpenRouter API: {response.text}")
        
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