with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = 'st.set_page_config(page_title="RAG Chatbot", page_icon="🤖", layout="centered")'
new = '''st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)'''

content = content.replace(old, new)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! Sidebar fix applied.")