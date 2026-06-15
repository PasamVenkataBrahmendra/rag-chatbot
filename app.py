import streamlit as st
from rag_pipeline import RAGChatbot

st.set_page_config(page_title="RAG Chatbot", page_icon="📖")
st.title("📖 RAG Chatbot — Technical Docs Q&A")
st.markdown("Ask anything about **Python, Machine Learning, Neural Networks, NLP, and Transformers.**")

@st.cache_resource
def load_bot():
    return RAGChatbot()

bot = load_bot()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

examples = [
    "What is machine learning?",
    "How do neural networks work?",
    "What is Python used for?",
    "What is natural language processing?",
    "How do transformers work in deep learning?"
]

st.markdown("**Example Questions:**")
cols = st.columns(len(examples))
for i, example in enumerate(examples):
    if cols[i].button(example[:25] + "...", key=f"ex_{i}"):
        st.session_state.prefill = example

if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer, sources = bot.answer(prompt)
            sources_text = "\n\n📚 **Sources:** " + ", ".join(sources)
            full_response = answer + sources_text
            st.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()