"""
Improved AI Question Answering Functions
Choose one of these based on your needs:
"""

# ============================================
# OPTION 1: Enhanced Keyword Matching (No API needed)
# ============================================
def answer_question_enhanced(question: str, context: str) -> str:
    """
    Enhanced keyword-based Q&A with better context understanding
    """
    import re
    
    question_lower = question.lower()
    context_lower = context.lower()
    
    # Handle common question patterns
    if any(word in question_lower for word in ['what', 'topic', 'about', 'subject']):
        # Return first few sentences as overview
        sentences = [s.strip() + '.' for s in context.split('.') if len(s.strip()) > 20]
        if sentences:
            return f"This document discusses: {' '.join(sentences[:3])}"
    
    if any(word in question_lower for word in ['summarize', 'summary', 'overview']):
        # Create a summary
        sentences = [s.strip() for s in context.split('.') if len(s.strip()) > 30]
        summary_sentences = sentences[:5] if len(sentences) >= 5 else sentences
        return "Summary: " + ". ".join(summary_sentences) + "."
    
    if any(word in question_lower for word in ['how many', 'count', 'number']):
        # Try to find numbers in context
        numbers = re.findall(r'\b\d+\.?\d*%?\b', context)
        if numbers:
            return f"The document mentions these numbers: {', '.join(numbers[:10])}"
    
    # Default: Find relevant sentences
    sentences = [s.strip() for s in context.split('.') if s.strip()]
    question_words = set(question_lower.split())
    
    relevant_sentences = []
    for sentence in sentences:
        sentence_words = set(sentence.lower().split())
        overlap = len(question_words.intersection(sentence_words))
        if overlap > 0:
            relevant_sentences.append((overlap, sentence))
    
    relevant_sentences.sort(reverse=True, key=lambda x: x[0])
    
    if relevant_sentences:
        top_sentences = [s[1] for s in relevant_sentences[:3]]
        return "Based on the document: " + ". ".join(top_sentences) + "."
    else:
        # Return first paragraph as fallback
        paragraphs = [p.strip() for p in context.split('\n\n') if len(p.strip()) > 50]
        if paragraphs:
            return f"Here's what I found: {paragraphs[0]}"
        return "I couldn't find specific information. Could you please rephrase your question?"


# ============================================
# OPTION 2: OpenAI GPT Integration (Best Results!)
# ============================================
def answer_question_openai(question: str, context: str) -> str:
    """
    Use OpenAI GPT for intelligent answers
    Install: pip install openai
    Set API key: export OPENAI_API_KEY="your-key"
    """
    import openai
    import os
    
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or "gpt-4" for better results
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions based on document content. Be concise and accurate."
                },
                {
                    "role": "user",
                    "content": f"Document content:\n{context[:3000]}\n\nQuestion: {question}\n\nAnswer based only on the document content:"
                }
            ],
            max_tokens=300,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error calling OpenAI API: {str(e)}"


# ============================================
# OPTION 3: Anthropic Claude Integration
# ============================================
def answer_question_claude(question: str, context: str) -> str:
    """
    Use Anthropic Claude for answers
    Install: pip install anthropic
    Set API key: export ANTHROPIC_API_KEY="your-key"
    """
    import anthropic
    import os
    
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    try:
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=300,
            messages=[
                {
                    "role": "user",
                    "content": f"Here is a document:\n\n{context[:3000]}\n\nBased ONLY on this document, please answer: {question}"
                }
            ]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error calling Claude API: {str(e)}"


# ============================================
# OPTION 4: LangChain with Vector Search (Advanced!)
# ============================================
def answer_question_langchain(question: str, context: str) -> str:
    """
    Use LangChain with embeddings for semantic search
    Install: pip install langchain openai chromadb
    """
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.vectorstores import Chroma
    from langchain.chains import RetrievalQA
    from langchain.llms import OpenAI
    import os
    
    try:
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_text(context)
        
        # Create embeddings and vector store
        embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        vectorstore = Chroma.from_texts(chunks, embeddings)
        
        # Create QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=OpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY")),
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
        )
        
        # Get answer
        answer = qa_chain.run(question)
        return answer
    except Exception as e:
        return f"Error with LangChain: {str(e)}"


# ============================================
# OPTION 5: Local LLM with Ollama (No API costs!)
# ============================================
def answer_question_ollama(question: str, context: str) -> str:
    """
    Use local Ollama models (free, runs on your machine)
    Install Ollama from: https://ollama.ai
    Then: ollama pull llama2
    Install: pip install ollama
    """
    import ollama
    
    try:
        response = ollama.chat(
            model='llama2',  # or 'mistral', 'codellama', etc.
            messages=[
                {
                    'role': 'system',
                    'content': 'Answer questions based only on the provided document content.'
                },
                {
                    'role': 'user',
                    'content': f'Document:\n{context[:3000]}\n\nQuestion: {question}'
                }
            ]
        )
        return response['message']['content']
    except Exception as e:
        return f"Error with Ollama: {str(e)}"


# ============================================
# How to use in main.py:
# ============================================
"""
Replace the answer_question() function in main.py with:

def answer_question(question: str, context: str) -> str:
    # Choose ONE of the following:
    
    # Option 1: Enhanced keyword (no API needed)
    return answer_question_enhanced(question, context)
    
    # Option 2: OpenAI GPT (best results, paid)
    # return answer_question_openai(question, context)
    
    # Option 3: Anthropic Claude (excellent, paid)
    # return answer_question_claude(question, context)
    
    # Option 4: LangChain (advanced, paid)
    # return answer_question_langchain(question, context)
    
    # Option 5: Ollama (free, runs locally)
    # return answer_question_ollama(question, context)
"""
