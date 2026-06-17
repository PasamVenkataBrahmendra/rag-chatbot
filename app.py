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
    "mode": "chat"
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
         "🎯 Interview Coach"],
        index=0
    )

    st.markdown("---")
    st.markdown("### ✅ Features")
    st.markdown("✅ Wikipedia Q&A")
    st.markdown("✅ Web search")
    st.markdown("✅ PDF chat (multi)")
    st.markdown("✅ Image understanding")
    st.markdown("✅ Image generation")
    st.markdown("✅ YouTube Q&A")
    st.markdown("✅ Website chat")
    st.markdown("✅ Math solver")
    st.markdown("✅ Code interpreter")
    st.markdown("✅ Auto summarizer")
    st.markdown("✅ Confidence score")
    st.markdown("✅ 11 languages")
    st.markdown("✅ Export chat")
    st.markdown("✅ Research reports")
    st.markdown("✅ Learning roadmaps")
    st.markdown("✅ Interview coach")
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
        for k in ["messages", "followups", "doc_chunks"]:
            st.session_state[k] = []
        for k in ["attachment_type", "doc_index", "image_b64"]:
            st.session_state[k] = None
        st.session_state.attachment_name = ""
        st.session_state.source = ""
        st.session_state.confidence = None
        st.session_state.show_upload = False
        bot.clear_history()
        st.rerun()

# ── WEB SEARCH MODE ──────────────────────────────────────────
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
        # Step 1: Search web immediately and save to session
        with st.spinner("Searching the web..."):
            results = web_search(prompt)

        # Step 2: Save results to session state so they survive rerun
        st.session_state.last_search_results = results
        st.session_state.last_search_query = prompt

        # Step 3: Save user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "search_results": None
        })

        # Step 4: Build full answer using results
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

        # Step 5: Get answer from Groq directly here
        response = bot.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.0,
            max_tokens=512
        )
        full_response = response.choices[0].message.content

        # Step 6: Save assistant message with results
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response,
            "search_results": results
        })
        st.rerun()

# ── IMAGE GENERATOR MODE ─────────────────────────────────────
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
                st.image(
                    f"data:image/jpeg;base64,{img_b64}",
                    caption=prompt
                )
                full_response = f"Here is your generated image for: **{prompt}**"
                st.markdown(full_response)

        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response,
            "generated_image": img_b64 if not error else None
        })
        st.rerun()

# ── MATH SOLVER MODE ─────────────────────────────────────────
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

        st.session_state.messages.append({
            "role": "assistant", "content": full_response
        })
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

        st.session_state.messages.append({
            "role": "assistant", "content": full_response
        })
        st.rerun()

# ── SUMMARIZE MODE ────────────────────────────────────────────
elif "Summarize" in mode:
    st.markdown("## 📝 Topic Summarizer")
    topic_input = st.text_input(
        "Enter topic:",
        placeholder="e.g. Quantum computing, DNA, World War 2..."
    )
    if st.button("📝 Summarize", use_container_width=True):
        if topic_input.strip():
            with st.spinner(f"Summarizing {topic_input}..."):
                summary, source = bot.summarize_topic(
                    topic_input, st.session_state.language
                )
            st.markdown(f"### 📖 {source}")
            st.markdown(summary)
            st.download_button(
                "📥 Download Summary",
                data=summary,
                file_name=f"summary_{topic_input.replace(' ', '_')}.txt",
                mime="text/plain"
            )
        else:
            st.warning("Please enter a topic.")
# ── RESEARCH ASSISTANT MODE ───────────────────────────────────
elif "Research Assistant" in mode:
    st.markdown("## 📊 Research Assistant")
    st.markdown("Generate a full structured research report on any topic.")

    col1, col2 = st.columns([3, 1])
    with col1:
        topic_input = st.text_input(
            "Research topic:",
            placeholder="e.g. Artificial Intelligence, Climate Change, Quantum Computing..."
        )
    with col2:
        lang = st.selectbox("Language", ["English", "Hindi", "Spanish", "French"], key="res_lang")

    if st.button("📊 Generate Research Report", use_container_width=True):
        if topic_input.strip():
            st.markdown(f"## 📄 Research Report: {topic_input}")
            response_placeholder = st.empty()
            full_report = ""

            with st.spinner(f"Researching {topic_input}... (this takes 30-60 seconds)"):
                for delta in bot.research_assistant(topic_input, lang):
                    full_report += delta
                    response_placeholder.markdown(full_report + "▌")

            response_placeholder.markdown(full_report)

            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "📥 Download as TXT",
                    data=full_report,
                    file_name=f"research_{topic_input.replace(' ', '_')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with col2:
                st.download_button(
                    "📥 Download as MD",
                    data=full_report,
                    file_name=f"research_{topic_input.replace(' ', '_')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
        else:
            st.warning("Please enter a research topic.")

# ── LEARNING PATH MODE ────────────────────────────────────────
elif "Learning Path" in mode:
    st.markdown("## 🗺️ Learning Path Generator")
    st.markdown("Get a personalised week by week roadmap for any skill.")

    col1, col2, col3 = st.columns(3)
    with col1:
        skill_input = st.text_input(
            "Skill to learn:",
            placeholder="e.g. Python, Machine Learning, Guitar, Photography..."
        )
    with col2:
        level = st.selectbox(
            "Your current level:",
            ["Complete Beginner", "Beginner", "Intermediate", "Advanced"],
            index=0
        )
    with col3:
        lang = st.selectbox("Language", ["English", "Hindi", "Spanish", "French"], key="lp_lang")

    if st.button("🗺️ Generate Learning Path", use_container_width=True):
        if skill_input.strip():
            st.markdown(f"## 🗺️ Learning Roadmap: {skill_input}")
            response_placeholder = st.empty()
            full_path = ""

            with st.spinner(f"Creating your personalised learning path for {skill_input}..."):
                for delta in bot.learning_path_generator(skill_input, level, lang):
                    full_path += delta
                    response_placeholder.markdown(full_path + "▌")

            response_placeholder.markdown(full_path)

            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "📥 Download Roadmap TXT",
                    data=full_path,
                    file_name=f"learning_path_{skill_input.replace(' ', '_')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with col2:
                st.download_button(
                    "📥 Download Roadmap MD",
                    data=full_path,
                    file_name=f"learning_path_{skill_input.replace(' ', '_')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
        else:
            st.warning("Please enter a skill.")

# ── INTERVIEW COACH MODE ──────────────────────────────────────
elif "Interview Coach" in mode:
    st.markdown("## 🎯 Interview Coach")
    st.markdown("Practice real interview questions for any job role and get graded.")

    # Session state for interview
    if "interview_role" not in st.session_state:
        st.session_state.interview_role = ""
    if "interview_round" not in st.session_state:
        st.session_state.interview_round = 0
    if "interview_question" not in st.session_state:
        st.session_state.interview_question = ""
    if "interview_history" not in st.session_state:
        st.session_state.interview_history = []
    if "interview_started" not in st.session_state:
        st.session_state.interview_started = False
    if "waiting_for_answer" not in st.session_state:
        st.session_state.waiting_for_answer = False

    # Setup screen
    if not st.session_state.interview_started:
        st.markdown("### Setup Your Interview")
        col1, col2 = st.columns(2)
        with col1:
            role_input = st.text_input(
                "Job role:",
                placeholder="e.g. Python Developer, Data Scientist, Product Manager..."
            )
        with col2:
            lang = st.selectbox(
                "Language",
                ["English", "Hindi", "Spanish", "French"],
                key="ic_lang"
            )

        if st.button("🎯 Start Interview", use_container_width=True):
            if role_input.strip():
                st.session_state.interview_role = role_input
                st.session_state.interview_round = 1
                st.session_state.interview_history = []
                st.session_state.interview_started = True
                st.session_state.interview_lang = lang

                with st.spinner("Preparing your first question..."):
                    question = bot.interview_coach_question(
                        role_input, 1, lang
                    )
                st.session_state.interview_question = question
                st.session_state.waiting_for_answer = True
                st.rerun()
            else:
                st.warning("Please enter a job role.")

    # Interview in progress
    else:
        role = st.session_state.interview_role
        round_num = st.session_state.interview_round
        lang = st.session_state.get("interview_lang", "English")

        # Stats bar
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Role", role)
        with col2:
            st.metric("Round", f"{round_num}")
        with col3:
            st.metric("Questions Done", round_num - 1)

        st.markdown("---")

        # Show interview history
        for item in st.session_state.interview_history:
            with st.expander(f"Round {item['round']}: {item['question'][:50]}..."):
                st.markdown(f"**❓ Question:** {item['question']}")
                st.markdown(f"**💬 Your Answer:** {item['answer']}")
                st.markdown("**📊 Feedback:**")
                st.markdown(item['feedback'])

        # Current question
        if st.session_state.interview_question:
            st.markdown(f"### ❓ Question {round_num}:")
            st.info(st.session_state.interview_question)

            # Answer input
            answer = st.text_area(
                "Your Answer:",
                placeholder="Type your answer here... Take your time and be specific.",
                height=150,
                key=f"answer_{round_num}"
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("📊 Submit Answer", use_container_width=True):
                    if answer.strip():
                        # Grade the answer
                        st.markdown("### 📊 Feedback:")
                        feedback_placeholder = st.empty()
                        full_feedback = ""

                        for delta in bot.interview_coach_grade(
                            role,
                            st.session_state.interview_question,
                            answer,
                            lang
                        ):
                            full_feedback += delta
                            feedback_placeholder.markdown(full_feedback + "▌")

                        feedback_placeholder.markdown(full_feedback)

                        # Save to history
                        st.session_state.interview_history.append({
                            "round": round_num,
                            "question": st.session_state.interview_question,
                            "answer": answer,
                            "feedback": full_feedback
                        })

                        # Next question
                        st.session_state.interview_round += 1
                        with st.spinner("Preparing next question..."):
                            next_q = bot.interview_coach_question(
                                role,
                                st.session_state.interview_round,
                                lang
                            )
                        st.session_state.interview_question = next_q
                        st.rerun()
                    else:
                        st.warning("Please type your answer before submitting.")

            with col2:
                if st.button("⏭️ Skip Question", use_container_width=True):
                    st.session_state.interview_round += 1
                    with st.spinner("Loading next question..."):
                        next_q = bot.interview_coach_question(
                            role,
                            st.session_state.interview_round,
                            lang
                        )
                    st.session_state.interview_question = next_q
                    st.rerun()

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Restart Interview", use_container_width=True):
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
                    report += f"Round {item['round']}\n"
                    report += f"Q: {item['question']}\n"
                    report += f"A: {item['answer']}\n"
                    report += f"Feedback:\n{item['feedback']}\n"
                    report += "\n" + "="*50 + "\n\n"

                st.download_button(
                    "📥 Download Interview Report",
                    data=report,
                    file_name=f"interview_{role.replace(' ', '_')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

# ── CHAT MODE ─────────────────────────────────────────────────
else:
    st.markdown("## 💬 RAG Chatbot")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("attachment"):
                st.markdown(
                    f'<div class="attachment-badge">📎 {msg["attachment"]}</div>',
                    unsafe_allow_html=True
                )
            if msg.get("image"):
                st.image(
                    f"data:image/jpeg;base64,{msg['image']}",
                    width=200
                )
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
            if cols[i].button(
                q[:30] + "..." if len(q) > 30 else q,
                key=f"fup_{i}_{q}"
            ):
                st.session_state.prefill_question = q
                st.rerun()

    st.markdown("---")

    # Attachment badge
    if st.session_state.attachment_name:
        icon = "📄" if st.session_state.attachment_type in ["pdf", "multipdf"] \
            else "🖼️" if st.session_state.attachment_type == "image" \
            else "🌐" if st.session_state.attachment_type == "website" \
            else "▶️"
        col1, col2 = st.columns([8, 1])
        with col1:
            st.markdown(
                f'<div class="attachment-badge">{icon} {st.session_state.attachment_name}</div>',
                unsafe_allow_html=True
            )
        with col2:
            if st.button("✕", key="remove_att"):
                st.session_state.attachment_type = None
                st.session_state.attachment_name = ""
                st.session_state.doc_index = None
                st.session_state.doc_chunks = []
                st.session_state.image_b64 = None
                st.rerun()

    # Upload popup
    if st.session_state.show_upload:
        with st.container():
            st.markdown('<div class="upload-popup">', unsafe_allow_html=True)
            st.markdown("### 📎 Add Attachment")

            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📄 PDF", "📄📄 Multi PDF",
                "🖼️ Image", "▶️ YouTube", "🌐 Website"
            ])

            with tab1:
                pdf_file = st.file_uploader(
                    "Upload PDF", type=["pdf"], key="pdf_up"
                )
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
                pdf_files = st.file_uploader(
                    "Upload Multiple PDFs",
                    type=["pdf"],
                    accept_multiple_files=True,
                    key="multi_pdf_up"
                )
                if pdf_files and st.button("Load All PDFs", key="load_multi"):
                    with st.spinner(f"Reading {len(pdf_files)} PDFs..."):
                        index, chunks = extract_multiple_pdfs(
                            pdf_files, bot.embed_model
                        )
                    st.session_state.doc_index = index
                    st.session_state.doc_chunks = chunks
                    st.session_state.attachment_type = "multipdf"
                    st.session_state.attachment_name = f"{len(pdf_files)} PDFs loaded"
                    st.session_state.image_b64 = None
                    st.session_state.show_upload = False
                    st.success(f"✅ {len(pdf_files)} PDFs loaded! ({len(chunks)} total chunks)")
                    st.rerun()

            with tab3:
                img_file = st.file_uploader(
                    "Upload Image",
                    type=["jpg", "jpeg", "png", "webp"],
                    key="img_up"
                )
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
                st.markdown("⚠️ Only works with videos with **captions enabled**")
                yt_url = st.text_input(
                    "YouTube URL:",
                    placeholder="https://www.youtube.com/watch?v=..."
                )
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
                website_url = st.text_input(
                    "Website URL:",
                    placeholder="https://example.com"
                )
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
                st.markdown(
                    f'<div class="attachment-badge">{icon} {attachment_info}</div>',
                    unsafe_allow_html=True
                )
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
                    full_response = bot.answer_image(
                        prompt, image_b64, st.session_state.language
                    )
                response_placeholder.markdown(full_response)
                followups = bot.get_followup_questions(prompt, full_response)
                source = "🖼️ Image Analysis"

            elif st.session_state.attachment_type in [
                "pdf", "multipdf", "youtube", "website"
            ] and st.session_state.doc_index:
                relevant_chunks = retrieve(
                    prompt,
                    st.session_state.doc_index,
                    st.session_state.doc_chunks,
                    bot.embed_model
                )
                context = "\n\n".join(relevant_chunks)
                for delta in bot.answer_from_context(
                    prompt, context,
                    st.session_state.attachment_name,
                    st.session_state.language
                ):
                    full_response += delta
                    response_placeholder.markdown(full_response + "▌")
                response_placeholder.markdown(full_response)
                followups = bot.get_followup_questions(prompt, full_response)
                confidence = bot.get_confidence(prompt, full_response, context)
                icon = "📄" if st.session_state.attachment_type in ["pdf", "multipdf"] \
                    else "🌐" if st.session_state.attachment_type == "website" \
                    else "▶️"
                source = f"{icon} {st.session_state.attachment_name}"

            else:
                for delta, src, fups, conf in bot.answer_stream(
                    prompt, st.session_state.language
                ):
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

        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response
        })
        st.session_state.followups = followups
        st.session_state.source = source
        st.session_state.confidence = confidence
        st.rerun()