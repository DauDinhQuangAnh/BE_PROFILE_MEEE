# 📄 Document Management System

Hệ thống quản lý tài liệu với kết nối Supabase và API Flask để upload, xử lý và lưu trữ tài liệu. (Đã loại bỏ giao diện Streamlit)

## 🚀 Tính năng

- **Flask API**: Backend API để xử lý và lưu trữ tài liệu
- **Supabase Integration**: Lưu trữ chunks tài liệu và vectors trong Supabase
- **Vietnamese Embedding**: Sử dụng SentenceTransformer cho tiếng Việt

## 📋 Yêu cầu hệ thống

- Python 3.8+
- Supabase account
- pip (Python package manager)

## 🛠️ Cài đặt

### 1. Clone repository
```bash
git clone <repository-url>
cd chatbot-management-system
```

### 2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 3. Cấu hình Supabase

1. Tạo project trên [Supabase](https://supabase.com)
2. Sử dụng bảng `Vector_database` hiện có với cấu trúc:

```sql
-- Bảng Vector_database đã tồn tại với cấu trúc:
-- id (int8, primary key)
-- chunks (varchar) - lưu nội dung chunk tài liệu
-- Vector (varchar) - lưu vector encoding (sẽ được cập nhật sau)
-- Doc (varchar) - lưu tên nguồn tài liệu
-- additional (varchar) - lưu link (format: "link:https://...")
```

3. Copy URL và API Key từ Supabase dashboard

### 4. Cấu hình biến môi trường

Tạo file `.env` từ `env_example.txt`:

```bash
cp env_example.txt .env
```

Cập nhật file `.env` với thông tin Supabase:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=development

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000

# Gemini
GEMINI_API_KEY=your_gemini_api_key_here
```

## 🚀 Chạy ứng dụng

### Khởi động Flask API
```bash
python app.py
```

API sẽ chạy tại: `http://localhost:5000`

## 📚 API Endpoints

### Health Check
```
GET /health
```
Kiểm tra trạng thái API

### Document Processing Endpoint
```
POST /api/chat
```
**Body:**
```json
{
    "prompt": "Document content chunk",
    "user_id": "document_source_name"
}
```

**Response:**
```json
{
    "content": "Document content chunk",
    "status": "processed",
    "source": "document_source_name",
    "timestamp": "now"
}
```

### Document Chunks
```
GET /api/chat/history?user_id=optional&limit=50
```
Lấy chunks tài liệu

### Query (semantic search + Gemini)
```
POST /api/query
```
**Body:**
```json
{
  "question": "nội dung câu hỏi",
  "match_threshold": 0.5,
  "match_count": 2
}
```

### Test Connection
```
GET /api/test-connection
```
Kiểm tra kết nối Supabase

### Test Gemini
```
POST /api/test-gemini
```
Body: `{ "prompt": "..." }`

## 🔧 Cấu trúc dự án

```
chatbot-management-system/
├── app.py                     # Flask API (entrypoint)
├── database/
│   ├── __init__.py
│   ├── supabase_client.py     # Supabase connection (Vector_database table)
│   └── vector_search.py       # Tối ưu vector search
├── gemini_client.py           # Google Gemini client
├── config.py                  # Configuration
├── requirements.txt           # Dependencies
├── env_example.txt            # Environment template
└── README.md                  # Documentation
```

## 🔒 Bảo mật
- Sử dụng biến môi trường cho thông tin nhạy cảm
- Validate input data
- Error handling cho tất cả API endpoints
- CORS enabled cho development

## 🐛 Troubleshooting
### Lỗi Flask API
1. Kiểm tra port 5000 có đang được sử dụng không
2. Đảm bảo tất cả dependencies đã được cài đặt
3. Kiểm tra logs trong terminal

## 📝 License
MIT License

## 📞 Hỗ trợ
Nếu gặp vấn đề, vui lòng tạo issue trên GitHub repository. 