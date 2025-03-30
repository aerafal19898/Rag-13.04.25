"""
Models for chat history storage.
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

class ChatStorage:
    """Manages chat histories, folders, and messages."""
    
    def __init__(self, storage_dir: str = None):
        """Initialize with the storage directory."""
        if storage_dir is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            storage_dir = os.path.join(base_dir, "data", "chats")
        
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Make sure we have the folders directory
        self.folders_dir = os.path.join(self.storage_dir, "folders")
        os.makedirs(self.folders_dir, exist_ok=True)
        
        # Initialize folders file if it doesn't exist
        self.folders_file = os.path.join(self.storage_dir, "folders.json")
        if not os.path.exists(self.folders_file):
            with open(self.folders_file, 'w') as f:
                json.dump({
                    "folders": [
                        {"id": "default", "name": "Default", "created_at": time.time()}
                    ]
                }, f)
    
    def create_chat(self, title: str = None, folder_id: str = "default") -> str:
        """Create a new chat and return its ID."""
        chat_id = f"chat_{int(time.time())}_{os.urandom(4).hex()}"
        timestamp = time.time()
        
        if title is None:
            title = "New Chat"
            
        chat_data = {
            "id": chat_id,
            "title": title,
            "created_at": timestamp,
            "updated_at": timestamp,
            "folder_id": folder_id,
            "dataset": "Default",
            "messages": []
        }
        
        # Save the chat file
        chat_file = os.path.join(self.storage_dir, f"{chat_id}.json")
        with open(chat_file, 'w') as f:
            json.dump(chat_data, f, indent=2)
            
        return chat_id
    
    def get_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a chat by ID."""
        chat_file = os.path.join(self.storage_dir, f"{chat_id}.json")
        if not os.path.exists(chat_file):
            return None
            
        with open(chat_file, 'r') as f:
            return json.load(f)
    
    def update_chat(self, chat_id: str, data: Dict[str, Any]) -> bool:
        """Update a chat's metadata."""
        chat = self.get_chat(chat_id)
        if chat is None:
            return False
            
        # Update fields
        for key, value in data.items():
            if key != 'id' and key != 'messages':  # Don't allow changing ID or messages directly
                chat[key] = value
                
        chat['updated_at'] = time.time()
            
        # Save the chat file
        chat_file = os.path.join(self.storage_dir, f"{chat_id}.json")
        with open(chat_file, 'w') as f:
            json.dump(chat, f, indent=2)
            
        return True
    
    def delete_chat(self, chat_id: str) -> dict:
        """Delete a chat by ID and return the most recent chat above it."""
        chat_file = os.path.join(self.storage_dir, f"{chat_id}.json")
        if not os.path.exists(chat_file):
            return {"success": False, "message": "Chat not found"}
        
        # Get the folder_id of the chat to be deleted
        with open(chat_file, 'r') as f:
            chat_data = json.load(f)
            folder_id = chat_data.get('folder_id', 'default')
        
        # List all chats in the same folder, sorted by updated_at (newest first)
        folder_chats = self.list_chats(folder_id)
        
        # Remove the chat being deleted from the list
        folder_chats = [c for c in folder_chats if c['id'] != chat_id]
        
        # Delete the chat file
        os.remove(chat_file)
        
        # Return the next most recent chat in the folder if available
        if folder_chats:
            return {
                "success": True, 
                "next_chat": folder_chats[0]['id'],
                "message": "Chat deleted successfully"
            }
        
        return {"success": True, "next_chat": None, "message": "Chat deleted successfully"}
    
    def add_message(self, chat_id: str, role: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """Add a message to a chat."""
        chat = self.get_chat(chat_id)
        if chat is None:
            return False
            
        timestamp = time.time()
        message = {
            "id": f"msg_{int(timestamp)}_{os.urandom(4).hex()}",
            "role": role,
            "content": content,
            "created_at": timestamp
        }
        
        if metadata is not None:
            message["metadata"] = metadata
            
        chat['messages'].append(message)
        chat['updated_at'] = timestamp
            
        # Save the chat file
        chat_file = os.path.join(self.storage_dir, f"{chat_id}.json")
        with open(chat_file, 'w') as f:
            json.dump(chat, f, indent=2)
            
        return True
    
    def list_chats(self, folder_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all chats, optionally filtered by folder."""
        chats = []
        
        for filename in os.listdir(self.storage_dir):
            if filename.startswith('chat_') and filename.endswith('.json'):
                chat_file = os.path.join(self.storage_dir, filename)
                with open(chat_file, 'r') as f:
                    chat = json.load(f)
                    
                    # Filter by folder if specified
                    if folder_id is None or chat.get('folder_id') == folder_id:
                        # Don't include the messages in the listing for efficiency
                        chat_summary = {k: v for k, v in chat.items() if k != 'messages'}
                        chat_summary['message_count'] = len(chat.get('messages', []))
                        chats.append(chat_summary)
        
        # Sort by updated_at (newest first)
        return sorted(chats, key=lambda x: x.get('updated_at', 0), reverse=True)
    
    def create_folder(self, name: str) -> str:
        """Create a new folder and return its ID."""
        folder_id = f"folder_{int(time.time())}_{os.urandom(4).hex()}"
        
        with open(self.folders_file, 'r') as f:
            folders_data = json.load(f)
            
        folders_data['folders'].append({
            "id": folder_id,
            "name": name,
            "created_at": time.time()
        })
        
        with open(self.folders_file, 'w') as f:
            json.dump(folders_data, f, indent=2)
            
        return folder_id
    
    def list_folders(self) -> List[Dict[str, Any]]:
        """List all folders."""
        with open(self.folders_file, 'r') as f:
            folders_data = json.load(f)
            
        return folders_data['folders']
    
    def delete_folder(self, folder_id: str) -> bool:
        """Delete a folder."""
        with open(self.folders_file, 'r') as f:
            folders_data = json.load(f)
            
        # Find the folder
        folder_index = None
        for i, folder in enumerate(folders_data['folders']):
            if folder['id'] == folder_id:
                folder_index = i
                break
                
        if folder_index is None:
            return False
            
        # Remove the folder
        folders_data['folders'].pop(folder_index)
        
        with open(self.folders_file, 'w') as f:
            json.dump(folders_data, f, indent=2)
            
        return True
    
    def move_chat_to_folder(self, chat_id: str, folder_id: str) -> bool:
        """Move a chat to a different folder."""
        return self.update_chat(chat_id, {"folder_id": folder_id})