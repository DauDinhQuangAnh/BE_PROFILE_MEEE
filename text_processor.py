#!/usr/bin/env python3
"""
Text processing module for document chunking and embedding
"""

import nltk
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextProcessor:
    def __init__(self):
        """Initialize text processor"""
        # Download NLTK punkt tokenizer if not available
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        self.tfidf_vectorizer = TfidfVectorizer()
        self.embedding_model = None
        
    def load_embedding_model(self, language="VIETNAMESE"):
        """Load the Vietnamese embedding model"""
        try:
            # Get the absolute path to the embedding model
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(current_dir, "embedding_model")
            
            logger.info(f"🔍 Looking for embedding model at: {model_path}")
            
            if os.path.exists(model_path):
                self.embedding_model = SentenceTransformer(model_path)
                logger.info("✅ Vietnamese embedding model loaded successfully from local path")
                return True
            else:
                # Fallback to online model
                logger.warning(f"⚠️ Local model not found at {model_path}, using online model")
                self.embedding_model = SentenceTransformer('keepitreal/vietnamese-sbert')
                logger.info("✅ Online Vietnamese embedding model loaded successfully")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            return False
    
    def split_into_sentences(self, text):
        """Split text into sentences using NLTK"""
        try:
            sentences = nltk.sent_tokenize(text)
            return [s.strip() for s in sentences if s.strip()]
        except Exception as e:
            logger.error(f"Error splitting sentences: {e}")
            return [text]
    
    def calculate_similarity(self, sentence1, sentence2):
        """Calculate cosine similarity between two sentences"""
        try:
            if not sentence1 or not sentence2:
                return 0.0
            
            # Vectorize sentences
            vectors = self.tfidf_vectorizer.fit_transform([sentence1, sentence2])
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(vectors)
            return similarity_matrix[0, 1]
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def merge_similar_sentences(self, sentences, threshold=0.5):
        """Merge sentences based on similarity threshold"""
        if not sentences:
            return []
        
        merged_chunks = []
        current_chunk = sentences[0]
        
        for i in range(1, len(sentences)):
            current_sentence = sentences[i]
            
            # Calculate similarity between current chunk and next sentence
            similarity = self.calculate_similarity(current_chunk, current_sentence)
            
            if similarity >= threshold:
                # Merge sentences
                current_chunk = current_chunk + " " + current_sentence
            else:
                # Add current chunk to results and start new chunk
                merged_chunks.append(current_chunk)
                current_chunk = current_sentence
        
        # Add the last chunk
        merged_chunks.append(current_chunk)
        
        return merged_chunks
    
    def process_text_to_chunks(self, text, threshold=0.5):
        """Process text into meaningful chunks"""
        try:
            # Split into sentences
            sentences = self.split_into_sentences(text)
            
            if len(sentences) <= 1:
                return [text]
            
            # Merge similar sentences
            chunks = self.merge_similar_sentences(sentences, threshold)
            
            return chunks
        except Exception as e:
            logger.error(f"Error processing text to chunks: {e}")
            return [text]
    
    def create_embeddings(self, texts):
        """Create embeddings for a list of texts"""
        try:
            if not self.embedding_model:
                logger.error("Embedding model not loaded")
                return None
            
            embeddings = self.embedding_model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            return None
    
    def process_dataframe(self, df, threshold=0.5):
        """Process entire dataframe and create embeddings"""
        try:
            if not self.embedding_model:
                logger.error("Embedding model not loaded")
                return pd.DataFrame()
            
            processed_data = []
            
            for index, row in df.iterrows():
                stt = row['STT']
                data = row['DATA']
                link = row['Link']
                
                # Process text into chunks
                chunks = self.process_text_to_chunks(data, threshold)
                
                # Create embeddings for chunks
                embeddings = self.create_embeddings(chunks)
                
                if embeddings is None:
                    logger.warning(f"Failed to create embeddings for row {index}")
                    continue
                
                # Create records for each chunk
                for i, chunk in enumerate(chunks):
                    record = {
                        'STT': stt,
                        'DATA': data,  # Keep original data
                        'Link': link,
                        'CHUNK': chunk,
                        'CHUNK_INDEX': i + 1,
                        'VECTOR': embeddings[i] if embeddings else None
                    }
                    processed_data.append(record)
            
            return pd.DataFrame(processed_data)
            
        except Exception as e:
            logger.error(f"Error processing dataframe: {e}")
            return pd.DataFrame()

# Create global instance
text_processor = TextProcessor() 