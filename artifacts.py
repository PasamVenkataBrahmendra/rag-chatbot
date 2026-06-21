import streamlit as st
import re

def detect_artifact_type(content):
    content_lower = content.lower()

    code_patterns = ["```python", "```javascript", "```html", "```css", "```java", "```sql", "```bash"]
    for pattern in code_patterns:
        if pattern in content_lower:
            lang = pattern.replace("```", "")
            return "code", lang

    if any(x in content_lower for x in ["<!doctype", "<html", "<body", "<div"]):
        return "html", "html"

    if "| --- |" in content or ("|" in content and "\n|" in content):
        return "table", "markdown"

    if any(x in content_lower for x in ["# ", "## ", "### ", "**", "---"]):
        return "document", "markdown"

    return "text", "plain"

def extract_code_blocks(content):
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(pattern, content, re.DOTALL)
    return matches

def render_artifact(content, artifact_type, lang):
    if artifact_type == "html":
        code_blocks = extract_code_blocks(content)
        html_code = ""
        for block_lang, block_code in code_blocks:
            if block_lang in ["html", ""] or not block_lang:
                html_code = block_code
                break
        if not html_code:
            html_code = content

        st.components.v1.html(html_code, height=400, scrolling=True)
        return html_code

    elif artifact_type == "code":
        code_blocks = extract_code_blocks(content)
        if code_blocks:
            block_lang, block_code = code_blocks[0]
            st.code(block_code, language=block_lang or lang)
            return block_code
        else:
            st.code(content, language=lang)
            return content

    elif artifact_type == "table":
        st.markdown(content)
        return content

    elif artifact_type == "document":
        st.markdown(content)
        return content

    else:
        st.markdown(content)
        return content

def show_artifact_panel(content, title="Artifact"):
    artifact_type, lang = detect_artifact_type(content)

    with st.expander(f"🎨 Artifact: {title}", expanded=True):
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.caption(f"Type: {artifact_type.upper()} | Language: {lang}")

        with col2:
            if st.button("📋 Copy", key=f"copy_{hash(content)}"):
                st.toast("Copied to clipboard!")

        with col3:
            st.download_button(
                "📥 Download",
                data=content,
                file_name=f"artifact.{lang if lang != 'plain' else 'txt'}",
                mime="text/plain",
                key=f"dl_{hash(content)}"
            )

        tabs = st.tabs(["👁️ Preview", "📝 Edit", "💻 Raw"])

        with tabs[0]:
            render_artifact(content, artifact_type, lang)

        with tabs[1]:
            edited = st.text_area(
                "Edit content:",
                value=content,
                height=300,
                key=f"edit_{hash(content)}"
            )
            if st.button("✅ Apply Changes", key=f"apply_{hash(content)}"):
                st.success("Changes applied!")
                return edited

        with tabs[2]:
            st.code(content, language=lang)

    return content