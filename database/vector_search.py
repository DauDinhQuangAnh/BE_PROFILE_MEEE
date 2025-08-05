#!/usr/bin/env python3
"""
Optimized Vector Search Module
Implements caching, indexing, and efficient similarity search
"""

import numpy as np
import ast
import logging
from typing import List, Dict, Tuple
from functools import lru_cache
import time
from collections import defaultdict

logger = logging.getLogger(__name__)

class VectorSearchOptimizer:
    """Optimized vector search with caching and indexing"""
    
    def __init__(self):
        self.vector_cache = {}  # Cache for parsed vectors
        self.similarity_cache = {}  # Cache for similarity calculations
        self.documents_cache = None
        self.last_cache_update = 0
        self.cache_ttl = 300  # 5 minutes cache TTL
        
    def parse_vector(self, vector_str: str) -> np.ndarray:
        """Parse vector string to numpy array with caching"""
        if vector_str in self.vector_cache:
            return self.vector_cache[vector_str]
        
        try:
            if isinstance(vector_str, str):
                vector_list = ast.literal_eval(vector_str)
                vector_array = np.array(vector_list, dtype=np.float32)
            else:
                vector_array = np.array(vector_str, dtype=np.float32)
            
            self.vector_cache[vector_str] = vector_array
            return vector_array
        except Exception as e:
            logger.error(f"Error parsing vector: {e}")
            return np.array([])
    
    def calculate_cosine_similarity_optimized(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Optimized cosine similarity calculation"""
        try:
            # Use numpy's optimized dot product
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def batch_similarity_search(self, query_embedding: List[float], 
                              documents: List[Dict], 
                              match_threshold: float = 0.5,
                              match_count: int = 2) -> List[Dict]:
        """Batch similarity search with optimizations"""
        try:
            start_time = time.time()
            
            # Convert query to numpy array once
            query_array = np.array(query_embedding, dtype=np.float32)
            
            # Pre-filter documents with valid vectors
            valid_docs = []
            for doc in documents:
                vector_str = doc.get('vector', '')
                if vector_str and vector_str != 'processed':
                    valid_docs.append(doc)
            
            logger.info(f"Processing {len(valid_docs)} valid documents out of {len(documents)}")
            
            # Batch process similarities
            similarities = []
            for doc in valid_docs:
                try:
                    # Parse vector with caching
                    doc_vector = self.parse_vector(doc.get('vector', ''))
                    
                    if len(doc_vector) == 0:
                        continue
                    
                    # Calculate similarity
                    similarity = self.calculate_cosine_similarity_optimized(query_array, doc_vector)
                    
                    if similarity >= match_threshold:
                        similarities.append({
                            'id': doc.get('id'),
                            'chunk': doc.get('chunk', ''),
                            'original_data': doc.get('original_data', ''),
                            'link': doc.get('link', ''),
                            'similarity': similarity
                        })
                        
                except Exception as e:
                    logger.error(f"Error processing document {doc.get('id')}: {e}")
                    continue
            
            # Sort and return top matches
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            top_matches = similarities[:match_count]
            
            processing_time = time.time() - start_time
            logger.info(f"Vector search completed in {processing_time:.3f}s, found {len(top_matches)} matches")
            
            return top_matches
            
        except Exception as e:
            logger.error(f"Error in batch similarity search: {e}")
            return []
    
    def clear_cache(self):
        """Clear all caches"""
        self.vector_cache.clear()
        self.similarity_cache.clear()
        self.documents_cache = None
        logger.info("Vector search cache cleared")

# Global instance
vector_optimizer = VectorSearchOptimizer() 