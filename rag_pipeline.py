import faiss
import numpy as np
import pickle
import os
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class RAGChatbot:
    def __init__(self):
        print("Loading embedding model...")
        self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")

        print("Loading FAISS index...")
        self.index = faiss.read_index("faiss_index.bin")

        print("Loading chunks...")
        with open("chunks.pkl", "rb") as f:
            self.chunks = pickle.load(f)

        print("Connecting to Groq...")
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env file!")
        self.groq = Groq(api_key=api_key)

        print(f"Ready! {self.index.ntotal} chunks loaded.\n")

    def retrieve(self, query, top_k=4):
        query_embedding = self.embed_model.encode([query])
        distances, indices = self.index.search(np.array(query_embedding), top_k)
        results = []
        for idx in indices[0]:
            if idx < len(self.chunks):
                results.append(self.chunks[idx])
        return results

    def answer(self, query):
        # Step 1: Retrieve relevant chunks
        relevant_chunks = self.retrieve(query)

        # Step 2: Build context from chunks
        context = "\n\n".join([
            f"[Source: {c['source']}]\n{c['text']}"
            for c in relevant_chunks
        ])

        # Step 3: Build prompt
        prompt = f"""You are a helpful assistant that answers questions using only the context provided below.
If the answer is not in the context, say "I don't have enough information about that."
Always mention which source your answer comes from.

Context:
{context}

Question: {query}

Answer:"""

        # Step 4: Call Groq Llama 3
        response = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=512
        )

        answer = response.choices[0].message.content
        sources = list(set([c["source"] for c in relevant_chunks]))
        return answer, sources

if __name__ == "__main__":
    bot = RAGChatbot()

    # Test questions
    test_questions = [
        "What is machine learning?",
        "How do neural networks work?",
        "What is natural language processing used for?",
        "What is Python used for?"
    ]

    for question in test_questions:
        print(f"Question: {question}")
        print("-" * 50)
        answer, sources = bot.answer(question)
        print(f"Answer: {answer}")
        print(f"Sources: {', '.join(sources)}")
        print("=" * 50 + "\n")