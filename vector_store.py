import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from load_docs import load_wikipedia_docs, chunk_documents

TOPICS = [
    "Python (programming language)",
    "Machine learning",
    "Neural network",
    "Natural language processing",
    "Transformer (machine learning model)"
]

def build_vector_store(chunks):
    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Creating embeddings (this takes 1-2 minutes)...")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)

    print("Building FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))

    print(f"FAISS index built with {index.ntotal} vectors")

    print("Saving to disk...")
    faiss.write_index(index, "faiss_index.bin")
    with open("chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)

    print("Done! Files saved: faiss_index.bin, chunks.pkl")
    return index, chunks

if __name__ == "__main__":
    print("Step 1: Loading Wikipedia docs...")
    docs = load_wikipedia_docs(TOPICS)

    print("\nStep 2: Chunking documents...")
    chunks = chunk_documents(docs)

    print("\nStep 3: Building vector store...")
    index, chunks = build_vector_store(chunks)

    print("\n--- Testing Search ---")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    test_query = "What is machine learning?"
    query_embedding = model.encode([test_query])
    distances, indices = index.search(np.array(query_embedding), 3)

    print(f"Query: {test_query}")
    print(f"\nTop 3 matching chunks:")
    for i, idx in enumerate(indices[0]):
        print(f"\nResult {i+1}:")
        print(f"Source: {chunks[idx]['source']}")
        print(f"Text: {chunks[idx]['text'][:200]}")