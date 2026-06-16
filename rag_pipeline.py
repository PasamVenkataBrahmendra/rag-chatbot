import faiss
import numpy as np
import os
import wikipediaapi
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

GREETINGS = [
    "hi", "hello", "hey", "good morning", "good evening",
    "good afternoon", "howdy", "what's up", "sup", "greetings",
    "hiya", "yo", "namaste", "helo", "hii", "hiii"
]

class RAGChatbot:
    def __init__(self):
        print("Loading embedding model...")
        self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Connecting to Groq...")
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found!")
        self.groq = Groq(api_key=api_key)
        self.wiki = wikipediaapi.Wikipedia(
            language="en",
            user_agent="rag-chatbot/1.0"
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        self.chat_history = []
        print("Ready!\n")

    def is_greeting(self, text):
        return text.lower().strip().rstrip("!.,?") in GREETINGS

    def search_wikipedia(self, query):
        page = self.wiki.page(query)
        if page.exists():
            return page.text, page.title
        words = query.split()
        for i in range(len(words), 0, -1):
            shorter = " ".join(words[:i])
            page = self.wiki.page(shorter)
            if page.exists():
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

    def get_confidence(self, query, answer, context):
        prompt = f"""Rate confidence that this answer is correct (0-100). Return ONLY the number.
Question: {query}
Answer: {answer}
Context: {context[:300]}
Score:"""
        try:
            response = self.groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=5
            )
            score = int(response.choices[0].message.content.strip().replace("%", ""))
            return min(max(score, 0), 100)
        except:
            return 85

    def get_followup_questions(self, query, answer):
        prompt = f"""Suggest exactly 3 short follow up questions based on this Q&A.
Return ONLY 3 questions, one per line, no numbering.

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

    def summarize_topic(self, topic, language="English"):
        wiki_text, wiki_title = self.search_wikipedia(topic)
        if not wiki_text:
            return f"Could not find information about {topic}.", "Not found"
        prompt = f"""Summarize the following in {language}.
Use clear bullet points and sections. Be concise but cover all key points.

Text: {wiki_text[:3000]}

Summary:"""
        response = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=800
        )
        return response.choices[0].message.content, wiki_title

    def answer_from_context(self, query, context, source_name, language="English"):
        system_prompt = f"""You are a helpful assistant like ChatGPT.
Answer questions directly and clearly in {language}.
Use bullet points when appropriate.
Base your answer on the provided context.
Never say 'the context does not mention'."""

        user_prompt = f"""Context:
{context}

Question: {query}"""

        self.chat_history.append({"role": "user", "content": query})
        messages = [{"role": "system", "content": system_prompt}]
        if len(self.chat_history) > 1:
            messages += self.chat_history[:-1]
        messages.append({"role": "user", "content": user_prompt})

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
            yield delta

        self.chat_history.append({"role": "assistant", "content": full_answer})

    def answer_image(self, query, image_base64, language="English"):
        self.chat_history.append({"role": "user", "content": query})
        response = self.groq.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": f"Answer in {language}. {query}"
                    }
                ]
            }],
            temperature=0.2,
            max_tokens=512
        )
        answer = response.choices[0].message.content
        self.chat_history.append({"role": "assistant", "content": answer})
        return answer

    def answer_stream(self, query, language="English"):
        self.chat_history.append({"role": "user", "content": query})

        system_prompt = f"""You are a helpful friendly assistant like ChatGPT.
Answer in {language}. Be direct, clear and helpful.
Use bullet points or numbered lists when appropriate.
For greetings respond warmly and ask how you can help.
Never say 'based on general knowledge' or 'the context does not mention'."""

        wiki_text, wiki_title = self.search_wikipedia(query)

        if not wiki_text:
            messages = [{"role": "system", "content": system_prompt}]
            messages += self.chat_history
            stream = self.groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.3,
                max_tokens=512,
                stream=True
            )
            full_answer = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_answer += delta
                yield delta, None, None, None
            self.chat_history.append({"role": "assistant", "content": full_answer})
            followups = [] if self.is_greeting(query) else self.get_followup_questions(query, full_answer)
            confidence = None if self.is_greeting(query) else self.get_confidence(query, full_answer, "")
            yield "", "Llama 3", followups, confidence
            return

        index, chunks = self.build_dynamic_index(wiki_text)
        if not chunks:
            yield "I could not find relevant information.", wiki_title, [], 0
            return

        relevant_chunks = self.retrieve(query, index, chunks)
        context = "\n\n".join(relevant_chunks)

        user_message = f"""Information:
{context}

Question: {query}"""

        messages = [{"role": "system", "content": system_prompt}]
        if len(self.chat_history) > 1:
            messages += self.chat_history[:-1]
        messages.append({"role": "user", "content": user_message})

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
            yield delta, None, None, None

        self.chat_history.append({"role": "assistant", "content": full_answer})
        followups = self.get_followup_questions(query, full_answer)
        confidence = self.get_confidence(query, full_answer, context)
        yield "", f"Wikipedia: {wiki_title}", followups, confidence

    def clear_history(self):
        self.chat_history = []