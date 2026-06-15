import wikipediaapi
from langchain_text_splitters import RecursiveCharacterTextSplitter

TOPICS = [
    "Python (programming language)",
    "Machine learning",
    "Neural network",
    "Natural language processing",
    "Transformer (Machine learning model)"
]

def load_wikipedia_docs(topics):
    wiki = wikipediaapi.Wikipedia(
        language="en",
        user_agent="rag-chatbot/1.0"
    )
    docs = []
    for topic in topics:
        try:
            page = wiki.page(topic)
            if page.exists():
                docs.append({"title": topic, "content": page.text})
                print(f"Loaded: {topic}")
            else:
                print(f"Page not found: {topic}")
        except Exception as e:
            print(f"Skipped {topic}: {e}")
    return docs

def chunk_documents(docs, chunk_size=500, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = []
    for doc in docs:
        parts = splitter.split_text(doc["content"])
        for part in parts:
            chunks.append({"text": part, "source": doc["title"]})
    print(f"Total chunks created: {len(chunks)}")
    return chunks

if __name__ == "__main__":
    docs = load_wikipedia_docs(TOPICS)
    if len(docs) == 0:
        print("No documents loaded. Check internet connection.")
    else:
        chunks = chunk_documents(docs)
        print("\n--- Preview of First Chunk ---")
        print(f"Source: {chunks[0]['source']}")
        print(f"Text: {chunks[0]['text'][:300]}")