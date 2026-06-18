import faiss
import numpy as np
import os
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
Return ONLY 3 questions, one per line, no numbering, no extra text.

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

    def web_search_answer(self, query, search_results, language="English"):
        print(f"DEBUG: Query = {query}")
        print(f"DEBUG: Number of results received = {len(search_results)}")

        if not search_results:
            yield "I searched the web but found no results. Please check your SERPER_API_KEY in the .env file."
            return

        context_parts = []
        for i, r in enumerate(search_results):
            part = f"Result {i+1}:\nTitle: {r['title']}\nContent: {r['snippet']}"
            if r.get('url'):
                part += f"\nSource: {r['url']}"
            context_parts.append(part)
        context = "\n\n---\n\n".join(context_parts)

        system_prompt = f"""You are a helpful web search assistant.
You have been given live Google search results.
Answer the question in {language} using these results.
Be direct and specific.
Do NOT mention knowledge cutoffs.
Do NOT say results are not found.
Quote specific facts from the results."""

        user_prompt = f"""Live search results for "{query}":

{context}

Answer this question using the above results: {query}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        stream = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.0,
            max_tokens=512,
            stream=True
        )

        full_answer = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_answer += delta
            yield delta

        self.chat_history.append({"role": "user", "content": query})
        self.chat_history.append({"role": "assistant", "content": full_answer})

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

        stream = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
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

    def answer_code(self, query, language="English"):
        system_prompt = f"""You are an expert programmer like ChatGPT Code Interpreter.
Answer in {language}.
Always provide:
1. Clear explanation of the code
2. Complete working code with comments
3. Example output if applicable
4. Any important notes or edge cases
Format code properly in markdown code blocks."""

        self.chat_history.append({"role": "user", "content": query})
        messages = [{"role": "system", "content": system_prompt}]
        messages += self.chat_history

        stream = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
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

    def research_assistant(self, topic, language="English"):
        wiki_text, _ = self.search_wikipedia(topic)
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

Use markdown formatting with headers bullet points and bold text.
Be thorough accurate and professional."""

        user_prompt = f"""Generate a full research report on: {topic}

Background context:
{wiki_context}

Create a comprehensive detailed research report with all sections."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        stream = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
            max_tokens=2048,
            stream=True
        )

        full_answer = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_answer += delta
            yield delta

        self.chat_history.append({"role": "user", "content": f"Research report on {topic}"})
        self.chat_history.append({"role": "assistant", "content": full_answer})

    def learning_path_generator(self, skill, level="Beginner", language="English"):
        system_prompt = f"""You are an expert learning coach and curriculum designer.
Create a detailed week by week learning roadmap in {language}.
The person is at {level} level.

Structure the roadmap like this:
- Overview
- Prerequisites
- Week by week plan (at least 8 weeks)
  For each week include:
  * Week number and theme
  * Topics to study
  * Specific resources
  * Hands on projects
  * Goals and milestones
- Final project idea
- Career opportunities
- Tips for success

Use markdown formatting. Be specific with real resources."""

        user_prompt = f"""Create a complete week by week learning roadmap for: {skill}
Student level: {level}
Make it detailed practical and achievable."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        stream = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
            max_tokens=2048,
            stream=True
        )

        full_answer = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_answer += delta
            yield delta

        self.chat_history.append({"role": "user", "content": f"Learning path for {skill}"})
        self.chat_history.append({"role": "assistant", "content": full_answer})

    def interview_coach_question(self, job_role, round_num, language="English"):
        system_prompt = f"""You are an expert interview coach for {job_role} positions.
Ask ONE professional interview question at a time in {language}.
For round {round_num}:
- Rounds 1-2: Easy warmup questions
- Rounds 3-4: Medium technical questions
- Rounds 5-6: Hard problem solving questions
- Round 7+: Advanced scenario questions

Return ONLY the question, nothing else."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Ask interview question #{round_num} for {job_role} role."}
        ]

        response = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()

    def interview_coach_grade(self, job_role, question, answer, language="English"):
        system_prompt = f"""You are an expert interview coach for {job_role} positions.
Grade the candidate answer in {language}.

Always provide:
## Score: X/10
## What You Did Well
## What Could Be Better
## Model Answer
## Tips for Next Time

Be honest constructive and specific."""

        user_prompt = f"""Job Role: {job_role}
Question: {question}
Candidate Answer: {answer}

Grade this answer."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        stream = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.2,
            max_tokens=800,
            stream=True
        )

        full_answer = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_answer += delta
            yield delta

        self.chat_history.append({"role": "assistant", "content": full_answer})

    def generate_flashcards(self, topic, num_cards=10, language="English"):
        wiki_text, _ = self.search_wikipedia(topic)
        context = wiki_text[:3000] if wiki_text else ""

        system_prompt = f"""You are an expert educator.
Create exactly {num_cards} flashcards in {language} for the topic provided.
Format EXACTLY like this for each card:

CARD 1
Q: [Question]
A: [Answer]

CARD 2
Q: [Question]
A: [Answer]

Make questions clear and answers concise but complete."""

        user_prompt = f"""Create {num_cards} flashcards for: {topic}

Context: {context}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        stream = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
            max_tokens=2048,
            stream=True
        )

        full_answer = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_answer += delta
            yield delta

        self.chat_history.append({"role": "user", "content": f"Flashcards on {topic}"})
        self.chat_history.append({"role": "assistant", "content": full_answer})

    def generate_quiz(self, topic, num_questions=5, language="English"):
        wiki_text, _ = self.search_wikipedia(topic)
        context = wiki_text[:3000] if wiki_text else ""

        system_prompt = f"""You are an expert quiz creator.
Create exactly {num_questions} multiple choice questions in {language}.
Format EXACTLY like this:

Q1: [Question]
A) [Option]
B) [Option]
C) [Option]
D) [Option]
ANSWER: [Correct letter]
EXPLANATION: [Why this is correct]

---

Q2: [Question]
...

Make questions challenging but fair."""

        user_prompt = f"""Create a {num_questions} question MCQ quiz on: {topic}

Context: {context}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        stream = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.4,
            max_tokens=2048,
            stream=True
        )

        full_answer = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_answer += delta
            yield delta

    def text_to_sql(self, description, schema="", language="English"):
        system_prompt = f"""You are an expert SQL developer.
Convert natural language descriptions to SQL queries.
Always provide:
1. The SQL query properly formatted
2. Explanation of what the query does
3. Any assumptions made
4. Alternative versions if applicable

Use standard SQL that works with MySQL PostgreSQL and SQLite."""

        user_prompt = f"""Convert this to SQL in {language}:

Description: {description}
{f"Database Schema: {schema}" if schema else ""}

Provide the SQL query with full explanation."""

        self.chat_history.append({"role": "user", "content": description})
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        stream = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
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

    def generate_diagram(self, description, language="English"):
        system_prompt = f"""You are an expert system architect.
Create a clear text based diagram in {language} for the described system.
Use ASCII art and text symbols:
- Flow diagrams using arrows
- Box diagrams using box characters
- Tree structures using tree characters

Also provide:
1. The diagram
2. Component descriptions
3. How components interact
4. Key design decisions"""

        user_prompt = f"""Create a detailed diagram for: {description}"""

        self.chat_history.append({"role": "user", "content": description})
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        stream = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
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

    def write_email(self, situation, tone="Professional", language="English"):
        system_prompt = f"""You are an expert email writer.
Write a {tone} email in {language} based on the situation described.
Always provide:
1. Subject line
2. Full email body
3. Alternative subject line
4. Tips for this type of email

Make the email clear concise and effective."""

        user_prompt = f"""Write a {tone} email for this situation:
{situation}"""

        self.chat_history.append({"role": "user", "content": situation})
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        stream = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
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

    def generate_cover_letter(self, job_description, skills, language="English"):
        system_prompt = f"""You are an expert career coach and cover letter writer.
Write a compelling tailored cover letter in {language}.
The letter should:
- Be professional and engaging
- Match skills to job requirements
- Show enthusiasm and fit
- Be 3-4 paragraphs
- Include strong opening and closing
- Feel personal not generic"""

        user_prompt = f"""Write a cover letter for this job:

Job Description:
{job_description}

My Skills and Experience:
{skills}"""

        self.chat_history.append({"role": "user", "content": "Cover letter request"})
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        stream = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
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

    def grammar_checker(self, text, language="English"):
        system_prompt = f"""You are an expert grammar and writing coach.
Check the provided text and return in {language}:

## Corrected Version
[Full corrected text]

## Errors Found
[List each error with explanation]

## Writing Tips
[Specific tips to improve this text]

## Score: X/10

Be thorough and educational."""

        user_prompt = f"""Check and correct this text:

{text}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        stream = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.1,
            max_tokens=1024,
            stream=True
        )

        full_answer = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_answer += delta
            yield delta

    def tone_changer(self, text, target_tone, language="English"):
        system_prompt = f"""You are an expert writing coach.
Rewrite the provided text in a {target_tone} tone in {language}.
Always provide:
1. Rewritten version in {target_tone} tone
2. Key changes made
3. Why these changes create the {target_tone} tone
4. Additional tone variations if helpful"""

        user_prompt = f"""Rewrite this text in a {target_tone} tone:

{text}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        stream = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.5,
            max_tokens=1024,
            stream=True
        )

        full_answer = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_answer += delta
            yield delta

    def mind_map(self, topic, language="English"):
        wiki_text, _ = self.search_wikipedia(topic)
        context = wiki_text[:2000] if wiki_text else ""

        system_prompt = f"""You are an expert at creating mind maps.
Create a detailed text based mind map in {language} using this format:

CENTRAL TOPIC
|
+-- Main Branch 1
|   +-- Sub-topic 1.1
|   +-- Sub-topic 1.2
|   +-- Sub-topic 1.3
|
+-- Main Branch 2
|   +-- Sub-topic 2.1
|   +-- Sub-topic 2.2
|
+-- Main Branch 3
    +-- Sub-topic 3.1
    +-- Sub-topic 3.2

Include at least 5 main branches with 3 or more sub-topics each.
After the mind map add a brief summary of key connections."""

        user_prompt = f"""Create a detailed mind map for: {topic}

Context: {context}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        stream = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
            max_tokens=2048,
            stream=True
        )

        full_answer = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_answer += delta
            yield delta

    def action_plan(self, goal, timeframe="30 days", language="English"):
        system_prompt = f"""You are an expert life and productivity coach.
Create a detailed action plan in {language} to achieve the goal in {timeframe}.

Always include:
## Goal Analysis
## Action Plan
## Week by Week Breakdown
## Success Tips
## Accountability System

Be specific and actionable."""

        user_prompt = f"""Create a complete action plan for:
Goal: {goal}
Timeframe: {timeframe}"""

        self.chat_history.append({"role": "user", "content": goal})
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        stream = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
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

    def debate_mode(self, topic, language="English"):
        system_prompt = f"""You are an expert debate coach.
Argue BOTH sides of the topic thoroughly in {language}.

Format exactly like this:

## FOR: {topic}
1. [Strong argument with evidence]
2. [Strong argument with evidence]
3. [Strong argument with evidence]
4. [Strong argument with evidence]
5. [Strong argument with evidence]

## AGAINST: {topic}
1. [Strong counter argument with evidence]
2. [Strong counter argument with evidence]
3. [Strong counter argument with evidence]
4. [Strong counter argument with evidence]
5. [Strong counter argument with evidence]

## VERDICT
[Balanced conclusion]

## KEY INSIGHT
[Most important thing to understand about this debate]"""

        user_prompt = f"""Debate both sides of: {topic}"""

        self.chat_history.append({"role": "user", "content": topic})
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        stream = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
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

    def answer_stream(self, query, language="English"):
        self.chat_history.append({"role": "user", "content": query})

        if self.is_greeting(query):
            reply = "Hello! How can I assist you today? I can answer any question, solve math, write code, generate images, search the web, chat with PDFs and much more!"
            self.chat_history.append({"role": "assistant", "content": reply})
            yield reply, "Llama 3", [], None
            return

        system_prompt = f"""You are a helpful friendly assistant like ChatGPT.
Answer in {language}. Be direct clear and helpful.
Use bullet points or numbered lists when appropriate.
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
            followups = self.get_followup_questions(query, full_answer)
            confidence = self.get_confidence(query, full_answer, "")
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