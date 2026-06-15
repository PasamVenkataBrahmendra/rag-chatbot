import streamlit as st
from rag_pipeline import RAGChatbot

st.set_page_config(page_title="RAG Chatbot", page_icon="🤖", layout="centered")

st.markdown("""
    <style>
    .followup-btn {
        background-color: #f0f2f6;
        border: 1px solid #d0d3da;
        border-radius: 8px;
        padding: 6px 12px;
        margin: 4px;
        cursor: pointer;
        font-size: 13px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 RAG Chatbot")
st.markdown("Ask me anything — I search Wikipedia and answer like ChatGPT.")

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

# Handle prefilled follow up question click
prefill = st.session_state.pop("prefill_question", None)

# Chat input
prompt = st.chat_input("Ask anything...") or prefill

if prompt:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Stream assistant response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        source = ""
        followups = []

        for delta, src, fups in bot.answer_stream(prompt):
            if delta:
                full_response += delta
                response_placeholder.markdown(full_response + "▌")
            if src:
                source = src
            if fups:
                followups = fups

        response_placeholder.markdown(full_response)

    # Save to session
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.session_state.followups = followups
    st.session_state.source = source
    st.rerun()

# Sidebar
with st.sidebar:
    st.markdown("## 🤖 RAG Chatbot")
    st.markdown("Powered by **Llama 3** + **Wikipedia** + **FAISS**")
    st.markdown("---")
    st.markdown("### Features")
    st.markdown("✅ Answers any question")
    st.markdown("✅ Remembers conversation")
    st.markdown("✅ Streams word by word")
    st.markdown("✅ Suggests follow ups")
    st.markdown("✅ Shows sources")
    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.followups = []
        st.session_state.source = ""
        bot.clear_history()
        st.rerun()