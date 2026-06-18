import streamlit as st
from rag_pipeline import RAGChatbot
from media_handler import (
    extract_text_from_pdf,
    extract_multiple_pdfs,
    extract_youtube_transcript,
    extract_website_text,
    image_to_base64,
    build_index,
    retrieve,
    web_search
)
import datetime

st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.markdown("""
<style>
    .stApp { background-color: #ffffff; color: #1a1a1a; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    div[data-testid="stSidebar"] {
        background-color: #f7f7f8;
        border-right: 1px solid #e5e5e5;
    }
    .attachment-badge {
        background: #f0f7ff;
        border: 1px solid #b3d4ff;
        border-radius: 8px;
        padding: 6px 12px;
        font-size: 13px;
        color: #0066cc;
        display: inline-block;
        margin: 4px 0;
    }
    .upload-popup {
        background: #ffffff;
        border: 1px solid #e5e5e5;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .search-result {
        background: #f7f7f8;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 10px;
        margin: 6px 0;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_bot():
    return RAGChatbot()

bot = load_bot()

defaults = {
    "messages": [],
    "followups": [],
    "source": "",
    "confidence": None,
    "language": "English",
    "show_upload": False,
    "attachment_type": None,
    "attachment_name": "",
    "doc_index": None,
    "doc_chunks": [],
    "image_b64": None,
    "interview_role": "",
    "interview_round": 0,
    "interview_question": "",
    "interview_history": [],
    "interview_started": False,
    "interview_lang": "English"
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Sidebar
with st.sidebar:
    st.markdown("## 🤖 RAG Chatbot")
    st.markdown("*Powered by Llama 3 + Wikipedia*")
    st.markdown("---")

    st.markdown("### 🌍 Language")
    language = st.selectbox(
        "Answer in:",
        ["English", "Hindi", "Spanish", "French", "German",
         "Arabic", "Chinese", "Japanese", "Portuguese", "Telugu", "Tamil"],
        index=0
    )
    st.session_state.language = language

    st.markdown("---")
    st.markdown("### 🛠️ Mode")
    mode = st.radio(
        "Choose mode:",
        ["💬 Chat",
         "🔍 Web Search",
         "🖼️ Image Generator",
         "🧮 Math Solver",
         "💻 Code Interpreter",
         "📝 Summarize Topic",
         "📊 Research Assistant",
         "🗺️ Learning Path",
         "🎯 Interview Coach",
         "🃏 Flashcards",
         "📝 Quiz Mode",
         "🗄️ Text to SQL",
         "📐 Diagram Generator",
         "📧 Email Writer",
         "📄 Cover Letter",
         "✅ Grammar Checker",
         "🎨 Tone Changer",
         "🧠 Mind Map",
         "🎯 Action Plan",
         "⚔️ Debate Mode"],
        index=0
    )

    st.markdown("---")
    st.markdown("### ✅ Features")
    st.markdown("✅ Wikipedia Q&A")
    st.markdown("✅ Web search")
    st.markdown("✅ PDF chat multi")
    st.markdown("✅ Image understanding")
    st.markdown("✅ Image generation")
    st.markdown("✅ YouTube Q&A")
    st.markdown("✅ Website chat")
    st.markdown("✅ Math solver")
    st.markdown("✅ Code interpreter")
    st.markdown("✅ Auto summarizer")
    st.markdown("✅ Research reports")
    st.markdown("✅ Learning roadmaps")
    st.markdown("✅ Interview coach")
    st.markdown("✅ Flashcard generator")
    st.markdown("✅ Quiz mode")
    st.markdown("✅ Text to SQL")
    st.markdown("✅ Diagram generator")
    st.markdown("✅ Email writer")
    st.markdown("✅ Cover letter")
    st.markdown("✅ Grammar checker")
    st.markdown("✅ Tone changer")
    st.markdown("✅ Mind map")
    st.markdown("✅ Action plan")
    st.markdown("✅ Debate mode")
    st.markdown("✅ Confidence score")
    st.markdown("✅ 11 languages")
    st.markdown("✅ Export chat")
    st.markdown("---")

    if st.session_state.messages:
        chat_export = "\n\n".join([
            f"{'You' if m['role'] == 'user' else 'Bot'}: {m['content']}"
            for m in st.session_state.messages
        ])
        st.download_button(
            label="📥 Export Chat",
            data=chat_export,
            file_name=f"chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    if st.button("🗑️ Clear Chat", use_container_width=True):
        for k in ["messages", "followups", "doc_chunks", "interview_history"]:
            st.session_state[k] = []
        for k in ["attachment_type", "doc_index", "image_b64"]:
            st.session_state[k] = None
        st.session_state.attachment_name = ""
        st.session_state.source = ""
        st.session_state.confidence = None
        st.session_state.show_upload = False
        st.session_state.interview_started = False
        st.session_state.interview_round = 0
        st.session_state.interview_question = ""
        bot.clear_history()
        st.rerun()

# ── WEB SEARCH MODE ───────────────────────────────────────────
if "Web Search" in mode:
    st.markdown("## 🔍 Web Search")
    st.markdown("Search the live internet like Perplexity AI.")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("search_results"):
                with st.expander("🔍 Search Results"):
                    for r in msg["search_results"]:
                        st.markdown(
                            f'<div class="search-result"><b>{r["title"]}</b><br>{r["snippet"]}<br><a href="{r["url"]}" target="_blank">🔗 Source</a></div>',
                            unsafe_allow_html=True
                        )
            st.markdown(msg["content"])

    prompt = st.chat_input("Search anything...")
    if prompt:
        with st.spinner("Searching the web..."):
            results = web_search(prompt)

        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "search_results": None
        })

        system_prompt = f"""You are a helpful web search assistant.
You have LIVE Google search results right now.
Answer in {st.session_state.language} using these results.
Be direct and specific. Never say knowledge cutoff.
Never say no results found. Use the results provided."""

        if results:
            context = "\n\n".join([
                f"Result {i+1}:\nTitle: {r['title']}\nInfo: {r['snippet']}\nURL: {r['url']}"
                for i, r in enumerate(results)
            ])
        else:
            context = "No results found."

        user_prompt = f"""Live search results for "{prompt}":

{context}

Answer directly: {prompt}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = bot.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.0,
            max_tokens=512
        )
        full_response = response.choices[0].message.content

        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response,
            "search_results": results
        })
        st.rerun()

# ── IMAGE GENERATOR MODE ──────────────────────────────────────
elif "Image Generator" in mode:
    st.markdown("## 🖼️ Image Generator")
    st.markdown("Generate images from text prompts.")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("generated_image"):
                st.image(
                    f"data:image/jpeg;base64,{msg['generated_image']}",
                    caption=msg["content"]
                )
            else:
                st.markdown(msg["content"])

    prompt = st.chat_input("Describe the image you want...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Generating image... (takes 10-20 seconds)"):
                img_b64, error = bot.generate_image(prompt)

            if error:
                st.error(f"❌ {error}")
                full_response = f"Failed to generate image: {error}"
            else:
                st.image(f"data:image/jpeg;base64,{img_b64}", caption=prompt)
                full_response = f"Here is your generated image for: **{prompt}**"
                st.markdown(full_response)

        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response,
            "generated_image": img_b64 if not error else None
        })
        st.rerun()

# ── MATH SOLVER MODE ──────────────────────────────────────────
elif "Math Solver" in mode:
    st.markdown("## 🧮 Math Solver")
    st.markdown("Solve any math problem step by step.")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Enter your math problem...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            for delta in bot.solve_math(prompt, st.session_state.language):
                full_response += delta
                response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()

# ── CODE INTERPRETER MODE ─────────────────────────────────────
elif "Code Interpreter" in mode:
    st.markdown("## 💻 Code Interpreter")
    st.markdown("Write, explain and debug code in any language.")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask a coding question...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            for delta in bot.answer_code(prompt, st.session_state.language):
                full_response += delta
                response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()

# ── SUMMARIZE MODE ────────────────────────────────────────────
elif "Summarize" in mode:
    st.markdown("## 📝 Topic Summarizer")
    topic_input = st.text_input("Enter topic:", placeholder="e.g. Quantum computing, DNA...")
    if st.button("📝 Summarize", use_container_width=True):
        if topic_input.strip():
            with st.spinner(f"Summarizing {topic_input}..."):
                summary, source = bot.summarize_topic(topic_input, st.session_state.language)
            st.markdown(f"### 📖 {source}")
            st.markdown(summary)
            st.download_button("📥 Download Summary", data=summary,
                file_name=f"summary_{topic_input.replace(' ','_')}.txt", mime="text/plain")
        else:
            st.warning("Please enter a topic.")

# ── RESEARCH ASSISTANT MODE ───────────────────────────────────
elif "Research Assistant" in mode:
    st.markdown("## 📊 Research Assistant")
    st.markdown("Generate a full structured research report on any topic.")

    col1, col2 = st.columns([3, 1])
    with col1:
        topic_input = st.text_input("Research topic:", placeholder="e.g. Artificial Intelligence...")
    with col2:
        lang = st.selectbox("Language", ["English", "Hindi", "Spanish", "French"], key="res_lang")

    if st.button("📊 Generate Research Report", use_container_width=True):
        if topic_input.strip():
            st.markdown(f"## 📄 Research Report: {topic_input}")
            response_placeholder = st.empty()
            full_report = ""
            with st.spinner(f"Researching {topic_input}... (30-60 seconds)"):
                for delta in bot.research_assistant(topic_input, lang):
                    full_report += delta
                    response_placeholder.markdown(full_report + "▌")
            response_placeholder.markdown(full_report)
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("📥 Download TXT", data=full_report,
                    file_name=f"research_{topic_input.replace(' ','_')}.txt", mime="text/plain", use_container_width=True)
            with col2:
                st.download_button("📥 Download MD", data=full_report,
                    file_name=f"research_{topic_input.replace(' ','_')}.md", mime="text/markdown", use_container_width=True)
        else:
            st.warning("Please enter a research topic.")

# ── LEARNING PATH MODE ────────────────────────────────────────
elif "Learning Path" in mode:
    st.markdown("## 🗺️ Learning Path Generator")
    st.markdown("Get a personalised week by week roadmap for any skill.")

    col1, col2, col3 = st.columns(3)
    with col1:
        skill_input = st.text_input("Skill to learn:", placeholder="e.g. Python, Guitar...")
    with col2:
        level = st.selectbox("Your level:", ["Complete Beginner", "Beginner", "Intermediate", "Advanced"])
    with col3:
        lang = st.selectbox("Language", ["English", "Hindi", "Spanish", "French"], key="lp_lang")

    if st.button("🗺️ Generate Learning Path", use_container_width=True):
        if skill_input.strip():
            st.markdown(f"## 🗺️ Learning Roadmap: {skill_input}")
            response_placeholder = st.empty()
            full_path = ""
            with st.spinner(f"Creating learning path for {skill_input}..."):
                for delta in bot.learning_path_generator(skill_input, level, lang):
                    full_path += delta
                    response_placeholder.markdown(full_path + "▌")
            response_placeholder.markdown(full_path)
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("📥 Download TXT", data=full_path,
                    file_name=f"learning_path_{skill_input.replace(' ','_')}.txt", mime="text/plain", use_container_width=True)
            with col2:
                st.download_button("📥 Download MD", data=full_path,
                    file_name=f"learning_path_{skill_input.replace(' ','_')}.md", mime="text/markdown", use_container_width=True)
        else:
            st.warning("Please enter a skill.")

# ── INTERVIEW COACH MODE ──────────────────────────────────────
elif "Interview Coach" in mode:
    st.markdown("## 🎯 Interview Coach")
    st.markdown("Practice real interview questions and get graded.")

    if not st.session_state.interview_started:
        st.markdown("### Setup Your Interview")
        col1, col2 = st.columns(2)
        with col1:
            role_input = st.text_input("Job role:", placeholder="e.g. Python Developer, Data Scientist...")
        with col2:
            lang = st.selectbox("Language", ["English", "Hindi", "Spanish", "French"], key="ic_lang")

        if st.button("🎯 Start Interview", use_container_width=True):
            if role_input.strip():
                st.session_state.interview_role = role_input
                st.session_state.interview_round = 1
                st.session_state.interview_history = []
                st.session_state.interview_started = True
                st.session_state.interview_lang = lang
                with st.spinner("Preparing first question..."):
                    question = bot.interview_coach_question(role_input, 1, lang)
                st.session_state.interview_question = question
                st.rerun()
            else:
                st.warning("Please enter a job role.")
    else:
        role = st.session_state.interview_role
        round_num = st.session_state.interview_round
        lang = st.session_state.get("interview_lang", "English")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Role", role)
        with col2:
            st.metric("Round", round_num)
        with col3:
            st.metric("Done", round_num - 1)

        st.markdown("---")

        for item in st.session_state.interview_history:
            with st.expander(f"Round {item['round']}: {item['question'][:50]}..."):
                st.markdown(f"**Question:** {item['question']}")
                st.markdown(f"**Your Answer:** {item['answer']}")
                st.markdown("**Feedback:**")
                st.markdown(item['feedback'])

        if st.session_state.interview_question:
            st.markdown(f"### Question {round_num}:")
            st.info(st.session_state.interview_question)

            answer = st.text_area("Your Answer:", placeholder="Type your answer here...", height=150, key=f"ans_{round_num}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Submit Answer", use_container_width=True):
                    if answer.strip():
                        st.markdown("### Feedback:")
                        feedback_placeholder = st.empty()
                        full_feedback = ""
                        for delta in bot.interview_coach_grade(role, st.session_state.interview_question, answer, lang):
                            full_feedback += delta
                            feedback_placeholder.markdown(full_feedback + "▌")
                        feedback_placeholder.markdown(full_feedback)

                        st.session_state.interview_history.append({
                            "round": round_num,
                            "question": st.session_state.interview_question,
                            "answer": answer,
                            "feedback": full_feedback
                        })

                        st.session_state.interview_round += 1
                        with st.spinner("Next question..."):
                            next_q = bot.interview_coach_question(role, st.session_state.interview_round, lang)
                        st.session_state.interview_question = next_q
                        st.rerun()
                    else:
                        st.warning("Please type your answer.")

            with col2:
                if st.button("⏭️ Skip", use_container_width=True):
                    st.session_state.interview_round += 1
                    with st.spinner("Next question..."):
                        next_q = bot.interview_coach_question(role, st.session_state.interview_round, lang)
                    st.session_state.interview_question = next_q
                    st.rerun()

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Restart", use_container_width=True):
                st.session_state.interview_started = False
                st.session_state.interview_round = 0
                st.session_state.interview_question = ""
                st.session_state.interview_history = []
                bot.clear_history()
                st.rerun()

        with col2:
            if st.session_state.interview_history:
                report = f"Interview Report — {role}\n\n"
                for item in st.session_state.interview_history:
                    report += f"Round {item['round']}\nQ: {item['question']}\nA: {item['answer']}\nFeedback:\n{item['feedback']}\n\n{'='*50}\n\n"
                st.download_button("📥 Download Report", data=report,
                    file_name=f"interview_{role.replace(' ','_')}.txt", mime="text/plain", use_container_width=True)

# ── FLASHCARDS MODE ───────────────────────────────────────────
elif "Flashcards" in mode:
    st.markdown("## 🃏 Flashcard Generator")
    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("Topic:", placeholder="e.g. Python, World War 2...")
    with col2:
        num = st.slider("Number of cards:", 5, 20, 10)

    if st.button("🃏 Generate Flashcards", use_container_width=True):
        if topic.strip():
            response_placeholder = st.empty()
            full_text = ""
            with st.spinner("Creating flashcards..."):
                for delta in bot.generate_flashcards(topic, num, st.session_state.language):
                    full_text += delta
                    response_placeholder.markdown(full_text + "▌")
            response_placeholder.markdown(full_text)
            st.download_button("📥 Download Flashcards", data=full_text,
                file_name=f"flashcards_{topic.replace(' ','_')}.txt", mime="text/plain")
        else:
            st.warning("Please enter a topic.")

# ── QUIZ MODE ─────────────────────────────────────────────────
elif "Quiz Mode" in mode:
    st.markdown("## 📝 Quiz Generator")
    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("Quiz topic:", placeholder="e.g. Machine Learning...")
    with col2:
        num_q = st.slider("Number of questions:", 3, 10, 5)

    if st.button("📝 Generate Quiz", use_container_width=True):
        if topic.strip():
            full_quiz = ""
            placeholder = st.empty()
            with st.spinner("Generating quiz..."):
                for delta in bot.generate_quiz(topic, num_q, st.session_state.language):
                    full_quiz += delta
                    placeholder.markdown(full_quiz + "▌")
            placeholder.markdown(full_quiz)
            st.download_button("📥 Download Quiz", data=full_quiz,
                file_name=f"quiz_{topic.replace(' ','_')}.txt", mime="text/plain")
        else:
            st.warning("Please enter a topic.")

# ── TEXT TO SQL MODE ──────────────────────────────────────────
elif "Text to SQL" in mode:
    st.markdown("## 🗄️ Text to SQL")
    description = st.text_area("Describe your query:", placeholder="e.g. Get all users who signed up last 30 days...", height=100)
    schema = st.text_area("Database schema (optional):", placeholder="e.g. users(id, name, email, created_at)...", height=80)

    if st.button("🗄️ Generate SQL", use_container_width=True):
        if description.strip():
            response_placeholder = st.empty()
            full_sql = ""
            for delta in bot.text_to_sql(description, schema, st.session_state.language):
                full_sql += delta
                response_placeholder.markdown(full_sql + "▌")
            response_placeholder.markdown(full_sql)
            st.download_button("📥 Download SQL", data=full_sql, file_name="query.sql", mime="text/plain")
        else:
            st.warning("Please describe what you want.")

# ── DIAGRAM GENERATOR MODE ────────────────────────────────────
elif "Diagram Generator" in mode:
    st.markdown("## 📐 Diagram Generator")
    description = st.text_area("Describe the system:", placeholder="e.g. A RAG chatbot with embeddings, FAISS and LLM...", height=100)

    if st.button("📐 Generate Diagram", use_container_width=True):
        if description.strip():
            response_placeholder = st.empty()
            full_diagram = ""
            for delta in bot.generate_diagram(description, st.session_state.language):
                full_diagram += delta
                response_placeholder.markdown(full_diagram + "▌")
            response_placeholder.markdown(full_diagram)
            st.download_button("📥 Download Diagram", data=full_diagram, file_name="diagram.txt", mime="text/plain")
        else:
            st.warning("Please describe the system.")

# ── EMAIL WRITER MODE ─────────────────────────────────────────
elif "Email Writer" in mode:
    st.markdown("## 📧 Email Writer")
    situation = st.text_area("Describe the email situation:", placeholder="e.g. Follow up with client after 2 weeks...", height=120)
    col1, col2 = st.columns(2)
    with col1:
        tone = st.selectbox("Tone:", ["Professional", "Formal", "Friendly", "Assertive", "Apologetic", "Persuasive"])
    with col2:
        lang = st.selectbox("Language:", ["English", "Hindi", "Spanish", "French"], key="email_lang")

    if st.button("📧 Write Email", use_container_width=True):
        if situation.strip():
            response_placeholder = st.empty()
            full_email = ""
            for delta in bot.write_email(situation, tone, lang):
                full_email += delta
                response_placeholder.markdown(full_email + "▌")
            response_placeholder.markdown(full_email)
            st.download_button("📥 Download Email", data=full_email, file_name="email.txt", mime="text/plain")
        else:
            st.warning("Please describe your situation.")

# ── COVER LETTER MODE ─────────────────────────────────────────
elif "Cover Letter" in mode:
    st.markdown("## 📄 Cover Letter Generator")
    col1, col2 = st.columns(2)
    with col1:
        job_desc = st.text_area("Job Description:", placeholder="Paste the full job description here...", height=200)
    with col2:
        skills = st.text_area("Your Skills and Experience:", placeholder="e.g. 3 years Python, built RAG chatbots...", height=200)
    lang = st.selectbox("Language:", ["English", "Hindi", "Spanish", "French"], key="cl_lang")

    if st.button("📄 Generate Cover Letter", use_container_width=True):
        if job_desc.strip() and skills.strip():
            response_placeholder = st.empty()
            full_letter = ""
            for delta in bot.generate_cover_letter(job_desc, skills, lang):
                full_letter += delta
                response_placeholder.markdown(full_letter + "▌")
            response_placeholder.markdown(full_letter)
            st.download_button("📥 Download Cover Letter", data=full_letter, file_name="cover_letter.txt", mime="text/plain")
        else:
            st.warning("Please fill in both fields.")

# ── GRAMMAR CHECKER MODE ──────────────────────────────────────
elif "Grammar Checker" in mode:
    st.markdown("## ✅ Grammar Checker")
    text_input = st.text_area("Paste your text:", placeholder="Enter any text to check grammar...", height=200)

    if st.button("✅ Check Grammar", use_container_width=True):
        if text_input.strip():
            response_placeholder = st.empty()
            full_check = ""
            for delta in bot.grammar_checker(text_input, st.session_state.language):
                full_check += delta
                response_placeholder.markdown(full_check + "▌")
            response_placeholder.markdown(full_check)
            st.download_button("📥 Download Corrections", data=full_check, file_name="grammar_check.txt", mime="text/plain")
        else:
            st.warning("Please enter some text.")

# ── TONE CHANGER MODE ─────────────────────────────────────────
elif "Tone Changer" in mode:
    st.markdown("## 🎨 Tone Changer")
    text_input = st.text_area("Your text:", placeholder="Paste the text you want to rewrite...", height=150)
    col1, col2 = st.columns(2)
    with col1:
        target_tone = st.selectbox("Target tone:", ["Professional", "Casual", "Formal", "Friendly", "Funny", "Persuasive", "Empathetic", "Confident", "Simple"])
    with col2:
        lang = st.selectbox("Language:", ["English", "Hindi", "Spanish", "French"], key="tc_lang")

    if st.button("🎨 Rewrite", use_container_width=True):
        if text_input.strip():
            response_placeholder = st.empty()
            full_rewrite = ""
            for delta in bot.tone_changer(text_input, target_tone, lang):
                full_rewrite += delta
                response_placeholder.markdown(full_rewrite + "▌")
            response_placeholder.markdown(full_rewrite)
            st.download_button("📥 Download", data=full_rewrite, file_name="rewritten.txt", mime="text/plain")
        else:
            st.warning("Please enter some text.")

# ── MIND MAP MODE ─────────────────────────────────────────────
elif "Mind Map" in mode:
    st.markdown("## 🧠 Mind Map Generator")
    topic = st.text_input("Topic:", placeholder="e.g. Machine Learning, Business Strategy...")

    if st.button("🧠 Generate Mind Map", use_container_width=True):
        if topic.strip():
            response_placeholder = st.empty()
            full_map = ""
            with st.spinner("Creating mind map..."):
                for delta in bot.mind_map(topic, st.session_state.language):
                    full_map += delta
                    response_placeholder.markdown(full_map + "▌")
            response_placeholder.markdown(full_map)
            st.download_button("📥 Download Mind Map", data=full_map,
                file_name=f"mindmap_{topic.replace(' ','_')}.txt", mime="text/plain")
        else:
            st.warning("Please enter a topic.")

# ── ACTION PLAN MODE ──────────────────────────────────────────
elif "Action Plan" in mode:
    st.markdown("## 🎯 Action Plan Generator")
    goal = st.text_area("Your goal:", placeholder="e.g. Learn Python and get a developer job in 6 months...", height=100)
    col1, col2 = st.columns(2)
    with col1:
        timeframe = st.selectbox("Timeframe:", ["7 days", "30 days", "60 days", "90 days", "6 months", "1 year"])
    with col2:
        lang = st.selectbox("Language:", ["English", "Hindi", "Spanish", "French"], key="ap_lang")

    if st.button("🎯 Generate Action Plan", use_container_width=True):
        if goal.strip():
            response_placeholder = st.empty()
            full_plan = ""
            with st.spinner("Creating action plan..."):
                for delta in bot.action_plan(goal, timeframe, lang):
                    full_plan += delta
                    response_placeholder.markdown(full_plan + "▌")
            response_placeholder.markdown(full_plan)
            st.download_button("📥 Download Plan", data=full_plan, file_name="action_plan.txt", mime="text/plain")
        else:
            st.warning("Please enter your goal.")

# ── DEBATE MODE ───────────────────────────────────────────────
elif "Debate Mode" in mode:
    st.markdown("## ⚔️ Debate Mode")
    topic = st.text_input("Debate topic:", placeholder="e.g. AI will replace all jobs, Remote work is better...")

    if st.button("⚔️ Start Debate", use_container_width=True):
        if topic.strip():
            response_placeholder = st.empty()
            full_debate = ""
            with st.spinner("Preparing debate arguments..."):
                for delta in bot.debate_mode(topic, st.session_state.language):
                    full_debate += delta
                    response_placeholder.markdown(full_debate + "▌")
            response_placeholder.markdown(full_debate)
            st.download_button("📥 Download Debate", data=full_debate,
                file_name=f"debate_{topic.replace(' ','_')}.txt", mime="text/plain")
        else:
            st.warning("Please enter a debate topic.")

# ── CHAT MODE ─────────────────────────────────────────────────
else:
    st.markdown("## 💬 RAG Chatbot")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("attachment"):
                st.markdown(f'<div class="attachment-badge">📎 {msg["attachment"]}</div>', unsafe_allow_html=True)
            if msg.get("image"):
                st.image(f"data:image/jpeg;base64,{msg['image']}", width=200)
            st.markdown(msg["content"])

    if st.session_state.confidence is not None:
        score = st.session_state.confidence
        color = "green" if score >= 80 else "orange" if score >= 60 else "red"
        st.markdown(f"🎯 Confidence: :{color}[**{score}%**]")

    if st.session_state.source:
        st.caption(f"📚 {st.session_state.source}")

    if st.session_state.followups:
        st.markdown("**💡 You might also want to ask:**")
        cols = st.columns(len(st.session_state.followups))
        for i, q in enumerate(st.session_state.followups):
            if cols[i].button(q[:30] + "..." if len(q) > 30 else q, key=f"fup_{i}_{q}"):
                st.session_state.prefill_question = q
                st.rerun()

    st.markdown("---")

    if st.session_state.attachment_name:
        icon = "📄" if st.session_state.attachment_type in ["pdf", "multipdf"] \
            else "🖼️" if st.session_state.attachment_type == "image" \
            else "🌐" if st.session_state.attachment_type == "website" \
            else "▶️"
        col1, col2 = st.columns([8, 1])
        with col1:
            st.markdown(f'<div class="attachment-badge">{icon} {st.session_state.attachment_name}</div>', unsafe_allow_html=True)
        with col2:
            if st.button("✕", key="remove_att"):
                st.session_state.attachment_type = None
                st.session_state.attachment_name = ""
                st.session_state.doc_index = None
                st.session_state.doc_chunks = []
                st.session_state.image_b64 = None
                st.rerun()

    if st.session_state.show_upload:
        with st.container():
            st.markdown('<div class="upload-popup">', unsafe_allow_html=True)
            st.markdown("### 📎 Add Attachment")

            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📄 PDF", "📄📄 Multi PDF", "🖼️ Image", "▶️ YouTube", "🌐 Website"])

            with tab1:
                pdf_file = st.file_uploader("Upload PDF", type=["pdf"], key="pdf_up")
                if pdf_file:
                    with st.spinner("Reading PDF..."):
                        text = extract_text_from_pdf(pdf_file)
                        index, chunks = build_index(text, bot.embed_model)
                    st.session_state.doc_index = index
                    st.session_state.doc_chunks = chunks
                    st.session_state.attachment_type = "pdf"
                    st.session_state.attachment_name = pdf_file.name
                    st.session_state.image_b64 = None
                    st.session_state.show_upload = False
                    st.success(f"✅ {pdf_file.name} loaded!")
                    st.rerun()

            with tab2:
                pdf_files = st.file_uploader("Upload Multiple PDFs", type=["pdf"], accept_multiple_files=True, key="multi_pdf_up")
                if pdf_files and st.button("Load All PDFs", key="load_multi"):
                    with st.spinner(f"Reading {len(pdf_files)} PDFs..."):
                        index, chunks = extract_multiple_pdfs(pdf_files, bot.embed_model)
                    st.session_state.doc_index = index
                    st.session_state.doc_chunks = chunks
                    st.session_state.attachment_type = "multipdf"
                    st.session_state.attachment_name = f"{len(pdf_files)} PDFs loaded"
                    st.session_state.image_b64 = None
                    st.session_state.show_upload = False
                    st.success(f"✅ {len(pdf_files)} PDFs loaded!")
                    st.rerun()

            with tab3:
                img_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png", "webp"], key="img_up")
                if img_file:
                    b64 = image_to_base64(img_file)
                    st.session_state.image_b64 = b64
                    st.session_state.attachment_type = "image"
                    st.session_state.attachment_name = img_file.name
                    st.session_state.doc_index = None
                    st.session_state.doc_chunks = []
                    st.session_state.show_upload = False
                    st.image(img_file, width=200)
                    st.success(f"✅ {img_file.name} loaded!")
                    st.rerun()

            with tab4:
                st.markdown("⚠️ Only works with videos with captions enabled")
                yt_url = st.text_input("YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")
                if st.button("Load Video", key="load_yt"):
                    if yt_url.strip():
                        with st.spinner("Fetching transcript..."):
                            text, error = extract_youtube_transcript(yt_url)
                        if error:
                            st.error(f"❌ {error}")
                        else:
                            index, chunks = build_index(text, bot.embed_model)
                            st.session_state.doc_index = index
                            st.session_state.doc_chunks = chunks
                            st.session_state.attachment_type = "youtube"
                            st.session_state.attachment_name = "YouTube Video"
                            st.session_state.image_b64 = None
                            st.session_state.show_upload = False
                            st.success("✅ YouTube transcript loaded!")
                            st.rerun()
                    else:
                        st.warning("Please enter a YouTube URL.")

            with tab5:
                website_url = st.text_input("Website URL:", placeholder="https://example.com")
                if st.button("Load Website", key="load_web"):
                    if website_url.strip():
                        with st.spinner("Reading website..."):
                            text, error = extract_website_text(website_url)
                        if error:
                            st.error(f"❌ {error}")
                        else:
                            index, chunks = build_index(text, bot.embed_model)
                            st.session_state.doc_index = index
                            st.session_state.doc_chunks = chunks
                            st.session_state.attachment_type = "website"
                            st.session_state.attachment_name = website_url[:40]
                            st.session_state.image_b64 = None
                            st.session_state.show_upload = False
                            st.success("✅ Website loaded!")
                            st.rerun()
                    else:
                        st.warning("Please enter a URL.")

            if st.button("✕ Close", key="close_up"):
                st.session_state.show_upload = False
                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    prefill = st.session_state.pop("prefill_question", None)

    col_plus, col_input = st.columns([1, 11])
    with col_plus:
        if st.button("➕", help="Add PDF, Image, YouTube or Website", key="plus"):
            st.session_state.show_upload = not st.session_state.show_upload
            st.rerun()

    prompt = st.chat_input("Message RAG Chatbot...") or prefill

    if prompt:
        attachment_info = st.session_state.attachment_name or None
        image_b64 = st.session_state.image_b64

        user_msg = {
            "role": "user",
            "content": prompt,
            "attachment": attachment_info,
            "image": image_b64 if st.session_state.attachment_type == "image" else None
        }
        st.session_state.messages.append(user_msg)

        with st.chat_message("user"):
            if attachment_info:
                icon = "📄" if st.session_state.attachment_type in ["pdf", "multipdf"] \
                    else "🖼️" if st.session_state.attachment_type == "image" \
                    else "🌐" if st.session_state.attachment_type == "website" \
                    else "▶️"
                st.markdown(f'<div class="attachment-badge">{icon} {attachment_info}</div>', unsafe_allow_html=True)
            if image_b64 and st.session_state.attachment_type == "image":
                st.image(f"data:image/jpeg;base64,{image_b64}", width=200)
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            source = ""
            followups = []
            confidence = None

            if st.session_state.attachment_type == "image" and image_b64:
                with st.spinner("Analyzing image..."):
                    full_response = bot.answer_image(prompt, image_b64, st.session_state.language)
                response_placeholder.markdown(full_response)
                followups = bot.get_followup_questions(prompt, full_response)
                source = "🖼️ Image Analysis"

            elif st.session_state.attachment_type in ["pdf", "multipdf", "youtube", "website"] and st.session_state.doc_index:
                relevant_chunks = retrieve(prompt, st.session_state.doc_index, st.session_state.doc_chunks, bot.embed_model)
                context = "\n\n".join(relevant_chunks)
                for delta in bot.answer_from_context(prompt, context, st.session_state.attachment_name, st.session_state.language):
                    full_response += delta
                    response_placeholder.markdown(full_response + "▌")
                response_placeholder.markdown(full_response)
                followups = bot.get_followup_questions(prompt, full_response)
                confidence = bot.get_confidence(prompt, full_response, context)
                icon = "📄" if st.session_state.attachment_type in ["pdf", "multipdf"] \
                    else "🌐" if st.session_state.attachment_type == "website" else "▶️"
                source = f"{icon} {st.session_state.attachment_name}"

            else:
                for delta, src, fups, conf in bot.answer_stream(prompt, st.session_state.language):
                    if delta:
                        full_response += delta
                        response_placeholder.markdown(full_response + "▌")
                    if src:
                        source = src
                    if fups:
                        followups = fups
                    if conf is not None:
                        confidence = conf
                response_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.followups = followups
        st.session_state.source = source
        st.session_state.confidence = confidence
        st.rerun()