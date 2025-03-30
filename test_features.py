#!/usr/bin/env python
"""
Test script for new RAG features.
"""

import os
import sys
from pathlib import Path

# Add project directories to path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "app"))

from app.utils.document_processor import LegalDocumentProcessor
from app.config import CHROMA_DIR, EMBEDDING_MODEL

print("Testing 1: Hybrid Search and Reranking")
print("-------------------------------------")

# Initialize document processor
processor = LegalDocumentProcessor(
    embedding_model=EMBEDDING_MODEL,
    chroma_path=CHROMA_DIR
)

# List available collections
import chromadb
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
collections = chroma_client.list_collections()
print(f"Available collections: {[c.name for c in collections]}")

if collections:
    # Test hybrid search on first collection
    collection_name = collections[0].name
    print(f"\nTesting on collection: {collection_name}")
    
    # Test query
    test_query = "What are the penalties for sanctions violations?"
    
    print(f"\nQuery: {test_query}")
    
    # Test with vector search only (baseline)
    vector_results = processor.query_dataset(
        dataset_name=collection_name,
        query=test_query,
        n_results=3,
        use_hybrid_search=False,
        use_reranking=False
    )
    
    print("\nVector search results:")
    for i, (doc, meta) in enumerate(zip(vector_results["documents"][0], vector_results["metadatas"][0])):
        print(f"Result {i+1}:")
        print(f"Source: {meta.get('source', 'Unknown')}")
        print(f"Preview: {doc[:100]}...\n")
    
    # Test with hybrid search
    hybrid_results = processor.query_dataset(
        dataset_name=collection_name,
        query=test_query,
        n_results=3,
        use_hybrid_search=True,
        use_reranking=False
    )
    
    print("\nHybrid search results:")
    for i, (doc, meta) in enumerate(zip(hybrid_results["documents"][0], hybrid_results["metadatas"][0])):
        print(f"Result {i+1}:")
        print(f"Source: {meta.get('source', 'Unknown')}")
        print(f"Preview: {doc[:100]}...\n")
    
    # Test with hybrid search and reranking
    hybrid_reranked_results = processor.query_dataset(
        dataset_name=collection_name,
        query=test_query,
        n_results=3,
        use_hybrid_search=True,
        use_reranking=True
    )
    
    print("\nHybrid search with reranking results:")
    for i, (doc, meta) in enumerate(zip(hybrid_reranked_results["documents"][0], hybrid_reranked_results["metadatas"][0])):
        print(f"Result {i+1}:")
        print(f"Source: {meta.get('source', 'Unknown')}")
        print(f"Preview: {doc[:100]}...\n")
    
    print("\nTest 2: Legal Metadata Extraction")
    print("-------------------------------------")
    
    # Check if any metadata has been extracted
    for i, meta in enumerate(hybrid_reranked_results["metadatas"][0]):
        if "legal_metadata" in meta:
            print(f"Legal metadata found in result {i+1}:")
            print(meta["legal_metadata"])
            print()
else:
    print("No collections found. Please create a collection first.")