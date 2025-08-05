# 📄 Document Management System

Hệ thống quản lý tài liệu với kết nối Supabase, giao diện Streamlit và API Flask để upload, xử lý và lưu trữ tài liệu.

## 🚀 Tính năng

- **Flask API**: Backend API để xử lý và lưu trữ tài liệu
- **Streamlit UI**: Giao diện upload và quản lý tài liệu
- **Supabase Integration**: Lưu trữ chunks tài liệu và vectors trong Supabase
- **Smart Text Processing**: 
  - Split câu với NLTK
  - Tính similarity với TF-IDF + Cosine
  - Gộp câu tương tự (threshold 0.5)
- **Vietnamese Embedding**: Sử dụng SentenceTransformer cho tiếng Việt
- **Document Management**: Quản lý và xuất dữ liệu tài liệu

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
-- additional (varchar) - lưu timestamp
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
```

## 🚀 Chạy ứng dụng

### 1. Khởi động Flask API
```bash
python api/app.py
```

API sẽ chạy tại: `http://localhost:5000`

### 2. Khởi động Streamlit UI
```bash
streamlit run streamlit_app.py
```

Giao diện sẽ mở tại: `http://localhost:8501`

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

### Test Connection
```
GET /api/test-connection
```
Kiểm tra kết nối Supabase

## 🎯 Sử dụng

### 1. Dashboard
- Xem tổng quan về hệ thống
- Thống kê số lượng tài liệu và chunks
- Trạng thái API và database

### 2. Upload Documents
- Upload file CSV/Excel với cấu trúc: STT, DATA, Link
- **Smart Text Processing**:
  - Split câu với NLTK
  - Tính similarity giữa 2 câu liên tiếp
  - Gộp câu tương tự (threshold có thể điều chỉnh)
- **Vietnamese Embedding**: Tạo vectors với SentenceTransformer
- Lưu trữ chunks và vectors vào database

### 3. Document Management
- Xem và quản lý chunks tài liệu
- Lọc theo nguồn tài liệu và ngày
- Xuất dữ liệu ra CSV

### 4. API Status
- Kiểm tra trạng thái các endpoint
- Test kết nối database
- Xem thông tin API

## 🔧 Cấu trúc dự án

```
chatbot-management-system/
├── api/
│   ├── __init__.py
│   └── app.py                 # Flask API
├── database/
│   ├── __init__.py
│   └── supabase_client.py     # Supabase connection (uses existing Vector_database table)
├── config.py                  # Configuration
├── streamlit_app.py           # Streamlit UI
├── requirements.txt           # Dependencies
├── env_example.txt           # Environment template
└── README.md                 # Documentation
```

## 📊 Database Schema

Dự án sử dụng bảng `Vector_database` hiện có trong Supabase:

| Column | Type | Description |
|--------|------|-------------|
| id | int8 | Primary key |
| chunks | varchar | Lưu CHUNK (đã xử lý) |
| Vector | varchar | Lưu vector encoding (768 dimensions) |
| Doc | varchar | Lưu DATA (gốc) |
| additional | varchar | Lưu link (format: "link:https://example.com") |

## 🧪 Test API

### Sử dụng curl
```bash
# Test health endpoint
curl http://localhost:5000/health

# Test chat endpoint
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, world!", "user_id": "test_user"}'

# Get chat history
curl http://localhost:5000/api/chat/history?limit=10
```

### Sử dụng Python requests
```python
import requests

# Test chat
response = requests.post(
    "http://localhost:5000/api/chat",
    json={"prompt": "Hello, world!", "user_id": "test_user"}
)
print(response.json())
```

## 🔒 Bảo mật

- Sử dụng biến môi trường cho thông tin nhạy cảm
- Validate input data
- Error handling cho tất cả API endpoints
- CORS enabled cho development

## 🐛 Troubleshooting

### Lỗi kết nối Supabase
1. Kiểm tra URL và API Key trong file `.env`
2. Đảm bảo bảng `chatbot_data` đã được tạo
3. Kiểm tra quyền truy cập trong Supabase dashboard

### Lỗi Flask API
1. Kiểm tra port 5000 có đang được sử dụng không
2. Đảm bảo tất cả dependencies đã được cài đặt
3. Kiểm tra logs trong terminal

### Lỗi Streamlit
1. Đảm bảo Flask API đang chạy
2. Kiểm tra URL API trong giao diện
3. Refresh trang nếu cần

## 📝 License

MIT License

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request

## 📞 Hỗ trợ

Nếu gặp vấn đề, vui lòng tạo issue trên GitHub repository. 