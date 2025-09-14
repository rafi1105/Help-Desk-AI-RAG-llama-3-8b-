"""
Knowledge Base manager for handling JSON data and vector embeddings.
"""
import json
import os
import pickle
from typing import List, Dict, Any, Optional
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import pandas as pd

from ..core.config import config

class KnowledgeBase:
    """Manages knowledge base with JSON data and vector embeddings."""
    
    def __init__(self):
        self.embedding_model = SentenceTransformer(config.embedding_model)
        self.index = None
        self.documents = []
        self.metadata = []
        self.vector_db_path = config.vector_db_path
        
        # Create directories if they don't exist
        os.makedirs(self.vector_db_path, exist_ok=True)
        os.makedirs(config.knowledge_base_path, exist_ok=True)
        
        # Load existing knowledge base if available
        self.load_knowledge_base()
    
    def add_json_data(self, json_data: Dict[str, Any], category: str = "general") -> None:
        """Add JSON data to the knowledge base."""
        # Convert JSON to text representation
        text_content = self._json_to_text(json_data, category)
        
        # Create embedding
        embedding = self.embedding_model.encode([text_content])
        
        # Add to documents and metadata
        self.documents.append(text_content)
        self.metadata.append({
            "category": category,
            "source": "json_data",
            "original_data": json_data,
            "id": len(self.documents)
        })
        
        # Add to vector index
        self._add_to_index(embedding)
        
        print(f"Added JSON data to knowledge base. Category: {category}")
    
    def add_text_document(self, text: str, metadata: Dict[str, Any] = None) -> None:
        """Add text document to the knowledge base."""
        if metadata is None:
            metadata = {}
        
        # Create embedding
        embedding = self.embedding_model.encode([text])
        
        # Add to documents and metadata
        self.documents.append(text)
        metadata.update({
            "source": "text_document",
            "id": len(self.documents)
        })
        self.metadata.append(metadata)
        
        # Add to vector index
        self._add_to_index(embedding)
        
        print(f"Added text document to knowledge base.")
    
    def search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Search for relevant documents in the knowledge base."""
        if top_k is None:
            top_k = config.top_k
        
        if self.index is None or len(self.documents) == 0:
            return []
        
        # Create query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Search in vector index
        scores, indices = self.index.search(query_embedding, top_k)
        
        # Prepare results
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.documents):  # Valid index
                results.append({
                    "content": self.documents[idx],
                    "metadata": self.metadata[idx],
                    "score": float(score),
                    "rank": i + 1
                })
        
        return results
    
    def load_json_file(self, file_path: str, category: str = "file_data") -> None:
        """Load JSON data from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                for item in data:
                    self.add_json_data(item, category)
            else:
                self.add_json_data(data, category)
                
            print(f"Loaded JSON file: {file_path}")
        except Exception as e:
            print(f"Error loading JSON file {file_path}: {e}")
    
    def save_knowledge_base(self) -> None:
        """Save the knowledge base to disk."""
        try:
            # Save vector index
            if self.index is not None:
                faiss.write_index(self.index, os.path.join(self.vector_db_path, "index.faiss"))
            
            # Save documents and metadata
            with open(os.path.join(self.vector_db_path, "documents.pkl"), "wb") as f:
                pickle.dump(self.documents, f)
            
            with open(os.path.join(self.vector_db_path, "metadata.pkl"), "wb") as f:
                pickle.dump(self.metadata, f)
            
            print("Knowledge base saved successfully.")
        except Exception as e:
            print(f"Error saving knowledge base: {e}")
    
    def load_knowledge_base(self) -> None:
        """Load existing knowledge base from disk."""
        try:
            index_path = os.path.join(self.vector_db_path, "index.faiss")
            docs_path = os.path.join(self.vector_db_path, "documents.pkl")
            meta_path = os.path.join(self.vector_db_path, "metadata.pkl")
            
            if all(os.path.exists(path) for path in [index_path, docs_path, meta_path]):
                # Load vector index
                self.index = faiss.read_index(index_path)
                
                # Load documents and metadata
                with open(docs_path, "rb") as f:
                    self.documents = pickle.load(f)
                
                with open(meta_path, "rb") as f:
                    self.metadata = pickle.load(f)
                
                print("Knowledge base loaded successfully.")
            else:
                print("No existing knowledge base found. Starting fresh.")
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
    
    def _json_to_text(self, json_data: Dict[str, Any], category: str) -> str:
        """Convert JSON data to text representation."""
        def flatten_json(obj, prefix=""):
            """Recursively flatten JSON object."""
            items = []
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_key = f"{prefix}.{key}" if prefix else key
                    if isinstance(value, (dict, list)):
                        items.extend(flatten_json(value, new_key))
                    else:
                        items.append(f"{new_key}: {value}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_key = f"{prefix}[{i}]" if prefix else f"item_{i}"
                    if isinstance(item, (dict, list)):
                        items.extend(flatten_json(item, new_key))
                    else:
                        items.append(f"{new_key}: {item}")
            return items
        
        flattened = flatten_json(json_data)
        text_content = f"Category: {category}\n" + "\n".join(flattened)
        return text_content
    
    def _add_to_index(self, embedding: np.ndarray) -> None:
        """Add embedding to the vector index."""
        if self.index is None:
            # Initialize index with first embedding
            dimension = embedding.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for similarity
        
        # Normalize embedding for cosine similarity
        faiss.normalize_L2(embedding)
        self.index.add(embedding)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        categories = {}
        sources = {}
        
        for meta in self.metadata:
            cat = meta.get("category", "unknown")
            src = meta.get("source", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
            sources[src] = sources.get(src, 0) + 1
        
        return {
            "total_documents": len(self.documents),
            "categories": categories,
            "sources": sources,
            "index_size": self.index.ntotal if self.index else 0
        }