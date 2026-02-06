#!/bin/bash

echo "🤖 AI Document Q&A System - Quick Start"
echo "======================================="
echo ""
echo "📦 Checking dependencies..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 found"

# Check if required packages are installed
echo ""
echo "📦 Installing dependencies..."
pip3 install -q fastapi uvicorn python-multipart PyPDF2 python-docx 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "⚠️  Some dependencies might already be installed"
fi

echo ""
echo "🚀 Starting FastAPI server..."
echo ""
echo "📍 API will be available at: http://127.0.0.1:8000"
echo "📚 API Docs: http://127.0.0.1:8000/docs"
echo "💬 Frontend: Open index.html in your browser"
echo ""
echo "⭐ Sample document available: sample_document.txt"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 main.py
