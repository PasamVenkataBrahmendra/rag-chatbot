import streamlit as st
from rag_pipeline import RAGChatbot
from media_handler import (
    extract_text_from_pdf,
    extract_youtube_transcript,
    image_to_base64,
    build_index,
    retrieve
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
    "image_b64": None
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
        ["💬 Chat", "📝 Summarize Topic"],
        index=0
    )

    st.markdown("---")
    st.markdown("### ✅ Features")
    st.markdown("✅ Ask anything")
    st.markdown("✅ PDF chat")
    st.markdown("✅ Image understanding")
    st.markdown("✅ YouTube Q&A")
    st.markdown("✅ Auto summarizer")
    st.markdown("✅ Confidence score")
    st.markdown("✅ 11 languages")
    st.markdown("✅ Follow up questions")
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

# SUMMARIZE MODE
if "Summarize" in mode:
    st.markdown("## 📝 Topic Summarizer")
    topic_input = st.text_input(
        "Enter topic:",
        placeholder="e.g. Quantum computing, DNA, World War 2..."
    )
    if st.button("📝 Summarize", use_container_width=True):
        if topic_input.strip():
            with st.spinner(f"Summarizing {topic_input}..."):
                summary, source = bot.summarize_topic(
                    topic_input,
                    st.session_state.language
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

# CHAT MODE
else:
    st.markdown("## 💬 RAG Chatbot")

    # Display chat history
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

    # Confidence
    if st.session_state.confidence is not None:
        score = st.session_state.confidence
        color = "green" if score >= 80 else "orange" if score >= 60 else "red"
        st.markdown(f"🎯 Confidence: :{color}[**{score}%**]")

    # Source
    if st.session_state.source:
        st.caption(f"📚 {st.session_state.source}")

    # Follow up questions
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
        icon = "📄" if st.session_state.attachment_type == "pdf" \
            else "🖼️" if st.session_state.attachment_type == "image" \
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

            tab1, tab2, tab3 = st.tabs(["📄 PDF", "🖼️ Image", "▶️ YouTube"])

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

            with tab3:
                st.markdown("⚠️ Only works with videos that have **captions enabled**")
                st.markdown("Try: `https://www.youtube.com/watch?v=aircAruvnKk`")
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

            if st.button("✕ Close", key="close_up"):
                st.session_state.show_upload = False
                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    # Input bar
    prefill = st.session_state.pop("prefill_question", None)

    col_plus, col_input = st.columns([1, 11])
    with col_plus:
        if st.button("➕", help="Add PDF, Image or YouTube", key="plus"):
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
                icon = "📄" if st.session_state.attachment_type == "pdf" \
                    else "🖼️" if st.session_state.attachment_type == "image" \
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

            # IMAGE MODE
            if st.session_state.attachment_type == "image" and image_b64:
                with st.spinner("Analyzing image..."):
                    full_response = bot.answer_image(
                        prompt, image_b64,
                        st.session_state.language
                    )
                response_placeholder.markdown(full_response)
                followups = bot.get_followup_questions(prompt, full_response)
                source = "🖼️ Image Analysis"

            # PDF or YOUTUBE MODE
            elif st.session_state.attachment_type in ["pdf", "youtube"] \
                    and st.session_state.doc_index:
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
                icon = "📄" if st.session_state.attachment_type == "pdf" else "▶️"
                source = f"{icon} {st.session_state.attachment_name}"

            # WIKIPEDIA MODE
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