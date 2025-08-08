from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import logging
import numpy as np
from sentence_transformers import SentenceTransformer
import ast

from config import Config
from database.supabase_client import supabase_manager
from database.vector_search import vector_optimizer
from gemini_client import gemini_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load configuration
app.config.from_object(Config)

# Global embedding model
embedding_model = None

def load_embedding_model():
    """Load the Vietnamese embedding model (online only)"""
    global embedding_model
    try:
        embedding_model = SentenceTransformer('keepitreal/vietnamese-sbert')
        logger.info("✅ Online Vietnamese embedding model loaded successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to load embedding model: {e}")
        return False

def calculate_cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors"""
    try:
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)
    except Exception as e:
        logger.error(f"Error calculating similarity: {e}")
        return 0.0

def find_nearest_matches(query_embedding, match_threshold=0.5, match_count=2):
    """Find nearest matches in database using optimized vector search"""
    try:
        # Get all documents from database
        documents = supabase_manager.get_chat_history(limit=1000)
        
        if not documents:
            return []
        
        # Use optimized vector search
        matches = vector_optimizer.batch_similarity_search(
            query_embedding=query_embedding,
            documents=documents,
            match_threshold=match_threshold,
            match_count=match_count
        )
        
        return matches
        
    except Exception as e:
        logger.error(f"Error finding nearest matches: {e}")
        return []

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Chatbot API is running'
    }), 200

@app.route('/api/chat', methods=['POST'])
def process_document():
    """Document processing endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                'error': 'Missing document content in request body'
            }), 400
        
        document_content = data['prompt']
        source_name = data.get('user_id', 'unknown_source')
        
        # Process document (for now, just store as chunks)
        # In the future, this could include vector encoding
        response = "processed"  # Placeholder for vector encoding
        
        # Store the document chunk in Supabase
        try:
            supabase_manager.insert_chat_data(
                prompt=document_content,
                response=response,
                original_data=document_content,  # Store original data
                link=None  # No link for API calls
            )
            logger.info(f"Document chunk stored successfully for source: {source_name}")
        except Exception as e:
            logger.error(f"Failed to store document chunk: {e}")
            # Continue even if storage fails
        
        return jsonify({
            'content': document_content,
            'status': response,
            'source': source_name,
            'timestamp': 'now'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in document processing endpoint: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@app.route('/api/chat/history', methods=['GET'])
def get_document_chunks():
    """Get document chunks from Supabase"""
    try:
        source_name = request.args.get('user_id', None)
        limit = int(request.args.get('limit', 50))
        
        chunks = supabase_manager.get_chat_history(limit, source_name)
        
        return jsonify({
            'chunks': chunks,
            'count': len(chunks)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting document chunks: {e}")
        return jsonify({
            'error': 'Failed to retrieve document chunks'
        }), 500

@app.route('/api/query', methods=['POST'])
def process_query():
    """Process user query and find relevant documents"""
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({
                'error': 'Missing question in request body'
            }), 400
        
        question = data['question']
        match_threshold = data.get('match_threshold', 0.5)
        match_count = data.get('match_count', 2)
        
        # Load embedding model if not loaded
        if embedding_model is None:
            if not load_embedding_model():
                return jsonify({
                    'error': 'Failed to load embedding model'
                }), 500
        
        # Encode the question
        try:
            question_embedding = embedding_model.encode(question).tolist()
            logger.info(f"Question encoded successfully: {len(question_embedding)} dimensions")
        except Exception as e:
            logger.error(f"Failed to encode question: {e}")
            return jsonify({
                'error': 'Failed to encode question'
            }), 500
        
        # Find nearest matches
        matches = find_nearest_matches(question_embedding, match_threshold, match_count)
        
        # Prepare response
        response_data = {
            'question': question,
            'question_embedding_dimensions': len(question_embedding),
            'match_threshold': match_threshold,
            'match_count': match_count,
            'found_matches': len(matches),
            'matches': matches
        }
        
        if matches:
            # Get unique original_data to avoid duplicates
            unique_original_data = []
            seen_original_data = set()
            
            for match in matches:
                original_data = match.get('original_data', '')
                if original_data and original_data not in seen_original_data:
                    unique_original_data.append(original_data)
                    seen_original_data.add(original_data)
            
            # Create documents text with unique original_data
            if unique_original_data:
                documents_text = '\n\n'.join([
                    f"Tài liệu {i+1}: {original_data}"
                    for i, original_data in enumerate(unique_original_data)
                ])
                
                # Create prompt in the requested format
                combined_content = f'Bạn sẽ thay mặt Đậu Đình Quang Anh để trả lời các câu hỏi của người dùng, sử dụng từ ngữ teencode 1 chút thêm cả icon. Câu hỏi của người dùng là "{question}" và các thông tin liên quan đến câu hỏi là:\n\n{documents_text}'
            else:
                combined_content = f'Bạn sẽ thay mặt Đậu Đình Quang Anh để trả lời các câu hỏi của người dùng, sử dụng từ ngữ teencode 1 chút thêm cả icon. Câu hỏi của người dùng là "{question}" và không có thông tin liên quan nào được tìm thấy.'
            
            response_data['combined_content'] = combined_content
            response_data['status'] = 'success'
            response_data['unique_original_data_count'] = len(unique_original_data)
            
            # Generate AI response using Gemini
            if gemini_client.is_available():
                logger.info("🤖 Generating AI response with Gemini...")
                ai_response = gemini_client.generate_response(combined_content)
                
                if ai_response['success']:
                    response_data['ai_response'] = ai_response['response']
                    response_data['ai_status'] = 'success'
                    logger.info("✅ AI response generated successfully")
                else:
                    response_data['ai_response'] = None
                    response_data['ai_status'] = 'failed'
                    response_data['ai_error'] = ai_response['error']
                    logger.warning(f"⚠️ AI response generation failed: {ai_response['error']}")
            else:
                response_data['ai_response'] = None
                response_data['ai_status'] = 'unavailable'
                logger.info("ℹ️ Gemini AI not available, skipping AI response")
        else:
            response_data['combined_content'] = f'Bạn sẽ thay mặt Đậu Đình Quang Anh để trả lời các câu hỏi của người dùng, sử dụng từ ngữ teencode 1 chút thêm cả icon, trả lời câu hỏi 1 cách thân thiện như đang đối thoại với người dùng vậy, nên nhớ chỉ trả lời các câu hỏi liên quan đến Quang Anh với mục đích giới thiệu Quang Anh(Đậu Đình Quang Anh). Câu hỏi của người dùng là "{question}" và không có thông tin liên quan nào được tìm thấy.'
            response_data['status'] = 'no_matches'
            
            # Generate AI response for no matches case
            if gemini_client.is_available():
                logger.info("🤖 Generating AI response for no matches case...")
                ai_response = gemini_client.generate_response(response_data['combined_content'])
                
                if ai_response['success']:
                    response_data['ai_response'] = ai_response['response']
                    response_data['ai_status'] = 'success'
                else:
                    response_data['ai_response'] = None
                    response_data['ai_status'] = 'failed'
                    response_data['ai_error'] = ai_response['error']
            else:
                response_data['ai_response'] = None
                response_data['ai_status'] = 'unavailable'
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error in query processing endpoint: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@app.route('/api/test-connection', methods=['GET'])
def test_supabase_connection():
    """Test Supabase connection"""
    try:
        is_connected = supabase_manager.test_connection()
        
        if is_connected:
            return jsonify({
                'status': 'connected',
                'message': 'Successfully connected to Supabase'
            }), 200
        else:
            return jsonify({
                'status': 'disconnected',
                'message': 'Failed to connect to Supabase'
            }), 500
            
    except Exception as e:
        logger.error(f"Error testing Supabase connection: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error testing connection: {str(e)}'
        }), 500

@app.route('/api/test-gemini', methods=['POST'])
def test_gemini():
    """Test Gemini AI functionality"""
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                'error': 'Missing prompt in request body'
            }), 400
        
        prompt = data['prompt']
        
        if not gemini_client.is_available():
            return jsonify({
                'error': 'Gemini AI not available. Please check your API key.',
                'ai_status': 'unavailable'
            }), 503
        
        # Generate response
        ai_response = gemini_client.generate_response(prompt)
        
        if ai_response['success']:
            return jsonify({
                'success': True,
                'prompt': prompt,
                'response': ai_response['response'],
                'ai_status': 'success'
            }), 200
        else:
            return jsonify({
                'success': False,
                'prompt': prompt,
                'error': ai_response['error'],
                'ai_status': 'failed'
            }), 500
            
    except Exception as e:
        logger.error(f"Error testing Gemini: {e}")
        return jsonify({
            'error': 'Internal server error',
            'ai_status': 'error'
        }), 500

if __name__ == '__main__':
    try:
        # Validate configuration
        Config.validate_config()
        logger.info("Configuration validated successfully")
        
        # Load embedding model
        if load_embedding_model():
            logger.info("Embedding model loaded successfully")
        else:
            logger.warning("Failed to load embedding model")
        
        # Test Supabase connection
        if supabase_manager.test_connection():
            logger.info("Supabase connection test successful")
        else:
            logger.warning("Supabase connection test failed")
        
        # Start the Flask app
        app.run(
            host=Config.API_HOST,
            port=Config.API_PORT,
            debug=Config.DEBUG
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1) 