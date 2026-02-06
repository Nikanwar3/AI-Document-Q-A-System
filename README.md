# 🤖 AI Document Q&A System

Upload documents (PDF, DOCX, TXT) and ask questions about them using AI! Built with FastAPI, SQLite, and a beautiful chat interface.

## ✨ Features

- 📄 **Document Upload** - Support for PDF, DOCX, and TXT files
- 💬 **AI Chat Interface** - Beautiful, modern chat UI
- 🗄️ **SQLite Database** - Store documents and chat history
- 📊 **Document Management** - View, select, and delete documents
- 🔄 **Chat History** - Automatic conversation tracking
- 🎨 **Responsive Design** - Works on desktop and mobile
- ⚡ **Real-time Updates** - Instant responses and updates

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install fastapi uvicorn python-multipart PyPDF2 python-docx
```

### 2. Start the Backend Server

```bash
python3 main.py
```

The API will run on `http://127.0.0.1:8000`

### 3. Open the Frontend

Simply open `index.html` in your browser:
```bash
open index.html        # Mac
start index.html       # Windows  
xdg-open index.html    # Linux
```

Or run a local server:
```bash
python3 -m http.server 8080
# Then visit: http://127.0.0.1:8080/index.html
```

## 📖 How to Use

1. **Upload a Document** 
   - Click the upload box or drag & drop
   - Supports PDF, DOCX, TXT files
   - Document is processed automatically

2. **Ask Questions**
   - Select a document from the sidebar
   - Type your question in the chat input
   - Get AI-powered answers instantly

3. **Manage Documents**
   - View all uploaded documents in sidebar
   - Click to switch between documents
   - Delete documents you no longer need

## 🏗️ Architecture

```
Frontend (HTML/CSS/JS)  ←→  Backend (FastAPI)  ←→  Database (SQLite)
     index.html              main.py              documents.db
```

### Backend API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | POST | Upload a document |
| `/documents` | GET | Get all documents |
| `/ask` | POST | Ask a question |
| `/history` | GET | Get chat history |
| `/documents/{id}` | DELETE | Delete a document |
| `/history` | DELETE | Clear chat history |

### Database Schema

**documents table:**
- id (PRIMARY KEY)
- filename
- content (extracted text)
- upload_date
- file_size

**chat_history table:**
- id (PRIMARY KEY)
- document_id (FOREIGN KEY)
- question
- answer
- timestamp

## 🎯 Features Explained

### Document Processing
- **PDF**: Extracts text using PyPDF2
- **DOCX**: Reads paragraphs using python-docx
- **TXT**: Direct UTF-8 decoding

### AI Question Answering
Current implementation uses **keyword-based matching** to find relevant sentences.

**For Production**: Integrate with:
- OpenAI API (GPT-4)
- LangChain
- Anthropic Claude API
- Local models (Ollama, LLaMA)

### Example Integration with OpenAI:

```python
import openai

def answer_question_with_gpt(question: str, context: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions based on document content."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
        ]
    )
    return response.choices[0].message.content
```

## 🔧 Customization

### Change AI Model

Edit `main.py` function `answer_question()`:

```python
def answer_question(question: str, context: str) -> str:
    # Replace with your AI model
    # Options: OpenAI API, Anthropic, LangChain, etc.
    pass
```

### Database Location

Change `DB_PATH` in `main.py`:
```python
DB_PATH = "path/to/your/database.db"
```

### Upload Directory

Change `UPLOAD_DIR` in `main.py`:
```python
UPLOAD_DIR = Path("your/upload/folder")
```

## 🎨 UI Customization

The `index.html` uses a purple gradient theme. To customize:

**Change colors:**
```css
background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
```

**Change fonts:**
```css
font-family: 'Your Font', sans-serif;
```

## 📊 API Examples

### Upload Document
```bash
curl -X POST "http://127.0.0.1:8000/upload" \
  -F "file=@document.pdf"
```

### Ask Question
```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?", "document_id": 1}'
```

### Get Documents
```bash
curl "http://127.0.0.1:8000/documents"
```

### Get Chat History
```bash
curl "http://127.0.0.1:8000/history?document_id=1&limit=10"
```

## 🔒 Security Notes

⚠️ **For Production:**
- Add authentication (JWT tokens)
- Implement rate limiting
- Validate file types strictly
- Add file size limits
- Use environment variables for API keys
- Enable HTTPS
- Sanitize user inputs
- Add CSRF protection

## 🐛 Troubleshooting

**Issue: "Could not connect to server"**
- Ensure `python3 main.py` is running
- Check if port 8000 is available
- Try `http://127.0.0.1:8000/docs` to verify API

**Issue: "Document upload failed"**
- Check file format (PDF, DOCX, TXT only)
- Ensure file is not corrupted
- Check file size (very large files may fail)

**Issue: "No documents uploaded yet"**
- Wait a few seconds after upload
- Refresh the page
- Check browser console for errors

## 🚀 Next Steps

### Enhancements to Add:
1. **Better AI Integration** - Use OpenAI, Claude, or LangChain
2. **Vector Search** - Add embeddings for semantic search
3. **Multi-language** - Support for different languages
4. **OCR Support** - Extract text from scanned PDFs
5. **User Authentication** - Add login system
6. **Export Chat** - Download conversations as PDF
7. **Document Comparison** - Compare multiple documents
8. **Advanced Search** - Full-text search across all documents

### LangChain Integration Example:

```python
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

# Create vector store
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_texts([context], embeddings)

# Create QA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    retriever=vectorstore.as_retriever()
)

# Ask question
answer = qa_chain.run(question)
```

## 📝 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

Contributions welcome! This is a starter template - make it your own!

## 💡 Tips

- Upload clear, well-formatted documents for best results
- Ask specific questions for better answers
- One document at a time works best
- Keep documents under 10MB for optimal performance

---

Built with ❤️ using FastAPI and modern web technologies
