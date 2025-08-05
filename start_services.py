#!/usr/bin/env python3
"""
Start script for Chatbot Management System
"""

import subprocess
import sys
import time
import os
import signal
import threading
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'flask', 'streamlit', 'supabase', 'python-dotenv', 
        'flask-cors', 'requests', 'pandas'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install missing packages:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def check_env_file():
    """Check if .env file exists"""
    print("🔍 Checking environment configuration...")
    
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please create .env file from env_example.txt:")
        print("cp env_example.txt .env")
        print("Then update with your Supabase credentials.")
        return False
    
    print("✅ .env file found!")
    return True

def start_flask_api():
    """Start Flask API server"""
    print("🚀 Starting Flask API...")
    
    try:
        # Start Flask API in a subprocess
        api_process = subprocess.Popen([
            sys.executable, 'api/app.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for the server to start
        time.sleep(3)
        
        # Check if process is still running
        if api_process.poll() is None:
            print("✅ Flask API started successfully!")
            return api_process
        else:
            stdout, stderr = api_process.communicate()
            print(f"❌ Flask API failed to start:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting Flask API: {e}")
        return None

def start_streamlit():
    """Start Streamlit UI"""
    print("🚀 Starting Streamlit UI...")
    
    try:
        # Start Streamlit in a subprocess
        streamlit_process = subprocess.Popen([
            sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py',
            '--server.port', '8501',
            '--server.address', 'localhost'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for the server to start
        time.sleep(5)
        
        # Check if process is still running
        if streamlit_process.poll() is None:
            print("✅ Streamlit UI started successfully!")
            return streamlit_process
        else:
            stdout, stderr = streamlit_process.communicate()
            print(f"❌ Streamlit failed to start:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        return None

def monitor_processes(api_process, streamlit_process):
    """Monitor running processes"""
    print("\n📊 Monitoring services...")
    print("Press Ctrl+C to stop all services")
    
    try:
        while True:
            # Check if processes are still running
            if api_process and api_process.poll() is not None:
                print("❌ Flask API stopped unexpectedly")
                break
                
            if streamlit_process and streamlit_process.poll() is not None:
                print("❌ Streamlit stopped unexpectedly")
                break
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        
        # Stop Flask API
        if api_process:
            api_process.terminate()
            try:
                api_process.wait(timeout=5)
                print("✅ Flask API stopped")
            except subprocess.TimeoutExpired:
                api_process.kill()
                print("⚠️ Flask API force killed")
        
        # Stop Streamlit
        if streamlit_process:
            streamlit_process.terminate()
            try:
                streamlit_process.wait(timeout=5)
                print("✅ Streamlit stopped")
            except subprocess.TimeoutExpired:
                streamlit_process.kill()
                print("⚠️ Streamlit force killed")

def main():
    """Main function"""
    print("🤖 Chatbot Management System")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    if not check_env_file():
        sys.exit(1)
    
    # Start Flask API
    api_process = start_flask_api()
    if not api_process:
        print("❌ Failed to start Flask API")
        sys.exit(1)
    
    # Start Streamlit
    streamlit_process = start_streamlit()
    if not streamlit_process:
        print("❌ Failed to start Streamlit")
        api_process.terminate()
        sys.exit(1)
    
    # Print service URLs
    print("\n" + "=" * 50)
    print("🎉 All services started successfully!")
    print("\n📱 Service URLs:")
    print("Flask API: http://localhost:5000")
    print("Streamlit UI: http://localhost:8501")
    print("\n📚 API Endpoints:")
    print("Health Check: http://localhost:5000/health")
    print("Chat API: http://localhost:5000/api/chat")
    print("Chat History: http://localhost:5000/api/chat/history")
    print("Test Connection: http://localhost:5000/api/test-connection")
    
    # Monitor processes
    monitor_processes(api_process, streamlit_process)
    
    print("\n👋 Goodbye!")

if __name__ == "__main__":
    main() 