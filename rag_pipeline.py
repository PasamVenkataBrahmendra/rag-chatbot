import faiss
import numpy as np
import os
import time
import requests
import wikipediaapi
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

GREETINGS = [
    "hi", "hello", "hey", "good morning", "good evening",
    "good afternoon", "howdy", "what's up", "sup", "greetings",
    "hiya", "yo", "namaste", "helo", "hii", "hiii", "hai",
    "heya", "hi there", "hello there", "hey there"
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
        cleaned = text.lower().strip().rstrip("!.,?")
        return cleaned in GREETINGS

    def groq_call(self, messages, temperature=0.2, max_tokens=512, stream=False, retries=3):
        for attempt in range(retries):
            try:
                response = self.groq.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream
                )
                return response
            except Exception as e:
                error_str = str(e)
                if "rate_limit" in error_str.lower() or "429" in error_str:
                    wait_time = (attempt + 1) * 5
                    print(f"Rate limit hit. Waiting {wait_time}s before retry {attempt+1}/{retries}...")
                    time.sleep(wait_time)
                elif "503" in error_str or "service unavailable" in error_str.lower():
                    wait_time = (attempt + 1) * 3
                    print(f"Service unavailable. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise e
        raise Exception("Max retries exceeded. Please try again later.")

    def search_wikipedia(self, query):
        print(f"Searching Wikipedia for: {query}")
        page = self.wiki.page(query)
        if page.exists():
            return page.text, page.title, page.fullurl
        words = query.split()
        for i in range(len(words), 0, -1):
            shorter = " ".join(words[:i])
            page = self.wiki.page(shorter)
            if page.exists():
                return page.text, page.title, page.fullurl
        return None, None, None

    def build_dynamic_index(self, text):
        chunks = self.splitter.split_text(text)
        if not chunks:
            return None, []
        embeddings = self.embed_model.encode(chunks, show_progress_bar=False)
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(embeddings))
        return index, chunks

    def retrieve_with_scores(self, query, index, chunks, top_k=4):
        query_embedding = self.embed_model.encode([query])
        distances, indices = index.search(np.array(query_embedding), top_k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(chunks):
                score = max(0, 100 - int(dist * 10))
                results.append({
                    "text": chunks[idx],
                    "score": score,
                    "index": int(idx)
                })
        return results

    def get_confidence(self, query, answer, context):
        prompt = f"""Rate confidence that this answer is correct (0-100). Return ONLY the number.
Question: {query}
Answer: {answer}
Context: {context[:300]}
Score:"""
        try:
            response = self.groq_call(
                [{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=5
            )
            score = int(response.choices[0].message.content.strip().replace("%", ""))
            return min(max(score, 0), 100)
        except:
            return 85

    def get_followup_questions(self, query, answer):
        prompt = f"""Suggest exactly 3 short follow up questions based on this Q&A.
Return ONLY 3 questions, one per line, no numbering, no extra text.

Question: {query}
Answer: {answer}

3 follow up questions:"""
        try:
            response = self.groq_call(
                [{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=150
            )
            raw = response.choices[0].message.content.strip()
            questions = [q.strip() for q in raw.split("\n") if q.strip()]
            return questions[:3]
        except:
            return []

    def improve_prompt(self, original_prompt):
        system_prompt = """You are an expert prompt engineer.
Rewrite the user's prompt to be clearer, more specific and more likely to get a great answer.
Return ONLY the improved prompt, nothing else.
Keep the same intent but make it much better."""

        try:
            response = self.groq_call(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Improve this prompt: {original_prompt}"}
                ],
                temperature=0.3,
                max_tokens=200
            )
            return response.choices[0].message.content.strip()
        except:
            return original_prompt

    def summarize_topic(self, topic, language="English"):
        wiki_text, wiki_title, wiki_url = self.search_wikipedia(topic)
        if not wiki_text:
            return f"Could not find information about {topic}.", "Not found"
        prompt = f"""Summarize the following in {language}.
Use clear bullet points and sections. Be concise but cover all key points.

Text: {wiki_text[:3000]}

Summary:"""
        try:
            response = self.groq_call(
                [{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=800
            )
            return response.choices[0].message.content, wiki_title
        except Exception as e:
            return f"Error: {str(e)}", "Error"

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

        try:
            stream = self.groq_call(messages, temperature=0.2, max_tokens=512, stream=True)
            full_answer = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_answer += delta
                yield delta
            self.chat_history.append({"role": "assistant", "content": full_answer})
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            yield error_msg

    def answer_image(self, query, image_base64, language="English"):
        self.chat_history.append({"role": "user", "content": query})
        try:
            response = self.groq.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
                        {"type": "text", "text": f"Answer in {language}. {query}"}
                    ]
                }],
                temperature=0.2,
                max_tokens=512
            )
            answer = response.choices[0].message.content
            self.chat_history.append({"role": "assistant", "content": answer})
            return answer
        except Exception as e:
            return f"Image analysis error: {str(e)}"

    def generate_image(self, prompt):
        try:
            import urllib.parse
            import base64
            encoded = urllib.parse.quote(prompt)
            image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=512&nologo=true"
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                b64 = base64.b64encode(response.content).decode("utf-8")
                return b64, None
            return None, "Image generation failed"
        except Exception as e:
            return None, str(e)

    def solve_math(self, problem, language="English"):
        system_prompt = f"""You are an expert math tutor.
Solve the math problem step by step in {language}.
Show every step clearly with explanation.
Use proper mathematical notation.
At the end give the final answer clearly."""

        self.chat_history.append({"role": "user", "content": problem})
        messages = [{"role": "system", "content": system_prompt}]
        messages += self.chat_history

        try:
            stream = self.groq_call(messages, temperature=0.1, max_tokens=1024, stream=True)
            full_answer = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_answer += delta
                yield delta
            self.chat_history.append({"role": "assistant", "content": full_answer})
        except Exception as e:
            yield f"Error: {str(e)}"

    def answer_code(self, query, language="English"):
        system_prompt = f"""You are an expert programmer like ChatGPT Code Interpreter.
Answer in {language}.
Always provide:
1. Clear explanation of the code
2. Complete working code with comments in a python code block
3. Example output if applicable
4. Any important notes or edge cases
Format code properly in markdown code blocks."""

        self.chat_history.append({"role": "user", "content": query})
        messages = [{"role": "system", "content": system_prompt}]
        messages += self.chat_history

        try:
            stream = self.groq_call(messages, temperature=0.2, max_tokens=1024, stream=True)
            full_answer = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_answer += delta
                yield delta
            self.chat_history.append({"role": "assistant", "content": full_answer})
        except Exception as e:
            yield f"Error: {str(e)}"

    def research_assistant(self, topic, language="English"):
        wiki_text, _, _ = self.search_wikipedia(topic)
        wiki_context = wiki_text[:3000] if wiki_text else ""

        system_prompt = f"""You are an expert research assistant.
Generate a comprehensive well structured research report in {language}.
Always include these sections:
1. Executive Summary
2. Background and History
3. Key Concepts and Definitions
4. Current State and Recent Developments
5. Applications and Use Cases
6. Challenges and Limitations
7. Future Outlook
8. Key Takeaways
9. References and Further Reading

Use markdown formatting with headers bullet points and bold text."""

        user_prompt = f"""Generate a full research report on: {topic}

Background context:
{wiki_context}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            stream = self.groq_call(messages, temperature=0.3, max_tokens=2048, stream=True)
            full_answer = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_answer += delta
                yield delta
            self.chat_history.append({"role": "user", "content": f"Research on {topic}"})
            self.chat_history.append({"role": "assistant", "content": full_answer})
        except Exception as e:
            yield f"Error: {str(e)}"

    def learning_path_generator(self, skill, level="Beginner", language="English"):
        system_prompt = f"""You are an expert learning coach.
Create a detailed week by week learning roadmap in {language}.
The person is at {level} level.
Include at least 8 weeks with topics resources projects and milestones.
Use markdown formatting."""

        user_prompt = f"""Create a complete learning roadmap for: {skill}
Student level: {level}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            stream = self.groq_call(messages, temperature=0.3, max_tokens=2048, stream=True)
            full_answer = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_answer += delta
                yield delta
        except Exception as e:
            yield f"Error: {str(e)}"

    def interview_coach_question(self, job_role, round_num, language="English"):
        system_prompt = f"""You are an expert interview coach for {job_role} positions.
Ask ONE professional interview question in {language}.
Rounds 1-2: Easy. Rounds 3-4: Medium. Rounds 5+: Hard.
Return ONLY the question."""

        try:
            response = self.groq_call(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Question #{round_num} for {job_role}"}
                ],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Could not generate question: {str(e)}"

    def interview_coach_grade(self, job_role, question, answer, language="English"):
        system_prompt = f"""You are an expert interview coach.
Grade the answer in {language}.
Provide: Score X/10, What You Did Well, What Could Be Better, Model Answer, Tips."""

        user_prompt = f"""Role: {job_role}
Question: {question}
Answer: {answer}"""

        try:
            stream = self.groq_call(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=800,
                stream=True
            )
            full_answer = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_answer += delta
                yield delta
        except Exception as e:
            yield f"Error: {str(e)}"

    def generate_flashcards(self, topic, num_cards=10, language="English"):
        wiki_text, _, _ = self.search_wikipedia(topic)
        context = wiki_text[:3000] if wiki_text else ""

        system_prompt = f"""Create exactly {num_cards} flashcards in {language}.
Format:
CARD 1
Q: [Question]
A: [Answer]

CARD 2
..."""

        try:
            stream = self.groq_call(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Flashcards for: {topic}\nContext: {context}"}
                ],
                temperature=0.3,
                max_tokens=2048,
                stream=True
            )
            full_answer = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_answer += delta
                yield delta
        except Exception as e:
            yield f"Error: {str(e)}"

    def generate_quiz(self, topic, num_questions=5, language="English"):
        wiki_text, _, _ = self.search_wikipedia(topic)
        context = wiki_text[:3000] if wiki_text else ""

        system_prompt = f"""Create exactly {num_questions} MCQ questions in {language}.
Format:
Q1: [Question]
A) B) C) D)
ANSWER: [Letter]
EXPLANATION: [Why]
---"""

        try:
            stream = self.groq_call(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Quiz on: {topic}\nContext: {context}"}
                ],
                temperature=0.4,
                max_tokens=2048,
                stream=True
            )
            full_answer = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_answer += delta
                yield delta
        except Exception as e:
            yield f"Error: {str(e)}"

    def text_to_sql(self, description, schema="", language="English"):
        system_prompt = f"""You are an expert SQL developer.
Convert natural language to SQL in {language}.
Provide: SQL query, explanation, assumptions, alternatives."""

        user_prompt = f"""Description: {description}
{f"Schema: {schema}" if schema else ""}"""

        self.chat_history.append({"role": "user", "content": description})
        try:
            stream = self.groq_call(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=1024,
                stream=True
            )
            full_answer = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_answer += delta
                yield delta
            self.chat_history.append({"role": "assistant", "content": full_answer})
        except Exception as e:
            yield f"Error: {str(e)}"

    def generate_diagram(self, description, language="English"):
        system_prompt = f"""Create a clear ASCII text diagram in {language}.
Use box characters and arrows.
Also provide component descriptions and interactions."""

        self.chat_history.append({"role": "user", "content": description})
        try:
            stream = self.groq_call(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Diagram for: {description}"}
                ],
                temperature=0.2,
                max_tokens=1024,
                stream=True
            )
            full_answer = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_answer += delta
                yield delta
            self.chat_history.append({"role": "assistant", "content": full_answer})
        except Exception as e:
            yield f"Error: {str(e)}"

    def write_email(self, situation, tone="Professional", language="English"):
        system_prompt = f"""Write a {tone} email in {language}.
Provide: Subject line, full email body, alternative subject, tips."""

        self.chat_history.append({"role": "user", "content": situation})
        try:
            stream = self.groq_call(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Write email for: {situation}"}
                ],
                temperature=0.4,
                max_tokens=1024,
                stream=True
            )
            full_answer = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_answer += delta
                yield delta
            self.chat_history.append({"role": "assistant", "content": full_answer})
        except Exception as e:
            yield f"Error: {str(e)}"

    def generate_cover_letter(self, job_description, skills, language="English"):
        system_prompt = f"""Write a compelling cover letter in {language}.
Match skills to requirements. Be professional and personal."""

        try:
            stream = self.groq_call(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Job:\n{job_description}\n\nSkills:\n{skills}"}
                ],
                temperature=0.4,
                max_tokens=1024,
                stream=True
            )
            full_answer = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_answer += delta
                yield delta
        except Exception as e:
            yield f"Error: {str(e)}"

    def grammar_checker(self, text, language="English"):
        system_prompt = f"""Check grammar in {language}.
Provide: Corrected version, errors found, writing tips, score X/10."""

        try:
            stream = self.groq_call(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Check: {text}"}
                ],
                temperature=0.1,
                max_tokens=1024,
                stream=True
            )
            full_answer = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_answer += delta
                yield delta
        except Exception as e:
            yield f"Error: {str(e)}"

    def tone_changer(self, text, target_tone, language="English"):
        system_prompt = f"""Rewrite in {target_tone} tone in {language}.
Provide: Rewritten version, key changes, why it works, alternatives."""

        try:
            stream = self.groq_call(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Rewrite in {target_tone}: {text}"}
                ],
                temperature=0.5,
                max_tokens=1024,
                stream=True
            )
            full_answer = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_answer += delta
                yield delta
        except Exception as e:
            yield f"Error: {str(e)}"

    def mind_map(self, topic, language="English"):
        wiki_text, _, _ = self.search_wikipedia(topic)
        context = wiki_text[:2000] if wiki_text else ""

        system_prompt = f"""Create a detailed text mind map in {language}.
Use tree structure with + and | characters.
Include 5+ main branches with 3+ sub-topics each."""

        try:
            stream = self.groq_call(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Mind map for: {topic}\nContext: {context}"}
                ],
                temperature=0.3,
                max_tokens=2048,
                stream=True
            )
            full_answer = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_answer += delta
                yield delta
        except Exception as e:
            yield f"Error: {str(e)}"

    def action_plan(self, goal, timeframe="30 days", language="English"):
        system_prompt = f"""Create a detailed action plan in {language} for {timeframe}.
Include: Goal analysis, weekly breakdown, success tips, accountability system."""

        self.chat_history.append({"role": "user", "content": goal})
        try:
            stream = self.groq_call(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Goal: {goal}\nTimeframe: {timeframe}"}
                ],
                temperature=0.3,
                max_tokens=2048,
                stream=True
            )
            full_answer = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_answer += delta
                yield delta
            self.chat_history.append({"role": "assistant", "content": full_answer})
        except Exception as e:
            yield f"Error: {str(e)}"

    def debate_mode(self, topic, language="English"):
        system_prompt = f"""Debate both sides thoroughly in {language}.
Format: FOR arguments, AGAINST arguments, VERDICT, KEY INSIGHT."""

        self.chat_history.append({"role": "user", "content": topic})
        try:
            stream = self.groq_call(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Debate: {topic}"}
                ],
                temperature=0.4,
                max_tokens=2048,
                stream=True
            )
            full_answer = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_answer += delta
                yield delta
            self.chat_history.append({"role": "assistant", "content": full_answer})
        except Exception as e:
            yield f"Error: {str(e)}"

    def answer_stream(self, query, language="English"):
        self.chat_history.append({"role": "user", "content": query})

        if self.is_greeting(query):
            reply = "Hello! How can I assist you today? I can answer questions, write code, generate images, search the web, and much more!"
            self.chat_history.append({"role": "assistant", "content": reply})
            yield reply, "Llama 3", [], None, []
            return

        system_prompt = f"""You are a helpful friendly assistant like ChatGPT.
Answer in {language}. Be direct clear and helpful.
Use bullet points when appropriate."""

        try:
            wiki_text, wiki_title, wiki_url = self.search_wikipedia(query)
        except Exception as e:
            wiki_text, wiki_title, wiki_url = None, None, None

        if not wiki_text:
            messages = [{"role": "system", "content": system_prompt}]
            messages += self.chat_history

            try:
                stream = self.groq_call(messages, temperature=0.3, max_tokens=512, stream=True)
                full_answer = ""
                for chunk in stream:
                    delta = chunk.choices[0].delta.content or ""
                    full_answer += delta
                    yield delta, None, None, None, []

                self.chat_history.append({"role": "assistant", "content": full_answer})
                followups = self.get_followup_questions(query, full_answer)
                confidence = self.get_confidence(query, full_answer, "")
                yield "", "Llama 3", followups, confidence, []
            except Exception as e:
                yield f"Error: {str(e)}", "Error", [], 0, []
            return

        index, chunks = self.build_dynamic_index(wiki_text)
        if not chunks:
            yield "Could not find relevant information.", wiki_title, [], 0, []
            return

        retrieved = self.retrieve_with_scores(query, index, chunks)
        context = "\n\n".join([r["text"] for r in retrieved])

        user_message = f"""Information:
{context}

Question: {query}"""

        messages = [{"role": "system", "content": system_prompt}]
        if len(self.chat_history) > 1:
            messages += self.chat_history[:-1]
        messages.append({"role": "user", "content": user_message})

        try:
            stream = self.groq_call(messages, temperature=0.2, max_tokens=512, stream=True)
            full_answer = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_answer += delta
                yield delta, None, None, None, []

            self.chat_history.append({"role": "assistant", "content": full_answer})
            followups = self.get_followup_questions(query, full_answer)
            confidence = self.get_confidence(query, full_answer, context)

            citations = []
            for i, r in enumerate(retrieved):
                citations.append({
                    "chunk_num": i + 1,
                    "text": r["text"][:200] + "...",
                    "relevance": r["score"],
                    "source": wiki_title,
                    "url": wiki_url
                })

            yield "", f"Wikipedia: {wiki_title}", followups, confidence, citations
        except Exception as e:
            yield f"Error: {str(e)}", "Error", [], 0, []
    def answer_pdf_with_citations(self, query, chunks_with_pages, index, embed_model, language="English"):
        from media_handler import retrieve_with_pages
        retrieved = retrieve_with_pages(query, index, chunks_with_pages, embed_model)

        if not retrieved:
            yield "Could not find relevant content in the PDF."
            return

        context = "\n\n".join([
            f"[Page {r['page']}]: {r['text']}"
            for r in retrieved
        ])

        system_prompt = f"""You are a helpful document assistant in {language}.
Answer questions based ONLY on the PDF content provided.
ALWAYS cite the exact page number like (Page X) after each fact.
Be direct and specific.
If information spans multiple pages mention all relevant pages."""

        user_prompt = f"""PDF Content:
{context}

Question: {query}

Answer with page citations:"""

        self.chat_history.append({"role": "user", "content": query})
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            stream = self.groq_call(messages, temperature=0.2, max_tokens=512, stream=True)
            full_answer = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_answer += delta
                yield delta

            self.chat_history.append({"role": "assistant", "content": full_answer})

            citations = [
                {"page": r["page"], "text": r["text"][:150], "score": r["score"]}
                for r in retrieved
            ]
            yield "\n\n__CITATIONS__" + str(citations)

        except Exception as e:
            yield f"Error: {str(e)}"

    def personal_tutor(self, topic, level="Beginner", language="English"):
        wiki_text, _, _ = self.search_wikipedia(topic)
        context = wiki_text[:2000] if wiki_text else ""

        system_prompt = f"""You are an expert personal tutor in {language}.
Teach the topic step by step for a {level} student.

Always structure your lesson like this:

## Lesson: [Topic]

### What You Will Learn
[Clear learning objectives]

### Step 1: Introduction
[Simple explanation with real world analogy]

### Step 2: Core Concept
[Main concept explained simply with example]

### Step 3: How It Works
[Detailed explanation with examples]

### Step 4: Practice Example
[Worked example the student can follow]

### Quick Quiz
Q1: [Simple question]
Q2: [Medium question]
Q3: [Harder question]
Answers at the bottom

### Key Takeaways
[3-5 bullet points]

### Next Steps
[What to learn next]

### Quiz Answers
[Answers to quiz questions]

Be encouraging friendly and clear."""

        user_prompt = f"""Teach me about: {topic}
My level: {level}
Context: {context}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            stream = self.groq_call(messages, temperature=0.3, max_tokens=2048, stream=True)
            full_answer = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_answer += delta
                yield delta

            self.chat_history.append({"role": "user", "content": f"Teach me {topic}"})
            self.chat_history.append({"role": "assistant", "content": full_answer})

        except Exception as e:
            yield f"Error: {str(e)}"

    def tutor_followup(self, question, topic, language="English"):
        system_prompt = f"""You are a helpful personal tutor teaching {topic} in {language}.
Answer the student's follow up question clearly.
Use simple examples and encourage the student.
If they got a quiz answer wrong explain why kindly."""

        self.chat_history.append({"role": "user", "content": question})
        messages = [{"role": "system", "content": system_prompt}]
        messages += self.chat_history

        try:
            stream = self.groq_call(messages, temperature=0.3, max_tokens=512, stream=True)
            full_answer = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_answer += delta
                yield delta

            self.chat_history.append({"role": "assistant", "content": full_answer})

        except Exception as e:
            yield f"Error: {str(e)}"

    def analyze_resume(self, resume_text, job_role="", language="English"):
        system_prompt = f"""You are an expert career coach and resume analyst in {language}.
Analyze the resume thoroughly and provide detailed professional feedback.

Always structure your analysis like this:

## Resume Score: X/10

## Strengths
[What is done well]

## Weaknesses
[What needs improvement]

## Section by Section Analysis

### Contact Information
### Summary/Objective
### Work Experience
### Education
### Skills
### Overall Formatting

## Top 5 Improvements
1.
2.
3.
4.
5.

## ATS Score: X/10
[How well it will pass Applicant Tracking Systems]

## Best Job Roles for This Resume
[Suggest 3-5 matching roles]

{f"## Fit for {job_role}: X/10" if job_role else ""}
{f"[How well this resume fits {job_role} and what to add]" if job_role else ""}

Be honest specific and actionable."""

        user_prompt = f"""Analyze this resume:

{resume_text[:4000]}

{f"Target role: {job_role}" if job_role else ""}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            stream = self.groq_call(messages, temperature=0.2, max_tokens=2048, stream=True)
            full_answer = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_answer += delta
                yield delta

        except Exception as e:
            yield f"Error: {str(e)}"


    def clear_history(self):
        self.chat_history = []