import streamlit as st
from rag_pipeline import RAGChatbot
from pdf_handler import extract_text_from_pdf, build_pdf_index, retrieve_from_pdf

st.set_page_config(page_title="RAG Chatbot", page_icon="🤖", layout="centered")

st.title("🤖 RAG Chatbot")

@st.cache_resource
def load_bot():
    return RAGChatbot()

bot = load_bot()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "followups" not in st.session_state:
    st.session_state.followups = []
if "source" not in st.session_state:
    st.session_state.source = ""
if "pdf_index" not in st.session_state:
    st.session_state.pdf_index = None
if "pdf_chunks" not in st.session_state:
    st.session_state.pdf_chunks = []
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = ""
if "mode" not in st.session_state:
    st.session_state.mode = "wikipedia"

# Sidebar
with st.sidebar:
    st.markdown("## 🤖 RAG Chatbot")
    st.markdown("---")

    # Mode selector
    st.markdown("### Mode")
    mode = st.radio(
        "Choose what to chat with:",
        ["🌐 Wikipedia (any question)", "📄 My PDF document"],
        index=0
    )

    if "Wikipedia" in mode:
        st.session_state.mode = "wikipedia"
        st.markdown("---")
        st.markdown("✅ Ask any question")
        st.markdown("✅ Searches Wikipedia live")

    else:
        st.session_state.mode = "pdf"
        st.markdown("---")
        st.markdown("### Upload PDF")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload any PDF and ask questions about it"
        )

        if uploaded_file:
            if uploaded_file.name != st.session_state.pdf_name:
                with st.spinner("Reading PDF..."):
                    text = extract_text_from_pdf(uploaded_file)
                    index, chunks = build_pdf_index(text, bot.embed_model)
                    st.session_state.pdf_index = index
                    st.session_state.pdf_chunks = chunks
                    st.session_state.pdf_name = uploaded_file.name
                    st.session_state.messages = []
                    st.session_state.followups = []
                    bot.clear_history()
                st.success(f"✅ {uploaded_file.name} loaded! ({len(chunks)} chunks)")

    st.markdown("---")
    st.markdown("### Features")
    st.markdown("✅ Answers any question")
    st.markdown("✅ Chat with your PDF")
    st.markdown("✅ Remembers conversation")
    st.markdown("✅ Streams word by word")
    st.markdown("✅ Suggests follow ups")
    st.markdown("---")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.followups = []
        st.session_state.source = ""
        bot.clear_history()
        st.rerun()

# Main chat area
if st.session_state.mode == "pdf" and not st.session_state.pdf_index:
    st.info("📄 Upload a PDF from the sidebar to start chatting with it.")
else:
    if st.session_state.mode == "wikipedia":
        st.markdown("Ask me anything — I search Wikipedia and answer like ChatGPT.")
    else:
        st.markdown(f"Chatting with **{st.session_state.pdf_name}** — ask anything about it.")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Show follow up questions
if st.session_state.followups:
    st.markdown("**💡 You might also want to ask:**")
    cols = st.columns(len(st.session_state.followups))
    for i, question in enumerate(st.session_state.followups):
        if cols[i].button(question, key=f"followup_{i}_{question}"):
            st.session_state.prefill_question = question
            st.rerun()

# Show source
if st.session_state.source:
    st.caption(f"📚 Source: {st.session_state.source}")

# Handle prefilled follow up question
prefill = st.session_state.pop("prefill_question", None)

# Chat input
prompt = st.chat_input("Ask anything...") or prefill

if prompt:
    if st.session_state.mode == "pdf" and not st.session_state.pdf_index:
        st.warning("Please upload a PDF first from the sidebar.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            source = ""
            followups = []

            if st.session_state.mode == "pdf":
                # PDF mode — retrieve from PDF and answer
                relevant_chunks = retrieve_from_pdf(
                    prompt,
                    st.session_state.pdf_index,
                    st.session_state.pdf_chunks,
                    bot.embed_model
                )
                context = "\n\n".join(relevant_chunks)

                system_prompt = """You are a helpful assistant.
Answer questions based on the document provided.
Be direct, clear and concise.
Never say 'the context does not mention'.
If the answer is not in the document say 'I could not find that in the uploaded document.'"""

                user_prompt = f"""Document content:
{context}

Question: {prompt}"""

                bot.chat_history.append({"role": "user", "content": prompt})

                messages = [{"role": "system", "content": system_prompt}]
                if len(bot.chat_history) > 1:
                    messages += bot.chat_history[:-1]
                messages.append({"role": "user", "content": user_prompt})

                stream = bot.groq.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=0.2,
                    max_tokens=512,
                    stream=True
                )

                for chunk in stream:
                    delta = chunk.choices[0].delta.content or ""
                    full_response += delta
                    response_placeholder.markdown(full_response + "▌")

                response_placeholder.markdown(full_response)
                bot.chat_history.append({"role": "assistant", "content": full_response})
                followups = bot.get_followup_questions(prompt, full_response)
                source = f"📄 {st.session_state.pdf_name}"

            else:
                # Wikipedia mode
                for delta, src, fups in bot.answer_stream(prompt):
                    if delta:
                        full_response += delta
                        response_placeholder.markdown(full_response + "▌")
                    if src:
                        source = src
                    if fups:
                        followups = fups

                response_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.followups = followups
        st.session_state.source = source
        st.rerun()