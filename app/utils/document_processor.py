"""
Utilities for processing legal documents and creating embeddings.
"""

import os
from typing import List, Dict, Any, Tuple
import uuid
from langchain_community.embeddings import HuggingFaceEmbeddings
from unstructured.partition.pdf import partition_pdf
from unstructured.cleaners.core import clean_extra_whitespace
import chromadb
import torch
from tqdm import tqdm

class LegalDocumentProcessor:
    """Processor for legal documents with specialized handling for legal terminology."""
    
    def __init__(
        self, 
        embedding_model: str, 
        chroma_path: str,
        device: str = None
    ):
        """Initialize the document processor.
        
        Args:
            embedding_model: Name of the HuggingFace embedding model
            chroma_path: Path to the Chroma DB
            device: Device to use for embeddings ('cuda' or 'cpu')
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={"device": self.device}
        )
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
    
    def process_document(self, file_path: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """Process a single document and return chunked text.
        
        Args:
            file_path: Path to the document
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Extract text from PDF using unstructured
        elements = partition_pdf(
            file_path,
            extract_images_in_pdf=False,
            infer_table_structure=True,
        )
        
        # Process text elements
        texts = []
        for element in elements:
            if hasattr(element, 'text'):
                text = element.text
                if text:
                    # Clean text
                    text = clean_extra_whitespace(text)
                    texts.append(text)
        
        # Chunk the text
        chunks = self._chunk_text(texts, chunk_size, chunk_overlap)
        
        return chunks
    
    def _chunk_text(self, texts: List[str], chunk_size: int, chunk_overlap: int) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks of specified size.
        
        Args:
            texts: List of text strings
            chunk_size: Maximum chunk size
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of text chunks with metadata
        """
        import re
        import nltk
        
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
            
        from nltk.tokenize import sent_tokenize
        
        # Precompile regex patterns for legal metadata extraction
        section_pattern = re.compile(r"(Article|Section|Regulation|ARTICLE|SECTION|§)\s+(\d+[\.\d]*\w*)", re.IGNORECASE)
        subsection_pattern = re.compile(r"([a-z])\)\s+", re.IGNORECASE)
        numbered_pattern = re.compile(r"(\d+)\.\s+")
        
        chunks_with_metadata = []
        
        for text_idx, text in enumerate(texts):
            # Skip very short texts
            if len(text) < 100:
                chunks_with_metadata.append({
                    "text": text,
                    "metadata": {
                        "type": "short_fragment",
                        "length": len(text)
                    }
                })
                continue
                
            # 1. Semantic-based chunking - identify logical units first
            # Try to split by sections/articles if we can identify them
            sections = []
            section_matches = list(section_pattern.finditer(text))
            
            if len(section_matches) > 1:
                # Text contains identifiable sections
                for i in range(len(section_matches)):
                    start_pos = section_matches[i].start()
                    # If this is the last section, go to the end of text
                    if i == len(section_matches) - 1:
                        end_pos = len(text)
                    else:
                        end_pos = section_matches[i+1].start()
                    
                    section_text = text[start_pos:end_pos].strip()
                    section_id = section_matches[i].group(0).strip()
                    section_num = section_matches[i].group(2).strip()
                    
                    sections.append({
                        "text": section_text,
                        "metadata": {
                            "type": "legal_section",
                            "section_id": section_id,
                            "section_num": section_num,
                            "length": len(section_text)
                        }
                    })
            else:
                # No clear sections found, use paragraph or sentence-based chunking
                # First try to split by paragraphs (empty lines)
                paragraphs = re.split(r"\n\s*\n", text)
                
                if len(paragraphs) > 1:
                    for para in paragraphs:
                        if len(para.strip()) > 0:
                            sections.append({
                                "text": para.strip(),
                                "metadata": {
                                    "type": "paragraph",
                                    "length": len(para.strip())
                                }
                            })
                else:
                    # Single paragraph - use sentence-based chunking
                    sections.append({
                        "text": text,
                        "metadata": {
                            "type": "full_text",
                            "length": len(text)
                        }
                    })
            
            # 2. Recursive chunking - break large sections into smaller units
            for section in sections:
                section_text = section["text"]
                metadata = section["metadata"]
                
                # If section is small enough, keep it as is
                if len(section_text) <= chunk_size:
                    chunks_with_metadata.append({
                        "text": section_text,
                        "metadata": metadata
                    })
                    continue
                
                # For larger sections, do recursive chunking
                # Level 1: Try to split by subsections if they exist
                subsections = []
                subsection_matches = list(subsection_pattern.finditer(section_text))
                
                if len(subsection_matches) > 1:
                    for i in range(len(subsection_matches)):
                        start_pos = subsection_matches[i].start()
                        # If this is the last subsection, go to the end
                        if i == len(subsection_matches) - 1:
                            end_pos = len(section_text)
                        else:
                            end_pos = subsection_matches[i+1].start()
                        
                        subsec_text = section_text[start_pos:end_pos].strip()
                        subsec_id = subsection_matches[i].group(0).strip()
                        
                        # Merge metadata with parent section info
                        subsec_metadata = metadata.copy()
                        subsec_metadata.update({
                            "type": "subsection",
                            "subsection_id": subsec_id,
                            "length": len(subsec_text)
                        })
                        
                        subsections.append({
                            "text": subsec_text,
                            "metadata": subsec_metadata
                        })
                else:
                    # Level 2: Try to split by numbered items
                    numbered_matches = list(numbered_pattern.finditer(section_text))
                    
                    if len(numbered_matches) > 1:
                        for i in range(len(numbered_matches)):
                            start_pos = numbered_matches[i].start()
                            # If this is the last item, go to the end
                            if i == len(numbered_matches) - 1:
                                end_pos = len(section_text)
                            else:
                                end_pos = numbered_matches[i+1].start()
                            
                            item_text = section_text[start_pos:end_pos].strip()
                            item_num = numbered_matches[i].group(1).strip()
                            
                            # Merge metadata with parent section info
                            item_metadata = metadata.copy()
                            item_metadata.update({
                                "type": "numbered_item",
                                "item_num": item_num,
                                "length": len(item_text)
                            })
                            
                            subsections.append({
                                "text": item_text,
                                "metadata": item_metadata
                            })
                    else:
                        # Level 3: Split by sentences with semantic grouping
                        sentences = sent_tokenize(section_text)
                        
                        # Group sentences into logical units
                        current_group = []
                        current_length = 0
                        
                        for sentence in sentences:
                            sentence = sentence.strip()
                            sentence_len = len(sentence)
                            
                            # If adding this sentence would exceed chunk size, save current group
                            if current_length + sentence_len > chunk_size and current_group:
                                grouped_text = " ".join(current_group)
                                group_metadata = metadata.copy()
                                group_metadata.update({
                                    "type": "sentence_group",
                                    "sentence_count": len(current_group),
                                    "length": len(grouped_text)
                                })
                                
                                subsections.append({
                                    "text": grouped_text,
                                    "metadata": group_metadata
                                })
                                
                                current_group = [sentence]
                                current_length = sentence_len
                            else:
                                current_group.append(sentence)
                                current_length += sentence_len
                        
                        # Add any remaining sentences
                        if current_group:
                            grouped_text = " ".join(current_group)
                            group_metadata = metadata.copy()
                            group_metadata.update({
                                "type": "sentence_group",
                                "sentence_count": len(current_group),
                                "length": len(grouped_text)
                            })
                            
                            subsections.append({
                                "text": grouped_text,
                                "metadata": group_metadata
                            })
                
                # Process all subsections
                for subsection in subsections:
                    subsec_text = subsection["text"]
                    subsec_metadata = subsection["metadata"]
                    
                    # If subsection is small enough, keep it as is
                    if len(subsec_text) <= chunk_size:
                        chunks_with_metadata.append({
                            "text": subsec_text,
                            "metadata": subsec_metadata
                        })
                    else:
                        # Final fallback: Create overlapping chunks with original method
                        start = 0
                        while start < len(subsec_text):
                            end = start + chunk_size
                            # If we're not at the end, try to find a good break point
                            if end < len(subsec_text):
                                # Try to find the end of a sentence
                                for i in range(min(100, chunk_overlap)):
                                    if end - i > 0 and subsec_text[end - i] in ['.', '!', '?', '\n']:
                                        end = end - i + 1
                                        break
                            
                            chunk = subsec_text[start:end]
                            
                            # Create metadata for this chunk
                            chunk_metadata = subsec_metadata.copy()
                            chunk_metadata.update({
                                "chunk_type": "character_chunk",
                                "chunk_start": start,
                                "chunk_end": end,
                                "length": len(chunk)
                            })
                            
                            chunks_with_metadata.append({
                                "text": chunk,
                                "metadata": chunk_metadata
                            })
                            
                            # Move start pointer
                            start = end - chunk_overlap
                            
                            # Break if we've reached the end
                            if start >= len(subsec_text):
                                break
        
        # Extract just the text for backwards compatibility
        final_chunks = [item["text"] for item in chunks_with_metadata]
        
        return final_chunks
    
    def create_dataset(
        self, 
        documents_dir: str, 
        dataset_name: str,
        file_filter: str = "*.pdf",
        metadata_extractor=None
    ) -> Tuple[int, int]:
        """Process multiple documents and create a Chroma collection.
        
        Args:
            documents_dir: Directory containing documents
            dataset_name: Name for the Chroma collection
            file_filter: Filter for files to process
            metadata_extractor: Optional function to extract metadata from filenames
            
        Returns:
            Tuple of (number of documents processed, number of chunks created)
        """
        import glob
        
        # Create or get collection
        collection = self.chroma_client.get_or_create_collection(name=dataset_name)
        
        # Get list of PDF files
        file_paths = glob.glob(os.path.join(documents_dir, file_filter))
        
        doc_count = 0
        chunk_count = 0
        
        # Process each document
        for file_path in tqdm(file_paths, desc="Processing documents"):
            try:
                # Extract base filename
                filename = os.path.basename(file_path)
                
                # Process document
                chunks = self.process_document(file_path)
                
                if not chunks:
                    continue
                
                # Prepare for Chroma
                documents = []
                metadatas = []
                ids = []
                
                # Extract metadata if provided
                base_metadata = {}
                if metadata_extractor:
                    base_metadata = metadata_extractor(filename)
                
                # Extract and store legal metadata for improved retrieval
                # For each chunk, extract structured information to add to metadata
                import re
                
                # Patterns for legal metadata extraction
                legal_patterns = {
                    "article_refs": re.compile(r"(Article|Section|Regulation|ARTICLE|SECTION|§)\s+(\d+[\.\d]*\w*)", re.IGNORECASE),
                    "date_patterns": re.compile(r"(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2})[,\s]+(\d{4})", re.IGNORECASE),
                    "citation_patterns": re.compile(r"\(\s*([12]\d{3})\s*\)\s*(\d+)\s*([A-Za-z]+)\s*(\d+)", re.IGNORECASE),  # e.g. (2019) 123 ABC 456
                    "legal_entity": re.compile(r"(plaintiff|defendant|respondent|appellant|court|judge|justice|council|committee|commission|parliament|legislature|government)", re.IGNORECASE),
                    "monetary_values": re.compile(r"(\$|€|£|USD|EUR|GBP|dollar|euro|pound)\s*(\d+(?:,\d+)*(?:\.\d+)?)", re.IGNORECASE),
                    "percentage_values": re.compile(r"(\d+(?:\.\d+)?)\s*(%|percent)", re.IGNORECASE)
                }
                
                # Prepare chunks with enhanced metadata
                for i, chunk in enumerate(chunks):
                    if len(chunk) < 100:  # Skip very short chunks
                        continue
                    
                    chunk_id = f"{filename}_{i}_{uuid.uuid4()}"
                    chunk_metadata = {
                        "source": filename,
                        "chunk_index": i,
                        **base_metadata
                    }
                    
                    # Extract legal metadata from chunk
                    legal_metadata = {}
                    
                    # Extract article/section references
                    article_refs = legal_patterns["article_refs"].findall(chunk)
                    if article_refs:
                        legal_metadata["article_refs"] = [f"{ref[0]} {ref[1]}" for ref in article_refs]
                    
                    # Extract dates
                    dates = legal_patterns["date_patterns"].findall(chunk)
                    if dates:
                        legal_metadata["dates"] = [f"{date[0]}, {date[1]}" for date in dates]
                    
                    # Extract legal citations
                    citations = legal_patterns["citation_patterns"].findall(chunk)
                    if citations:
                        legal_metadata["citations"] = [f"({cit[0]}) {cit[1]} {cit[2]} {cit[3]}" for cit in citations]
                    
                    # Extract legal entities
                    entities = legal_patterns["legal_entity"].findall(chunk)
                    if entities:
                        legal_metadata["legal_entities"] = list(set(entities))
                    
                    # Extract monetary values
                    monetary = legal_patterns["monetary_values"].findall(chunk)
                    if monetary:
                        legal_metadata["monetary_values"] = [f"{m[0]}{m[1]}" for m in monetary]
                    
                    # Extract percentage values
                    percentages = legal_patterns["percentage_values"].findall(chunk)
                    if percentages:
                        legal_metadata["percentages"] = [f"{p[0]}%" for p in percentages]
                    
                    # Add a summary field for context
                    if legal_metadata:
                        # Create a summary of the legal metadata for easier filtering
                        summary_parts = []
                        
                        if "article_refs" in legal_metadata:
                            summary_parts.append(f"Articles: {', '.join(legal_metadata['article_refs'][:3])}")
                            
                        if "legal_entities" in legal_metadata:
                            summary_parts.append(f"Entities: {', '.join(legal_metadata['legal_entities'][:3])}")
                            
                        if "dates" in legal_metadata:
                            summary_parts.append(f"Dates: {', '.join(legal_metadata['dates'][:2])}")
                        
                        legal_metadata["summary"] = " | ".join(summary_parts)
                    
                    # Add legal metadata to chunk metadata if any was extracted
                    if legal_metadata:
                        chunk_metadata["legal_metadata"] = legal_metadata
                    
                    documents.append(chunk)
                    metadatas.append(chunk_metadata)
                    ids.append(chunk_id)
                
                # Add to Chroma in batches
                batch_size = 100
                for i in range(0, len(documents), batch_size):
                    end_idx = min(i + batch_size, len(documents))
                    
                    batch_docs = documents[i:end_idx]
                    batch_meta = metadatas[i:end_idx]
                    batch_ids = ids[i:end_idx]
                    
                    # Generate embeddings using the embeddings model
                    # In production, replace this with proper embedding generation
                    collection.add(
                        documents=batch_docs,
                        metadatas=batch_meta,
                        ids=batch_ids
                    )
                
                doc_count += 1
                chunk_count += len(documents)
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
        
        return doc_count, chunk_count
    
    def query_dataset(
        self, 
        dataset_name: str, 
        query: str, 
        n_results: int = 5,
        use_hybrid_search: bool = True,
        use_reranking: bool = True
    ) -> Dict[str, Any]:
        """Query a dataset with a natural language query.
        
        Args:
            dataset_name: Name of the Chroma collection
            query: Natural language query
            n_results: Number of results to return
            use_hybrid_search: Whether to use hybrid search (vector + BM25)
            use_reranking: Whether to rerank results for better relevance
            
        Returns:
            Dictionary with query results
        """
        # Import numpy for array operations
        import numpy as np
        
        collection = self.chroma_client.get_collection(name=dataset_name)
        
        # 1. Hybrid Search: Combine vector search with keyword search
        if use_hybrid_search:
            # Vector search component
            vector_results = collection.query(
                query_texts=[query],
                n_results=min(n_results * 2, 20)  # Get more results for hybrid reranking
            )
            
            # Keyword search component (using where filter with $contains operator)
            # Split query into keywords
            keywords = [kw.strip() for kw in query.lower().split() if len(kw.strip()) > 3]
            
            # Get unique document IDs from vector search
            vector_doc_ids = vector_results["ids"][0]
            all_results = {
                "ids": [vector_doc_ids],
                "documents": [vector_results["documents"][0]],
                "metadatas": [vector_results["metadatas"][0]],
                "distances": [vector_results["distances"][0]] if "distances" in vector_results else None
            }
            
            # If we have keywords, enhance with keyword search
            if keywords:
                # For each significant keyword, find matching documents
                for keyword in keywords[:3]:  # Limit to top 3 keywords
                    try:
                        # Use metadata $contains filter as keyword search
                        keyword_results = collection.query(
                            query_texts=[query],
                            where_document={"$contains": keyword},
                            n_results=min(n_results, 10)
                        )
                        
                        # Merge results if we found any
                        if keyword_results["ids"][0]:
                            for i, doc_id in enumerate(keyword_results["ids"][0]):
                                # Skip if already in results
                                if doc_id in vector_doc_ids:
                                    continue
                                
                                # Add new items to result lists
                                all_results["ids"][0].append(doc_id)
                                all_results["documents"][0].append(keyword_results["documents"][0][i])
                                all_results["metadatas"][0].append(keyword_results["metadatas"][0][i])
                                if all_results["distances"] is not None:
                                    # Assign a distance value slightly worse than the worst vector distance
                                    max_dist = max(all_results["distances"][0]) if all_results["distances"][0] else 1.0
                                    all_results["distances"][0].append(max_dist * 1.1)
                    except Exception as e:
                        print(f"Error in keyword search for '{keyword}': {str(e)}")
            
            results = all_results
            
            # 2. Reranking: Use cross-encoder to rerank combined results
            if use_reranking and len(results["documents"][0]) > 0:
                try:
                    from sentence_transformers import CrossEncoder
                    
                    # Check if we have more documents than requested results
                    if len(results["documents"][0]) > n_results:
                        # Load cross-encoder model for reranking
                        reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', device=self.device)
                        
                        # Prepare document-query pairs for reranking
                        pairs = [(query, doc) for doc in results["documents"][0]]
                        
                        # Get relevance scores
                        rerank_scores = reranker.predict(pairs)
                        
                        # Create index based on scores
                        rerank_indexes = np.argsort(-np.array(rerank_scores))  # Sort in descending order
                        
                        # Reorder all result components based on reranking
                        results["documents"][0] = [results["documents"][0][i] for i in rerank_indexes[:n_results]]
                        results["ids"][0] = [results["ids"][0][i] for i in rerank_indexes[:n_results]]
                        results["metadatas"][0] = [results["metadatas"][0][i] for i in rerank_indexes[:n_results]]
                        if results["distances"] is not None:
                            results["distances"][0] = [results["distances"][0][i] for i in rerank_indexes[:n_results]]
                except Exception as e:
                    print(f"Error in reranking: {str(e)}")
        else:
            # Standard vector search if hybrid search is disabled
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
        return results