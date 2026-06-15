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

        # Chat memory — stores full conversation
        self.chat_history = []

        print("Ready!\n")

    def search_wikipedia(self, query):
        print(f"Searching Wikipedia for: {query}")
        page = self.wiki.page(query)
        if page.exists():
            return page.text, page.title

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

    def get_followup_questions(self, query, answer):
        prompt = f"""Based on this question and answer, suggest exactly 3 short follow up questions the user might want to ask next.
Return ONLY the 3 questions, one per line, no numbering, no extra text.

Question: {query}
Answer: {answer}

3 follow up questions:"""

        response = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=150
        )
        raw = response.choices[0].message.content.strip()
        questions = [q.strip() for q in raw.split("\n") if q.strip()]
        return questions[:3]

    def answer_stream(self, query):
        # Step 1: Add user message to history
        self.chat_history.append({"role": "user", "content": query})

        # Step 2: Search Wikipedia
        wiki_text, wiki_title = self.search_wikipedia(query)

        system_prompt = """You are a helpful assistant like ChatGPT.
Answer questions directly, clearly and confidently.
Format your answers nicely using bullet points or numbered lists when appropriate.
Never say 'based on general knowledge' or 'the context does not mention'.
Never reference any context or documents in your answer.
Keep answers concise but complete."""

        if not wiki_text:
            # Use Llama 3 directly with chat history
            messages = [{"role": "system", "content": system_prompt}]
            messages += self.chat_history

            stream = self.groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.2,
                max_tokens=512,
                stream=True
            )

            full_answer = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_answer += delta
                yield delta, None, None

            self.chat_history.append({"role": "assistant", "content": full_answer})
            followups = self.get_followup_questions(query, full_answer)
            yield "", "Llama 3", followups
            return

        # Step 3: Build dynamic index
        index, chunks = self.build_dynamic_index(wiki_text)

        if not chunks:
            yield "I could not find relevant information.", wiki_title, []
            return

        # Step 4: Retrieve relevant chunks
        relevant_chunks = self.retrieve(query, index, chunks)
        context = "\n\n".join(relevant_chunks)

        # Step 5: Build messages with full chat history + context
        user_message = f"""Use the information below to answer the question.
Information:
{context}

Question: {query}"""

        messages = [{"role": "system", "content": system_prompt}]

        # Add previous chat history (excluding current message)
        if len(self.chat_history) > 1:
            messages += self.chat_history[:-1]

        messages.append({"role": "user", "content": user_message})

        # Step 6: Stream response
        stream = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.2,
            max_tokens=512,
            stream=True
        )

        full_answer = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_answer += delta
            yield delta, None, None

        # Step 7: Save assistant response to history
        self.chat_history.append({"role": "assistant", "content": full_answer})

        # Step 8: Generate follow up questions
        followups = self.get_followup_questions(query, full_answer)
        yield "", f"Wikipedia: {wiki_title}", followups

    def clear_history(self):
        self.chat_history = []