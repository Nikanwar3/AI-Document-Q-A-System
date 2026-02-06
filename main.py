from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sqlite3
import os
import json
from pathlib import Path

# For document processing
import PyPDF2
import docx
from io import BytesIO

app = FastAPI(
    title="AI Document Q&A System",
    description="Upload documents and ask questions using AI",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory setup
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

DB_PATH = "documents.db"

# Pydantic models
class QuestionRequest(BaseModel):
    question: str
    document_id: Optional[int] = None

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: str

class DocumentInfo(BaseModel):
    id: int
    filename: str
    upload_date: str
    file_size: int
    content_preview: str

# Database initialization
def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            content TEXT NOT NULL,
            upload_date TEXT NOT NULL,
            file_size INTEGER
        )
    """)
    
    # Chat history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (document_id) REFERENCES documents (id)
        )
    """)
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Document processing functions
def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(BytesIO(file_content))
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading DOCX: {str(e)}")

def extract_text_from_txt(file_content: bytes) -> str:
    """Extract text from TXT file"""
    try:
        return file_content.decode('utf-8').strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading TXT: {str(e)}")

def process_document(filename: str, file_content: bytes) -> str:
    """Process document based on file type"""
    file_ext = filename.lower().split('.')[-1]
    
    if file_ext == 'pdf':
        return extract_text_from_pdf(file_content)
    elif file_ext == 'docx':
        return extract_text_from_docx(file_content)
    elif file_ext == 'txt':
        return extract_text_from_txt(file_content)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF, DOCX, or TXT files.")

# Simple AI answering function - ENHANCED VERSION
def answer_question(question: str, context: str) -> str:
    """
    Enhanced keyword-based Q&A system with better context understanding.
    For production, integrate OpenAI API, Anthropic Claude, or LangChain.
    See ai_improvements.py for advanced options.
    """
    import re
    
    question_lower = question.lower()
    context_lower = context.lower()
    
    # Handle "what is this about" / "topic" type questions
    if any(word in question_lower for word in ['what', 'topic', 'about', 'subject', 'main', 'discuss']):
        # Return first few sentences as overview
        sentences = [s.strip() + '.' for s in context.split('.') if len(s.strip()) > 20]
        if sentences:
            return f"This document discusses: {' '.join(sentences[:3])}"
    
    # Handle summary requests
    if any(word in question_lower for word in ['summarize', 'summary', 'overview', 'gist']):
        sentences = [s.strip() for s in context.split('.') if len(s.strip()) > 30]
        summary_sentences = sentences[:5] if len(sentences) >= 5 else sentences
        return "📝 Summary: " + ". ".join(summary_sentences) + "."
    
    # Handle counting/number questions
    if any(word in question_lower for word in ['how many', 'count', 'number of']):
        numbers = re.findall(r'\b\d+\.?\d*%?\b', context)
        if numbers:
            return f"📊 The document mentions these numbers: {', '.join(numbers[:10])}"
    
    # Handle "who", "where", "when" questions
    if question_lower.startswith('who'):
        # Look for names (capitalized words)
        names = re.findall(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b', context)
        if names:
            return f"👤 People/entities mentioned: {', '.join(set(names[:10]))}"
    
    # Default: Find relevant sentences with better matching
    sentences = [s.strip() for s in context.split('.') if s.strip()]
    question_words = set(w for w in question_lower.split() if len(w) > 3)
    
    relevant_sentences = []
    for sentence in sentences:
        sentence_words = set(sentence.lower().split())
        overlap = len(question_words.intersection(sentence_words))
        if overlap > 0:
            relevant_sentences.append((overlap, sentence))
    
    relevant_sentences.sort(reverse=True, key=lambda x: x[0])
    
    if relevant_sentences:
        top_sentences = [s[1] for s in relevant_sentences[:3]]
        return "📄 Based on the document: " + ". ".join(top_sentences) + "."
    else:
        # Return first paragraph as fallback
        paragraphs = [p.strip() for p in context.split('\n\n') if len(p.strip()) > 50]
        if paragraphs:
            return f"ℹ️ Here's what I found in the document:\n\n{paragraphs[0]}"
        
        # Last resort: return first 500 characters
        if len(context) > 100:
            return f"📖 Document overview: {context[:500]}..."
        
        return "❓ I couldn't find specific information to answer that question. Could you try rephrasing or ask about something specific mentioned in the document?"

# API Endpoints
@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "AI Document Q&A System",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/upload",
            "documents": "/documents",
            "ask": "/ask",
            "history": "/history"
        }
    }

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document (PDF, DOCX, TXT)"""
    try:
        # Read file content
        content = await file.read()
        
        # Extract text
        text_content = process_document(file.filename, content)
        
        if not text_content or len(text_content) < 10:
            raise HTTPException(status_code=400, detail="Document appears to be empty or too short")
        
        # Save to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO documents (filename, content, upload_date, file_size)
            VALUES (?, ?, ?, ?)
        """, (file.filename, text_content, datetime.now().isoformat(), len(content)))
        conn.commit()
        doc_id = cursor.lastrowid
        conn.close()
        
        return {
            "success": True,
            "message": "Document uploaded successfully",
            "document_id": doc_id,
            "filename": file.filename,
            "characters": len(text_content),
            "preview": text_content[:200] + "..." if len(text_content) > 200 else text_content
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.get("/documents")
async def get_documents():
    """Get all uploaded documents"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, upload_date, file_size, content FROM documents ORDER BY upload_date DESC")
    rows = cursor.fetchall()
    conn.close()
    
    documents = []
    for row in rows:
        documents.append({
            "id": row[0],
            "filename": row[1],
            "upload_date": row[2],
            "file_size": row[3],
            "content_preview": row[4][:150] + "..." if len(row[4]) > 150 else row[4]
        })
    
    return {"documents": documents}

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """Ask a question about a document"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get document content
        if request.document_id:
            cursor.execute("SELECT content, filename FROM documents WHERE id = ?", (request.document_id,))
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Document not found")
            context, filename = result
        else:
            # Use the most recent document
            cursor.execute("SELECT id, content, filename FROM documents ORDER BY upload_date DESC LIMIT 1")
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="No documents uploaded yet")
            request.document_id, context, filename = result
        
        # Generate answer
        answer = answer_question(request.question, context)
        
        # Save to chat history
        timestamp = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO chat_history (document_id, question, answer, timestamp)
            VALUES (?, ?, ?, ?)
        """, (request.document_id, request.question, answer, timestamp))
        conn.commit()
        conn.close()
        
        return {
            "question": request.question,
            "answer": answer,
            "document": filename,
            "document_id": request.document_id,
            "timestamp": timestamp
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.get("/history")
async def get_chat_history(document_id: Optional[int] = None, limit: int = 20):
    """Get chat history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if document_id:
        cursor.execute("""
            SELECT ch.question, ch.answer, ch.timestamp, d.filename
            FROM chat_history ch
            JOIN documents d ON ch.document_id = d.id
            WHERE ch.document_id = ?
            ORDER BY ch.timestamp DESC
            LIMIT ?
        """, (document_id, limit))
    else:
        cursor.execute("""
            SELECT ch.question, ch.answer, ch.timestamp, d.filename
            FROM chat_history ch
            JOIN documents d ON ch.document_id = d.id
            ORDER BY ch.timestamp DESC
            LIMIT ?
        """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            "question": row[0],
            "answer": row[1],
            "timestamp": row[2],
            "document": row[3]
        })
    
    return {"history": history}

@app.delete("/documents/{document_id}")
async def delete_document(document_id: int):
    """Delete a document and its chat history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if document exists
    cursor.execute("SELECT id FROM documents WHERE id = ?", (document_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete chat history
    cursor.execute("DELETE FROM chat_history WHERE document_id = ?", (document_id,))
    
    # Delete document
    cursor.execute("DELETE FROM documents WHERE id = ?", (document_id,))
    
    conn.commit()
    conn.close()
    
    return {"success": True, "message": "Document deleted successfully"}

@app.delete("/history")
async def clear_history():
    """Clear all chat history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history")
    conn.commit()
    conn.close()
    
    return {"success": True, "message": "Chat history cleared"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AI Document Q&A System...")
    print("📄 Upload documents and ask questions!")
    print("🌐 API: http://127.0.0.1:8000")
    print("📚 Docs: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
