# RAG Chatbot — Technical Documentation Q&A

A Retrieval-Augmented Generation (RAG) system that answers questions
over a Wikipedia corpus using SBERT embeddings, FAISS vector search,
and Llama 3 via Groq API.

## Architecture
User Query → SBERT Embed → FAISS Retrieve → Llama 3 Answer → User

## Tech Stack
- Python
- Sentence Transformers (all-MiniLM-L6-v2)
- FAISS (vector database)
- Groq API (Llama 3.3 70B)
- Streamlit (UI)
- LangChain (text splitting)
- Wikipedia API (corpus)

## Quick Start

### 1. Clone the repo
git clone https://github.com/yourusername/rag-chatbot.git
cd rag-chatbot

### 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Add your Groq API key
Create a .env file:
GROQ_API_KEY=your_key_here

Get a free key at https://console.groq.com

### 5. Build the vector index
python vector_store.py

### 6. Run the chatbot
streamlit run app.py

## How It Works
1. Wikipedia articles loaded and split into 500 word chunks
2. Each chunk embedded using Sentence Transformers
3. Embeddings stored in FAISS vector index
4. User query embedded and top 4 similar chunks retrieved
5. Retrieved chunks sent to Llama 3 as context
6. Llama 3 generates answer grounded in retrieved context

## Topics Covered
- Python programming language
- Machine learning
- Neural networks
- Natural language processing
- Transformers

## Results
- 730 document chunks indexed
- Top 4 chunks retrieved per query
- Average response time under 3 seconds