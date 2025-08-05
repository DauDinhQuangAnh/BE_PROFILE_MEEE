#!/usr/bin/env python3
"""
Gemini AI Client Module
Handles communication with Google's Gemini AI for generating responses
"""

import google.generativeai as genai
import logging
import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiClient:
    """Client for interacting with Google Gemini AI"""
    
    def __init__(self):
        """Initialize Gemini client"""
        self.api_key = Config.GEMINI_API_KEY
        self.model = None
        self.is_initialized = False
        self.executor = ThreadPoolExecutor(max_workers=3)  # Limit concurrent requests
        self.timeout = 30  # 10 seconds timeout
        
        if self.api_key:
            self._initialize_gemini()
        else:
            logger.warning("Gemini API key not found. AI responses will be disabled.")
    
    def _initialize_gemini(self):
        """Initialize Gemini AI with API key"""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            self.is_initialized = True
            logger.info("✅ Gemini AI initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini AI: {e}")
            self.is_initialized = False
    
    def generate_response(self, prompt: str) -> dict:
        """
        Generate AI response using Gemini with timeout
        
        Args:
            prompt (str): The prompt to send to Gemini
            
        Returns:
            dict: Response containing success status and generated text
        """
        if not self.is_initialized:
            return {
                'success': False,
                'error': 'Gemini AI not initialized. Please check your API key.',
                'response': None
            }
        
        try:
            logger.info(f"🤖 Sending prompt to Gemini: {prompt[:100]}...")
            start_time = time.time()
            
            # Submit to thread pool with timeout
            future = self.executor.submit(self._generate_response_sync, prompt)
            
            try:
                response = future.result(timeout=self.timeout)
                processing_time = time.time() - start_time
                logger.info(f"✅ Gemini response generated in {processing_time:.2f}s")
                return response
            except TimeoutError:
                logger.warning(f"⚠️ Gemini request timed out after {self.timeout}s")
                return {
                    'success': False,
                    'error': f'Request timed out after {self.timeout} seconds',
                    'response': None
                }
                
        except Exception as e:
            logger.error(f"❌ Error generating Gemini response: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': None
            }
    
    def _generate_response_sync(self, prompt: str) -> dict:
        """Synchronous Gemini response generation"""
        try:
            # Generate response
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return {
                    'success': True,
                    'response': response.text,
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'error': 'Empty response from Gemini',
                    'response': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': None
            }
    
    def generate_response_async(self, prompt: str) -> dict:
        """
        Asynchronous AI response generation (non-blocking)
        
        Args:
            prompt (str): The prompt to send to Gemini
            
        Returns:
            dict: Response with async status
        """
        if not self.is_initialized:
            return {
                'success': False,
                'error': 'Gemini AI not initialized',
                'response': None,
                'async': False
            }
        
        try:
            # Start async generation
            future = self.executor.submit(self._generate_response_sync, prompt)
            
            return {
                'success': True,
                'future': future,
                'async': True,
                'message': 'AI response generation started'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': None,
                'async': False
            }
    
    def get_async_result(self, future, timeout: float = None) -> dict:
        """Get result from async generation"""
        try:
            if timeout:
                result = future.result(timeout=timeout)
            else:
                result = future.result()
            
            return {
                'success': True,
                'response': result.get('response'),
                'error': result.get('error'),
                'async': False
            }
            
        except TimeoutError:
            return {
                'success': False,
                'error': 'Async request timed out',
                'response': None,
                'async': False
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': None,
                'async': False
            }
    
    def is_available(self) -> bool:
        """Check if Gemini AI is available"""
        return self.is_initialized and self.api_key is not None
    
    def set_timeout(self, timeout: float):
        """Set timeout for requests"""
        self.timeout = timeout
        logger.info(f"Timeout set to {timeout}s")
    
    def shutdown(self):
        """Shutdown the executor"""
        self.executor.shutdown(wait=True)
        logger.info("Gemini client executor shutdown")

# Global instance
gemini_client = GeminiClient() 