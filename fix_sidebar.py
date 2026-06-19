with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Remove header hidden CSS that hides sidebar toggle
content = content.replace(
    'header { visibility: hidden; }',
    'header { visibility: visible; }'
)

# Fix 2: Add sidebar always expanded
content = content.replace(
    'initial_sidebar_state="expanded"',
    'initial_sidebar_state="expanded"'
)

# Fix 3: If set_page_config still on one line fix it
old1 = 'st.set_page_config(page_title="RAG Chatbot", page_icon="🤖", layout="centered")'
new1 = 'st.set_page_config(page_title="RAG Chatbot", page_icon="🤖", layout="centered", initial_sidebar_state="expanded")'
content = content.replace(old1, new1)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done!")