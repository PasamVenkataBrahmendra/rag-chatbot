import faiss
import numpy as np
import os
import wikipediaapi
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

class RAGChatbot:
    def __init__(self):
        print("Loading embedding model...")
        self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")

        print("Connecting to Groq...")
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env file!")
        self.groq = Groq(api_key=api_key)

        self.wiki = wikipediaapi.Wikipedia(
            language="en",
            user_agent="rag-chatbot/1.0"
        )

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

        print("Ready! I can now answer ANY question!\n")

    def search_wikipedia(self, query):
        print(f"Searching Wikipedia for: {query}")

        page = self.wiki.page(query)
        if page.exists():
            return page.text, page.title

        # Try shorter versions of the query
        words = query.split()
        for i in range(len(words), 0, -1):
            shorter = " ".join(words[:i])
            page = self.wiki.page(shorter)
            if page.exists():
                print(f"Found page: {shorter}")
                return page.text, page.title

        return None, None

    def build_dynamic_index(self, text):
        chunks = self.splitter.split_text(text)
        if not chunks:
            return None, []

        embeddings = self.embed_model.encode(chunks, show_progress_bar=False)
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(embeddings))
        return index, chunks

    def retrieve(self, query, index, chunks, top_k=4):
        query_embedding = self.embed_model.encode([query])
        distances, indices = index.search(np.array(query_embedding), top_k)
        results = []
        for idx in indices[0]:
            if idx < len(chunks):
                results.append(chunks[idx])
        return results

    def call_llm(self, system_prompt, user_prompt):
        response = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=512
        )
        return response.choices[0].message.content

    def answer(self, query):
        # Step 1: Search Wikipedia dynamically
        wiki_text, wiki_title = self.search_wikipedia(query)

        # System prompt used everywhere
        system_prompt = """You are a helpful assistant. 
Answer questions directly, clearly and confidently.
Never say 'based on general knowledge' or 'the context does not mention'.
Never reference any context or documents in your answer.
Just give a clean, direct, accurate answer as if you know it yourself."""

        if not wiki_text:
            # No Wikipedia page found — use Llama 3 directly
            print("No Wikipedia page found. Using Llama 3 directly...")
            answer = self.call_llm(system_prompt, query)
            return answer, ["Llama 3"]

        # Step 2: Build dynamic FAISS index from Wikipedia page
        index, chunks = self.build_dynamic_index(wiki_text)

        if not chunks:
            answer = self.call_llm(system_prompt, query)
            return answer, ["Llama 3"]

        # Step 3: Retrieve most relevant chunks
        relevant_chunks = self.retrieve(query, index, chunks)

        # Step 4: Build context
        context = "\n\n".join(relevant_chunks)

        # Step 5: Build user prompt with context
        user_prompt = f"""Use the information below to answer the question.

Information:
{context}

Question: {query}"""

        # Step 6: Call Groq Llama 3
        answer = self.call_llm(system_prompt, user_prompt)
        return answer, [f"Wikipedia: {wiki_title}"]

if __name__ == "__main__":
    bot = RAGChatbot()
    while True:
        q = input("\nAsk anything (or 'quit'): ")
        if q.lower() == "quit":
            break
        answer, sources = bot.answer(q)
        print(f"\nAnswer: {answer}")
        print(f"Sources: {', '.join(sources)}")