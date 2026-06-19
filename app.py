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
from database import init_db, create_session, save_message, load_session_messages, get_all_sessions, delete_session, rename_session
from code_executor import extract_python_code, execute_python_code, is_safe_code
import datetime
import pyttsx3
import threading

# Init DB
init_db()

st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #ffffff; color: #1a1a1a; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: visible; }
    div[data-testid="stSidebar"] { background-color: #f7f7f8; border-right: 1px solid #e5e5e5; }
    div[data-testid="collapsedControl"] { display: block !important; visibility: visible !important; }
    button[kind="header"] { display: block !important; }
    section[data-testid="stSidebarCollapsedControl"] { display: block !important; }
    .attachment-badge { background: #f0f7ff; border: 1px solid #b3d4ff; border-radius: 8px; padding: 6px 12px; font-size: 13px; color: #0066cc; display: inline-block; margin: 4px 0; }
    .upload-popup { background: #ffffff; border: 1px solid #e5e5e5; border-radius: 12px; padding: 16px; margin: 8px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .search-result { background: #f7f7f8; border: 1px solid #e5e5e5; border-radius: 8px; padding: 10px; margin: 6px 0; font-size: 13px; }
    .citation-box { background: #f0f7ff; border-left: 3px solid #0066cc; padding: 8px 12px; margin: 4px 0; border-radius: 4px; font-size: 12px; }
    .improved-prompt { background: #f0fff4; border: 1px solid #68d391; border-radius: 8px; padding: 10px; margin: 8px 0; font-size: 13px; }
    .exec-output { background: #1a1a1a; color: #00ff00; padding: 12px; border-radius: 8px; font-family: monospace; font-size: 13px; margin: 8px 0; }
    .exec-error { background: #fff5f5; color: #e53e3e; padding: 12px; border-radius: 8px; font-family: monospace; font-size: 13px; margin: 8px 0; }
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
    "interview_lang": "English",
    "session_id": None,
    "citations": [],
    "auto_improve": False,
    "tts_enabled": False
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def speak_text(text):
    def run():
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.say(text[:500])
            engine.runAndWait()
        except:
            pass
    thread = threading.Thread(target=run, daemon=True)
    thread.start()

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
    st.markdown("### ⚙️ Settings")
    st.session_state.auto_improve = st.toggle("✨ Auto Improve Prompts", value=st.session_state.auto_improve)
    st.session_state.tts_enabled = st.toggle("🔊 Text to Speech", value=st.session_state.tts_enabled)

    st.markdown("---")
    st.markdown("### 💾 Chat History")

    if st.button("➕ New Chat", use_container_width=True):
        session_id = create_session()
        st.session_state.session_id = session_id
        st.session_state.messages = []
        st.session_state.followups = []
        st.session_state.citations = []
        bot.clear_history()
        st.rerun()

    sessions = get_all_sessions()
    if sessions:
        st.markdown("**Previous Chats:**")
        for s in sessions[:5]:
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(f"💬 {s['name'][:20]}", key=f"sess_{s['id']}", use_container_width=True):
                    st.session_state.session_id = s['id']
                    msgs = load_session_messages(s['id'])
                    st.session_state.messages = [
                        {"role": m["role"], "content": m["content"], **m["metadata"]}
                        for m in msgs
                    ]
                    bot.clear_history()
                    for m in msgs:
                        if m["role"] in ["user", "assistant"]:
                            bot.chat_history.append({"role": m["role"], "content": m["content"]})
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{s['id']}"):
                    delete_session(s['id'])
                    if st.session_state.session_id == s['id']:
                        st.session_state.session_id = None
                        st.session_state.messages = []
                    st.rerun()

    st.markdown("---")
    st.markdown("### 🛠️ Mode")
    mode = st.radio(
        "Choose mode:",
        ["💬 Chat", "🔍 Web Search", "🖼️ Image Generator",
         "🧮 Math Solver", "💻 Code Interpreter", "📝 Summarize Topic",
         "📊 Research Assistant", "🗺️ Learning Path", "🎯 Interview Coach",
         "🃏 Flashcards", "📝 Quiz Mode", "🗄️ Text to SQL",
         "📐 Diagram Generator", "📧 Email Writer", "📄 Cover Letter",
         "✅ Grammar Checker", "🎨 Tone Changer", "🧠 Mind Map",
         "🎯 Action Plan", "⚔️ Debate Mode"],
        index=0
    )

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
        st.session_state.messages = []
        st.session_state.followups = []
        st.session_state.citations = []
        st.session_state.doc_chunks = []
        st.session_state.interview_history = []
        for k in ["attachment_type", "doc_index", "image_b64"]:
            st.session_state[k] = None
        st.session_state.attachment_name = ""
        st.session_state.source = ""
        st.session_state.confidence = None
        st.session_state.show_upload = False
        st.session_state.interview_started = False
        bot.clear_history()
        st.rerun()

# ── HELPER: Save message to DB ────────────────────────────────
def save_to_db(role, content, metadata=None):
    if st.session_state.session_id:
        save_message(st.session_state.session_id, role, content, metadata)
    elif role == "user":
        session_id = create_session(content[:30])
        st.session_state.session_id = session_id
        save_message(session_id, role, content, metadata)

# ── WEB SEARCH MODE ───────────────────────────────────────────
if "Web Search" in mode:
    st.markdown("## 🔍 Web Search")
    st.markdown("Search the live internet like Perplexity AI.")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("search_results"):
                with st.expander("🔍 Search Results"):
                    for r in msg["search_results"]:
                        st.markdown(f'<div class="search-result"><b>{r["title"]}</b><br>{r["snippet"]}<br><a href="{r["url"]}" target="_blank">🔗 Source</a></div>', unsafe_allow_html=True)
            st.markdown(msg["content"])

    prompt = st.chat_input("Search anything...")
    if prompt:
        with st.spinner("Searching the web..."):
            results = web_search(prompt)

        save_to_db("user", prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        system_prompt = f"""You are a helpful web search assistant.
Answer in {st.session_state.language} using LIVE search results.
Be direct. Never mention knowledge cutoff."""

        context = "\n\n".join([
            f"Result {i+1}:\nTitle: {r['title']}\nInfo: {r['snippet']}\nURL: {r['url']}"
            for i, r in enumerate(results)
        ]) if results else "No results found."

        response = bot.groq_call(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Search results for '{prompt}':\n\n{context}\n\nAnswer: {prompt}"}
            ],
            temperature=0.0,
            max_tokens=512
        )
        full_response = response.choices[0].message.content
        save_to_db("assistant", full_response, {"search_results": results})
        st.session_state.messages.append({"role": "assistant", "content": full_response, "search_results": results})
        if st.session_state.tts_enabled:
            speak_text(full_response)
        st.rerun()

# ── IMAGE GENERATOR MODE ──────────────────────────────────────
elif "Image Generator" in mode:
    st.markdown("## 🖼️ Image Generator")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("generated_image"):
                st.image(f"data:image/jpeg;base64,{msg['generated_image']}", caption=msg["content"])
            else:
                st.markdown(msg["content"])

    prompt = st.chat_input("Describe the image you want...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_to_db("user", prompt)
        with st.chat_message("assistant"):
            with st.spinner("Generating image... (10-20 seconds)"):
                img_b64, error = bot.generate_image(prompt)
            if error:
                st.error(f"❌ {error}")
                full_response = f"Failed: {error}"
            else:
                st.image(f"data:image/jpeg;base64,{img_b64}", caption=prompt)
                full_response = f"Generated image for: **{prompt}**"
                st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response, "generated_image": img_b64 if not error else None})
        save_to_db("assistant", full_response)
        st.rerun()

# ── MATH SOLVER MODE ──────────────────────────────────────────
elif "Math Solver" in mode:
    st.markdown("## 🧮 Math Solver")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Enter your math problem...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_to_db("user", prompt)
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            for delta in bot.solve_math(prompt, st.session_state.language):
                full_response += delta
                response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        save_to_db("assistant", full_response)
        if st.session_state.tts_enabled:
            speak_text(full_response)
        st.rerun()

# ── CODE INTERPRETER MODE ─────────────────────────────────────
elif "Code Interpreter" in mode:
    st.markdown("## 💻 Code Interpreter")
    st.markdown("Write, explain and **actually execute** Python code.")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("execution_output"):
                if msg.get("execution_success"):
                    st.markdown(f'<div class="exec-output">▶ Output:\n{msg["execution_output"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="exec-error">❌ Error:\n{msg["execution_output"]}</div>', unsafe_allow_html=True)

    prompt = st.chat_input("Ask a coding question...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_to_db("user", prompt)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            for delta in bot.answer_code(prompt, st.session_state.language):
                full_response += delta
                response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)

            # Auto execute Python code
            code = extract_python_code(full_response)
            execution_output = None
            execution_success = False

            if code:
                is_safe, reason = is_safe_code(code)
                if is_safe:
                    with st.spinner("Executing code..."):
                        execution_success, execution_output = execute_python_code(code)
                    if execution_success:
                        st.markdown(f'<div class="exec-output">▶ Output:\n{execution_output}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="exec-error">❌ Error:\n{execution_output}</div>', unsafe_allow_html=True)
                else:
                    st.warning(f"Code not executed: {reason}")

        msg_data = {
            "role": "assistant",
            "content": full_response,
            "execution_output": execution_output,
            "execution_success": execution_success
        }
        st.session_state.messages.append(msg_data)
        save_to_db("assistant", full_response, {"execution_output": execution_output})
        st.rerun()

# ── SUMMARIZE MODE ────────────────────────────────────────────
elif "Summarize" in mode:
    st.markdown("## 📝 Topic Summarizer")
    topic_input = st.text_input("Enter topic:", placeholder="e.g. Quantum computing...")
    if st.button("📝 Summarize", use_container_width=True):
        if topic_input.strip():
            with st.spinner(f"Summarizing {topic_input}..."):
                summary, source = bot.summarize_topic(topic_input, st.session_state.language)
            st.markdown(f"### 📖 {source}")
            st.markdown(summary)
            if st.session_state.tts_enabled:
                speak_text(summary[:500])
            st.download_button("📥 Download", data=summary, file_name=f"summary_{topic_input.replace(' ','_')}.txt", mime="text/plain")
        else:
            st.warning("Please enter a topic.")

# ── RESEARCH ASSISTANT MODE ───────────────────────────────────
elif "Research Assistant" in mode:
    st.markdown("## 📊 Research Assistant")
    col1, col2 = st.columns([3, 1])
    with col1:
        topic_input = st.text_input("Research topic:", placeholder="e.g. Artificial Intelligence...")
    with col2:
        lang = st.selectbox("Language", ["English", "Hindi", "Spanish", "French"], key="res_lang")

    if st.button("📊 Generate Report", use_container_width=True):
        if topic_input.strip():
            response_placeholder = st.empty()
            full_report = ""
            with st.spinner("Researching..."):
                for delta in bot.research_assistant(topic_input, lang):
                    full_report += delta
                    response_placeholder.markdown(full_report + "▌")
            response_placeholder.markdown(full_report)
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("📥 TXT", data=full_report, file_name=f"research_{topic_input.replace(' ','_')}.txt", mime="text/plain", use_container_width=True)
            with col2:
                st.download_button("📥 MD", data=full_report, file_name=f"research_{topic_input.replace(' ','_')}.md", mime="text/markdown", use_container_width=True)
        else:
            st.warning("Please enter a topic.")

# ── LEARNING PATH MODE ────────────────────────────────────────
elif "Learning Path" in mode:
    st.markdown("## 🗺️ Learning Path Generator")
    col1, col2, col3 = st.columns(3)
    with col1:
        skill_input = st.text_input("Skill:", placeholder="e.g. Python, Guitar...")
    with col2:
        level = st.selectbox("Level:", ["Complete Beginner", "Beginner", "Intermediate", "Advanced"])
    with col3:
        lang = st.selectbox("Language", ["English", "Hindi", "Spanish", "French"], key="lp_lang")

    if st.button("🗺️ Generate Path", use_container_width=True):
        if skill_input.strip():
            response_placeholder = st.empty()
            full_path = ""
            with st.spinner("Creating roadmap..."):
                for delta in bot.learning_path_generator(skill_input, level, lang):
                    full_path += delta
                    response_placeholder.markdown(full_path + "▌")
            response_placeholder.markdown(full_path)
            st.download_button("📥 Download", data=full_path, file_name=f"learning_{skill_input.replace(' ','_')}.txt", mime="text/plain")
        else:
            st.warning("Please enter a skill.")

# ── INTERVIEW COACH MODE ──────────────────────────────────────
elif "Interview Coach" in mode:
    st.markdown("## 🎯 Interview Coach")

    if not st.session_state.interview_started:
        col1, col2 = st.columns(2)
        with col1:
            role_input = st.text_input("Job role:", placeholder="e.g. Python Developer...")
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
        with col1: st.metric("Role", role)
        with col2: st.metric("Round", round_num)
        with col3: st.metric("Done", round_num - 1)
        st.markdown("---")

        for item in st.session_state.interview_history:
            with st.expander(f"Round {item['round']}: {item['question'][:50]}..."):
                st.markdown(f"**Q:** {item['question']}")
                st.markdown(f"**A:** {item['answer']}")
                st.markdown(item['feedback'])

        if st.session_state.interview_question:
            st.markdown(f"### Question {round_num}:")
            st.info(st.session_state.interview_question)
            if st.session_state.tts_enabled:
                speak_text(st.session_state.interview_question)

            answer = st.text_area("Your Answer:", height=150, key=f"ans_{round_num}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Submit", use_container_width=True):
                    if answer.strip():
                        feedback_placeholder = st.empty()
                        full_feedback = ""
                        for delta in bot.interview_coach_grade(role, st.session_state.interview_question, answer, lang):
                            full_feedback += delta
                            feedback_placeholder.markdown(full_feedback + "▌")
                        feedback_placeholder.markdown(full_feedback)
                        st.session_state.interview_history.append({
                            "round": round_num, "question": st.session_state.interview_question,
                            "answer": answer, "feedback": full_feedback
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
                st.download_button("📥 Report", data=report, file_name=f"interview_{role.replace(' ','_')}.txt", mime="text/plain", use_container_width=True)

# ── FLASHCARDS MODE ───────────────────────────────────────────
elif "Flashcards" in mode:
    st.markdown("## 🃏 Flashcard Generator")
    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("Topic:", placeholder="e.g. Python, History...")
    with col2:
        num = st.slider("Cards:", 5, 20, 10)
    if st.button("🃏 Generate", use_container_width=True):
        if topic.strip():
            placeholder = st.empty()
            full_text = ""
            for delta in bot.generate_flashcards(topic, num, st.session_state.language):
                full_text += delta
                placeholder.markdown(full_text + "▌")
            placeholder.markdown(full_text)
            st.download_button("📥 Download", data=full_text, file_name=f"flashcards_{topic.replace(' ','_')}.txt", mime="text/plain")
        else:
            st.warning("Please enter a topic.")

# ── QUIZ MODE ─────────────────────────────────────────────────
elif "Quiz Mode" in mode:
    st.markdown("## 📝 Quiz Generator")
    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("Topic:", placeholder="e.g. Machine Learning...")
    with col2:
        num_q = st.slider("Questions:", 3, 10, 5)
    if st.button("📝 Generate Quiz", use_container_width=True):
        if topic.strip():
            placeholder = st.empty()
            full_quiz = ""
            for delta in bot.generate_quiz(topic, num_q, st.session_state.language):
                full_quiz += delta
                placeholder.markdown(full_quiz + "▌")
            placeholder.markdown(full_quiz)
            st.download_button("📥 Download", data=full_quiz, file_name=f"quiz_{topic.replace(' ','_')}.txt", mime="text/plain")
        else:
            st.warning("Please enter a topic.")

# ── TEXT TO SQL MODE ──────────────────────────────────────────
elif "Text to SQL" in mode:
    st.markdown("## 🗄️ Text to SQL")
    description = st.text_area("Describe query:", placeholder="e.g. Get all users who signed up last 30 days...", height=100)
    schema = st.text_area("Schema (optional):", placeholder="e.g. users(id, name, email)...", height=60)
    if st.button("🗄️ Generate SQL", use_container_width=True):
        if description.strip():
            placeholder = st.empty()
            full_sql = ""
            for delta in bot.text_to_sql(description, schema, st.session_state.language):
                full_sql += delta
                placeholder.markdown(full_sql + "▌")
            placeholder.markdown(full_sql)
            st.download_button("📥 Download", data=full_sql, file_name="query.sql", mime="text/plain")
        else:
            st.warning("Please describe what you want.")

# ── DIAGRAM GENERATOR MODE ────────────────────────────────────
elif "Diagram Generator" in mode:
    st.markdown("## 📐 Diagram Generator")
    description = st.text_area("Describe system:", placeholder="e.g. RAG chatbot pipeline...", height=100)
    if st.button("📐 Generate", use_container_width=True):
        if description.strip():
            placeholder = st.empty()
            full_diagram = ""
            for delta in bot.generate_diagram(description, st.session_state.language):
                full_diagram += delta
                placeholder.markdown(full_diagram + "▌")
            placeholder.markdown(full_diagram)
            st.download_button("📥 Download", data=full_diagram, file_name="diagram.txt", mime="text/plain")
        else:
            st.warning("Please describe the system.")

# ── EMAIL WRITER MODE ─────────────────────────────────────────
elif "Email Writer" in mode:
    st.markdown("## 📧 Email Writer")
    situation = st.text_area("Situation:", placeholder="e.g. Follow up with client...", height=100)
    col1, col2 = st.columns(2)
    with col1:
        tone = st.selectbox("Tone:", ["Professional", "Formal", "Friendly", "Assertive", "Apologetic", "Persuasive"])
    with col2:
        lang = st.selectbox("Language:", ["English", "Hindi", "Spanish", "French"], key="email_lang")
    if st.button("📧 Write Email", use_container_width=True):
        if situation.strip():
            placeholder = st.empty()
            full_email = ""
            for delta in bot.write_email(situation, tone, lang):
                full_email += delta
                placeholder.markdown(full_email + "▌")
            placeholder.markdown(full_email)
            st.download_button("📥 Download", data=full_email, file_name="email.txt", mime="text/plain")
        else:
            st.warning("Please describe your situation.")

# ── COVER LETTER MODE ─────────────────────────────────────────
elif "Cover Letter" in mode:
    st.markdown("## 📄 Cover Letter Generator")
    col1, col2 = st.columns(2)
    with col1:
        job_desc = st.text_area("Job Description:", height=200)
    with col2:
        skills = st.text_area("Your Skills:", height=200)
    lang = st.selectbox("Language:", ["English", "Hindi", "Spanish", "French"], key="cl_lang")
    if st.button("📄 Generate", use_container_width=True):
        if job_desc.strip() and skills.strip():
            placeholder = st.empty()
            full_letter = ""
            for delta in bot.generate_cover_letter(job_desc, skills, lang):
                full_letter += delta
                placeholder.markdown(full_letter + "▌")
            placeholder.markdown(full_letter)
            st.download_button("📥 Download", data=full_letter, file_name="cover_letter.txt", mime="text/plain")
        else:
            st.warning("Please fill both fields.")

# ── GRAMMAR CHECKER MODE ──────────────────────────────────────
elif "Grammar Checker" in mode:
    st.markdown("## ✅ Grammar Checker")
    text_input = st.text_area("Paste text:", height=200)
    if st.button("✅ Check", use_container_width=True):
        if text_input.strip():
            placeholder = st.empty()
            full_check = ""
            for delta in bot.grammar_checker(text_input, st.session_state.language):
                full_check += delta
                placeholder.markdown(full_check + "▌")
            placeholder.markdown(full_check)
            st.download_button("📥 Download", data=full_check, file_name="grammar_check.txt", mime="text/plain")
        else:
            st.warning("Please enter text.")

# ── TONE CHANGER MODE ─────────────────────────────────────────
elif "Tone Changer" in mode:
    st.markdown("## 🎨 Tone Changer")
    text_input = st.text_area("Your text:", height=150)
    col1, col2 = st.columns(2)
    with col1:
        target_tone = st.selectbox("Tone:", ["Professional", "Casual", "Formal", "Friendly", "Funny", "Persuasive", "Empathetic", "Confident", "Simple"])
    with col2:
        lang = st.selectbox("Language:", ["English", "Hindi", "Spanish", "French"], key="tc_lang")
    if st.button("🎨 Rewrite", use_container_width=True):
        if text_input.strip():
            placeholder = st.empty()
            full_rewrite = ""
            for delta in bot.tone_changer(text_input, target_tone, lang):
                full_rewrite += delta
                placeholder.markdown(full_rewrite + "▌")
            placeholder.markdown(full_rewrite)
            st.download_button("📥 Download", data=full_rewrite, file_name="rewritten.txt", mime="text/plain")
        else:
            st.warning("Please enter text.")

# ── MIND MAP MODE ─────────────────────────────────────────────
elif "Mind Map" in mode:
    st.markdown("## 🧠 Mind Map Generator")
    topic = st.text_input("Topic:", placeholder="e.g. Machine Learning...")
    if st.button("🧠 Generate", use_container_width=True):
        if topic.strip():
            placeholder = st.empty()
            full_map = ""
            for delta in bot.mind_map(topic, st.session_state.language):
                full_map += delta
                placeholder.markdown(full_map + "▌")
            placeholder.markdown(full_map)
            st.download_button("📥 Download", data=full_map, file_name=f"mindmap_{topic.replace(' ','_')}.txt", mime="text/plain")
        else:
            st.warning("Please enter a topic.")

# ── ACTION PLAN MODE ──────────────────────────────────────────
elif "Action Plan" in mode:
    st.markdown("## 🎯 Action Plan Generator")
    goal = st.text_area("Your goal:", height=100)
    col1, col2 = st.columns(2)
    with col1:
        timeframe = st.selectbox("Timeframe:", ["7 days", "30 days", "60 days", "90 days", "6 months", "1 year"])
    with col2:
        lang = st.selectbox("Language:", ["English", "Hindi", "Spanish", "French"], key="ap_lang")
    if st.button("🎯 Generate Plan", use_container_width=True):
        if goal.strip():
            placeholder = st.empty()
            full_plan = ""
            for delta in bot.action_plan(goal, timeframe, lang):
                full_plan += delta
                placeholder.markdown(full_plan + "▌")
            placeholder.markdown(full_plan)
            st.download_button("📥 Download", data=full_plan, file_name="action_plan.txt", mime="text/plain")
        else:
            st.warning("Please enter your goal.")

# ── DEBATE MODE ───────────────────────────────────────────────
elif "Debate Mode" in mode:
    st.markdown("## ⚔️ Debate Mode")
    topic = st.text_input("Topic:", placeholder="e.g. AI will replace all jobs...")
    if st.button("⚔️ Start Debate", use_container_width=True):
        if topic.strip():
            placeholder = st.empty()
            full_debate = ""
            for delta in bot.debate_mode(topic, st.session_state.language):
                full_debate += delta
                placeholder.markdown(full_debate + "▌")
            placeholder.markdown(full_debate)
            st.download_button("📥 Download", data=full_debate, file_name=f"debate_{topic.replace(' ','_')}.txt", mime="text/plain")
        else:
            st.warning("Please enter a topic.")

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

    if st.session_state.get("citations"):
        with st.expander(f"📖 View {len(st.session_state.citations)} Source Citations"):
            for c in st.session_state.citations:
                st.markdown(f"""<div class="citation-box">
<b>Chunk {c['chunk_num']}</b> — Relevance: {c['relevance']}%<br>
<i>{c['text']}</i><br>
Source: <a href="{c['url']}" target="_blank">{c['source']}</a>
</div>""", unsafe_allow_html=True)

    if st.session_state.followups:
        st.markdown("**💡 You might also want to ask:**")
        cols = st.columns(len(st.session_state.followups))
        for i, q in enumerate(st.session_state.followups):
            if cols[i].button(q[:30] + "..." if len(q) > 30 else q, key=f"fup_{i}_{q}"):
                st.session_state.prefill_question = q
                st.rerun()

    st.markdown("---")

    if st.session_state.attachment_name:
        icon = "📄" if st.session_state.attachment_type in ["pdf", "multipdf"] else "🖼️" if st.session_state.attachment_type == "image" else "🌐" if st.session_state.attachment_type == "website" else "▶️"
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
                            st.success("✅ YouTube loaded!")
                            st.rerun()
                    else:
                        st.warning("Please enter a URL.")

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
        # Auto improve prompt if enabled
        if st.session_state.auto_improve:
            with st.spinner("✨ Improving your prompt..."):
                improved = bot.improve_prompt(prompt)
            if improved != prompt:
                st.markdown(f'<div class="improved-prompt">✨ <b>Improved prompt:</b> {improved}</div>', unsafe_allow_html=True)
                prompt = improved

        attachment_info = st.session_state.attachment_name or None
        image_b64 = st.session_state.image_b64

        user_msg = {
            "role": "user",
            "content": prompt,
            "attachment": attachment_info,
            "image": image_b64 if st.session_state.attachment_type == "image" else None
        }
        st.session_state.messages.append(user_msg)
        save_to_db("user", prompt, {"attachment": attachment_info})

        with st.chat_message("user"):
            if attachment_info:
                icon = "📄" if st.session_state.attachment_type in ["pdf", "multipdf"] else "🖼️" if st.session_state.attachment_type == "image" else "🌐" if st.session_state.attachment_type == "website" else "▶️"
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
            citations = []

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
                icon = "📄" if st.session_state.attachment_type in ["pdf", "multipdf"] else "🌐" if st.session_state.attachment_type == "website" else "▶️"
                source = f"{icon} {st.session_state.attachment_name}"

            else:
                for delta, src, fups, conf, cits in bot.answer_stream(prompt, st.session_state.language):
                    if delta:
                        full_response += delta
                        response_placeholder.markdown(full_response + "▌")
                    if src: source = src
                    if fups: followups = fups
                    if conf is not None: confidence = conf
                    if cits: citations = cits
                response_placeholder.markdown(full_response)

        if st.session_state.tts_enabled:
            speak_text(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})
        save_to_db("assistant", full_response)
        st.session_state.followups = followups
        st.session_state.source = source
        st.session_state.confidence = confidence
        st.session_state.citations = citations
        st.rerun()