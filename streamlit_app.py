import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import sys
import os
import io
import base64

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from database.supabase_client import supabase_manager
from text_processor import text_processor

# Page configuration
st.set_page_config(
    page_title="Document Management System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
    }
    .upload-area {
        border: 2px dashed #1f77b4;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

def parse_timestamp(timestamp_str):
    """Parse timestamp from additional field format"""
    try:
        if timestamp_str and timestamp_str.startswith('timestamp:'):
            timestamp = int(timestamp_str.replace('timestamp:', ''))
            return pd.to_datetime(timestamp, unit='s')
        else:
            return pd.to_datetime('now')
    except:
        return pd.to_datetime('now')

def main():
    # Header
    st.markdown('<h1 class="main-header">📄 Document Management System</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Dashboard", "Upload Documents", "Document Management", "API Status"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Upload Documents":
        show_upload_documents()
    elif page == "Document Management":
        show_document_management()
    elif page == "API Status":
        show_api_status()

def show_dashboard():
    """Dashboard page with overview metrics"""
    st.header("📊 Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    try:
        # Get documents for metrics
        documents = supabase_manager.get_chat_history(limit=1000)  # Reusing function but for documents
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>Total Documents</h3>
                <h2>{}</h2>
            </div>
            """.format(len(documents)), unsafe_allow_html=True)
        
        with col2:
            unique_sources = len(set([doc.get('user_id') for doc in documents if doc.get('user_id')]))
            st.markdown("""
            <div class="metric-card">
                <h3>Document Sources</h3>
                <h2>{}</h2>
            </div>
            """.format(unique_sources), unsafe_allow_html=True)
        
        with col3:
            # Test API connection
            try:
                response = requests.get("http://localhost:5000/health", timeout=5)
                api_status = "🟢 Online" if response.status_code == 200 else "🔴 Offline"
            except:
                api_status = "🔴 Offline"
            
            st.markdown("""
            <div class="metric-card">
                <h3>API Status</h3>
                <h2>{}</h2>
            </div>
            """.format(api_status), unsafe_allow_html=True)
        
        # Recent documents
        st.subheader("Recent Documents")
        if documents:
            df = pd.DataFrame(documents)
            df['created_at'] = df['created_at'].apply(parse_timestamp)
            df = df.sort_values('created_at', ascending=False).head(10)
            
            # Create a clean dataframe for display
            display_df = df.copy()
            display_df['Chunk Preview'] = display_df['chunk'].apply(lambda x: x[:100] + "..." if len(x) > 100 else x)
            display_df['Original Data Preview'] = display_df['original_data'].apply(lambda x: x[:100] + "..." if len(x) > 100 else x)
            display_df['Vector Status'] = display_df['vector'].apply(lambda x: '✅ Encoded' if x else '❌ Not encoded')
            display_df['Link'] = display_df['link'].apply(lambda x: x if x else 'No link')
            
            # Display as table
            st.dataframe(
                display_df[['chunk', 'Original Data Preview', 'Link', 'Vector Status']],
                use_container_width=True,
                column_config={
                    "chunk": "Chunk",
                    "Original Data Preview": "Original Data",
                    "Link": "Link",
                    "Vector Status": "Status"
                },
                hide_index=True
            )
        else:
            st.info("No documents found.")
            
    except Exception as e:
        st.error(f"Error loading dashboard data: {str(e)}")

def show_upload_documents():
    """Upload documents page"""
    st.header("📤 Upload Documents")
    
    # Upload section
    st.subheader("Upload New Document")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a file to upload",
        type=['csv', 'xlsx', 'xls'],
        help="Supported formats: CSV, Excel (XLSX, XLS) with columns: STT, DATA, Link"
    )
    
    if uploaded_file is not None:
        # Display file info
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**File name:** {uploaded_file.name}")
            st.write(f"**File size:** {uploaded_file.size} bytes")
            st.write(f"**File type:** {uploaded_file.type}")
        
        with col2:
            # Preview content
            try:
                # Read file based on type
                if uploaded_file.type == "text/csv":
                    df_preview = pd.read_csv(uploaded_file)
                elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"]:
                    df_preview = pd.read_excel(uploaded_file)
                else:
                    st.error("Unsupported file format")
                    return
                
                # Check required columns
                required_columns = ['STT', 'DATA', 'Link']
                missing_columns = [col for col in required_columns if col not in df_preview.columns]
                
                if missing_columns:
                    st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
                    st.info(f"Required columns: {', '.join(required_columns)}")
                    st.write("Current columns:", list(df_preview.columns))
                    return
                else:
                    st.success("✅ File format is correct!")
                
                # Show preview
                st.write("**File Preview:**")
                st.dataframe(df_preview.head(5), use_container_width=True)
                
                # Reset file pointer
                uploaded_file.seek(0)
            except Exception as e:
                st.error(f"Error reading file: {e}")
        
        # Processing options
        st.subheader("Processing Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            source_name = st.text_input("Document Source", value=uploaded_file.name)
            similarity_threshold = st.slider("Similarity Threshold", min_value=0.1, max_value=0.9, value=0.5, step=0.1, 
                                           help="Threshold for merging similar sentences")
        
        with col2:
            include_links = st.checkbox("Include Links in Processing", value=True)
            max_rows = st.number_input("Max Rows to Process", min_value=1, value=100, help="Set to 0 for all rows")
        
        # Upload button
        if st.button("🚀 Process and Upload Data", type="primary"):
            with st.spinner("Processing data..."):
                try:
                    # Load embedding model
                    with st.spinner("Loading embedding model..."):
                        if not text_processor.load_embedding_model("VIETNAMESE"):
                            st.error("❌ Failed to load embedding model")
                            return
                    
                    # Read file again
                    if uploaded_file.type == "text/csv":
                        df = pd.read_csv(uploaded_file)
                    elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"]:
                        df = pd.read_excel(uploaded_file)
                    
                    # Limit rows if specified
                    if max_rows > 0:
                        df = df.head(max_rows)
                    
                    # Process dataframe with text processor
                    with st.spinner("Processing text and creating embeddings..."):
                        processed_df = text_processor.process_dataframe(df, similarity_threshold)
                    
                    if processed_df.empty:
                        st.error("❌ Failed to process data")
                        return
                    
                    # Show processing results
                    st.success(f"✅ Processed {len(df)} rows into {len(processed_df)} chunks")
                    
                    # Display sample results
                    with st.expander("📊 Processing Results Preview"):
                        st.dataframe(processed_df.head(10), use_container_width=True)
                    
                                            # Upload to database
                        with st.spinner("Uploading to database..."):
                            uploaded_count = 0
                            for index, row in processed_df.iterrows():
                                # Store in database
                                result = supabase_manager.insert_chat_data(
                                    prompt=row['CHUNK'],  # Store chunk
                                    response=str(row['VECTOR']) if row['VECTOR'] else "",  # Store vector
                                    original_data=row['DATA'],  # Store original DATA
                                    link=row['Link']  # Store link in additional
                                )
                                if result.data:
                                    uploaded_count += 1
                    
                    st.success(f"✅ Successfully uploaded {uploaded_count} chunks to database")
                    
                except Exception as e:
                    st.error(f"❌ Error processing data: {str(e)}")
                    st.exception(e)

def split_text_into_chunks(text, chunk_size, overlap):
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    
    return chunks

def show_document_management():
    """Document management page"""
    st.header("📁 Document Management")
    
    # Supabase connection test
    st.subheader("Database Connection")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Test Database Connection"):
            try:
                is_connected = supabase_manager.test_connection()
                if is_connected:
                    st.success("✅ Successfully connected to database!")
                else:
                    st.error("❌ Failed to connect to database")
            except Exception as e:
                st.error(f"❌ Connection error: {str(e)}")
    
    with col2:
        if st.button("Refresh Data"):
            st.rerun()
    
    # Document display
    st.subheader("Document Chunks")
    
    try:
        # Get all documents
        documents = supabase_manager.get_chat_history(limit=1000)
        
        if documents:
            df = pd.DataFrame(documents)
            df['created_at'] = df['created_at'].apply(parse_timestamp)
            
            # Filters
            st.subheader("Filters")
            col1, col2 = st.columns(2)
            
            with col1:
                source_filter = st.selectbox(
                    "Filter by Source",
                    ["All"] + list(df['user_id'].dropna().unique())
                )
            
            with col2:
                date_filter = st.date_input(
                    "Filter by Date",
                    value=datetime.now().date()
                )
            
            # Apply filters
            filtered_df = df.copy()
            
            if source_filter != "All":
                filtered_df = filtered_df[filtered_df['user_id'] == source_filter]
            
            filtered_df = filtered_df[
                filtered_df['created_at'].dt.date == date_filter
            ]
            
            # Display data
            st.dataframe(
                filtered_df[['chunk', 'original_data', 'vector', 'link']],
                use_container_width=True,
                column_config={
                    "chunk": "Chunk",
                    "original_data": "Original Data",
                    "vector": "Vector Status",
                    "link": "Link"
                }
            )
            
            # Export data
            st.subheader("Export Data")
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"document_chunks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
        else:
            st.info("No documents found in the database.")
            
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")

def show_api_status():
    """API status page"""
    st.header("🔌 API Status")
    
    # API endpoints
    st.subheader("Available Endpoints")
    
    endpoints = [
        {
            "endpoint": "/health",
            "method": "GET",
            "description": "Health check endpoint"
        },
        {
            "endpoint": "/api/chat",
            "method": "POST",
            "description": "Document processing endpoint"
        },
        {
            "endpoint": "/api/chat/history",
            "method": "GET",
            "description": "Get document chunks"
        },
        {
            "endpoint": "/api/test-connection",
            "method": "GET",
            "description": "Test database connection"
        }
    ]
    
    for endpoint in endpoints:
        st.markdown(f"""
        **{endpoint['method']}** `{endpoint['endpoint']}`  
        {endpoint['description']}
        """)
    
    # Test API endpoints
    st.subheader("Test API Endpoints")
    
    api_base = st.text_input("API Base URL", value="http://localhost:5000")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Test Health Endpoint"):
            try:
                response = requests.get(f"{api_base}/health", timeout=5)
                if response.status_code == 200:
                    st.success("✅ Health endpoint is working!")
                    st.json(response.json())
                else:
                    st.error(f"❌ Health endpoint failed: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Connection error: {str(e)}")
    
    with col2:
        if st.button("Test Database Connection"):
            try:
                response = requests.get(f"{api_base}/api/test-connection", timeout=5)
                if response.status_code == 200:
                    st.success("✅ Database connection test successful!")
                    st.json(response.json())
                else:
                    st.error(f"❌ Database connection test failed: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Connection error: {str(e)}")

if __name__ == "__main__":
    main() 