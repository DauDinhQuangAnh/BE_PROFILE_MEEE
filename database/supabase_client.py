from supabase import create_client, Client
from config import Config
import logging
import time

logger = logging.getLogger(__name__)

class SupabaseManager:
    """Manager class for Supabase operations"""
    
    def __init__(self):
        """Initialize Supabase client"""
        try:
            Config.validate_config()
            self.client: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    
    def test_connection(self):
        """Test the connection to Supabase"""
        try:
            # Simple query to test connection - using existing table structure
            response = self.client.table('Vector_database').select('*').limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def insert_chat_data(self, prompt: str, response: str, original_data: str = None, link: str = None):
        """Insert chat data into Supabase using existing table structure"""
        try:
            # Create additional info with only link
            additional_info = ""
            if link:
                additional_info = f"link:{link}"
            
            data = {
                'chunks': prompt,  # Store CHUNK
                'Vector': response if response else "",  # Store vector
                'Doc': original_data or "",  # Store original DATA
                'additional': additional_info  # Store link
            }
            
            result = self.client.table('Vector_database').insert(data).execute()
            logger.info(f"Chat data inserted successfully: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to insert chat data: {e}")
            raise
    
    def get_chat_history(self, limit: int = 50, user_id: str = None):
        """Get chat history from Supabase using existing table structure"""
        try:
            query = self.client.table('Vector_database').select('*')
            
            if user_id:
                query = query.eq('Doc', user_id)
            
            result = query.order('id', desc=True).limit(limit).execute()
            
            # Transform data to match expected format
            transformed_data = []
            for item in result.data:
                additional = item.get('additional', '')
                
                # Parse additional field for link only
                link = ""
                if additional and additional.startswith('link: '):
                    link = additional.replace('link: ', '')
                
                transformed_data.append({
                    'id': item.get('id'),
                    'chunk': item.get('chunks'),  # CHUNK
                    'vector': item.get('Vector'),  # Vector
                    'original_data': item.get('Doc'),  # Original DATA
                    'link': link  # Link
                })
            
            return transformed_data
        except Exception as e:
            logger.error(f"Failed to get chat history: {e}")
            raise
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        # Note: Using existing table structure from user's Supabase database
        logger.info("Using existing 'Vector_database' table structure")
        logger.info("Table structure: id, chunks, Vector, Doc, additional")

# Global instance
supabase_manager = SupabaseManager() 