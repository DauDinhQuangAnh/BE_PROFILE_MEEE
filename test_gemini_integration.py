#!/usr/bin/env python3
"""
Test script for Gemini AI integration
Demonstrates how to use the enhanced /api/query endpoint with AI responses
"""

import requests
import json
import time

# Configuration
API_BASE_URL = "http://localhost:5000"

def test_gemini_availability():
    """Test if Gemini AI is available"""
    print("🔍 Testing Gemini AI Availability")
    print("=" * 50)
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/test-gemini",
            json={"prompt": "Xin chào! Bạn có khỏe không?"},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Gemini AI is available!")
            print(f"🤖 Response: {result.get('response', '')[:200]}...")
            return True
        elif response.status_code == 503:
            print("❌ Gemini AI not available")
            print("   Please check your GEMINI_API_KEY in .env file")
            return False
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.json()}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("   Make sure the Flask API is running: python api/app.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_query_with_ai():
    """Test the enhanced /api/query endpoint with AI responses"""
    print("\n🎯 Testing Query API with AI Responses")
    print("=" * 50)
    
    test_questions = [
        "Thông tin về chủ đề A",
        "Dữ liệu mẫu có gì?",
        "Tìm hiểu về các chủ đề khác nhau"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🧪 Test {i}: {question}")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/query",
                json={
                    "question": question,
                    "match_threshold": 0.2,
                    "match_count": 3
                },
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ Query successful!")
                print(f"📊 Question: {result.get('question')}")
                print(f"🎯 Found matches: {result.get('found_matches')}")
                print(f"📋 Unique documents: {result.get('unique_original_data_count', 'N/A')}")
                
                # Show AI status
                ai_status = result.get('ai_status', 'unknown')
                print(f"🤖 AI Status: {ai_status}")
                
                if ai_status == 'success':
                    ai_response = result.get('ai_response', '')
                    print(f"🎉 AI Response:")
                    print(f"   {ai_response}")
                elif ai_status == 'failed':
                    ai_error = result.get('ai_error', 'Unknown error')
                    print(f"❌ AI Error: {ai_error}")
                elif ai_status == 'unavailable':
                    print("ℹ️ AI not available (no API key)")
                
                # Show combined content (prompt sent to AI)
                combined_content = result.get('combined_content', '')
                if combined_content:
                    print(f"\n📄 Prompt sent to AI:")
                    print(f"   {combined_content[:300]}...")
                
            else:
                print(f"❌ Query failed: {response.status_code}")
                print(f"   {response.json()}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to API server")
            print("   Make sure the Flask API is running: python api/app.py")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def test_gemini_direct():
    """Test Gemini AI directly"""
    print("\n🤖 Testing Gemini AI Directly")
    print("=" * 50)
    
    test_prompts = [
        "Xin chào! Bạn có thể giới thiệu về bản thân không?",
        "Hãy kể một câu chuyện vui về một con mèo",
        "Giải thích về trí tuệ nhân tạo một cách đơn giản"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n🧪 Test {i}: {prompt[:50]}...")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/test-gemini",
                json={"prompt": prompt},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Gemini response:")
                print(f"   {result.get('response', '')}")
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"   {response.json()}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to API server")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def show_usage_instructions():
    """Show how to use the enhanced API"""
    print("\n📚 Usage Instructions")
    print("=" * 50)
    print("""
🚀 How to use the enhanced /api/query endpoint:

1. 🔑 Setup Gemini API Key:
   - Get API key from: https://makersuite.google.com/app/apikey
   - Add to .env file: GEMINI_API_KEY=your_key_here

2. 🎯 Make a query request:
   POST http://localhost:5000/api/query
   {
     "question": "Your question here",
     "match_threshold": 0.5,
     "match_count": 2
   }

3. 📊 Response includes:
   - question: Your original question
   - found_matches: Number of relevant documents found
   - combined_content: Prompt sent to AI
   - ai_response: Generated AI response (if available)
   - ai_status: success/failed/unavailable

4. 🤖 AI Response Format:
   - Uses teencode style with icons
   - Based on relevant documents found
   - Personalized as Đậu Đình Quang Anh

5. 🧪 Test endpoints:
   - Test Gemini: POST /api/test-gemini
   - Test connection: GET /api/test-connection
   - Health check: GET /health
""")

def main():
    """Main test function"""
    print("🎯 Gemini AI Integration Test Suite")
    print("=" * 80)
    
    # Test Gemini availability
    gemini_available = test_gemini_availability()
    
    if gemini_available:
        # Test direct Gemini
        test_gemini_direct()
        
        # Test query with AI
        test_query_with_ai()
    else:
        print("\n⚠️ Skipping AI tests - Gemini not available")
        print("   Please add GEMINI_API_KEY to your .env file")
    
    # Show usage instructions
    show_usage_instructions()
    
    print("\n" + "=" * 80)
    print("🎉 Gemini AI integration test completed!")

if __name__ == "__main__":
    main() 