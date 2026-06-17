import fitz
import faiss
import numpy as np
import base64
import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import re

def extract_text_from_pdf(pdf_file):
    text = ""
    pdf_bytes = pdf_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def extract_multiple_pdfs(pdf_files, embed_model):
    all_chunks = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    for pdf_file in pdf_files:
        text = extract_text_from_pdf(pdf_file)
        chunks = splitter.split_text(text)
        for chunk in chunks:
            all_chunks.append({"text": chunk, "source": pdf_file.name})
    if not all_chunks:
        return None, []
    texts = [c["text"] for c in all_chunks]
    embeddings = embed_model.encode(texts, show_progress_bar=False)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    return index, all_chunks

def extract_youtube_transcript(url):
    try:
        video_id = None
        patterns = [
            r'v=([a-zA-Z0-9_-]{11})',
            r'youtu\.be/([a-zA-Z0-9_-]{11})',
            r'embed/([a-zA-Z0-9_-]{11})'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                break
        if not video_id:
            return None, "Could not extract video ID from URL"
        ytt_api = YouTubeTranscriptApi()
        fetched = ytt_api.fetch(video_id)
        text = " ".join([t.text for t in fetched])
        return text, None
    except Exception as e:
        error_msg = str(e)
        if "Subtitles are disabled" in error_msg or "Could not retrieve" in error_msg:
            return None, "This video has subtitles disabled. Please try a video with captions enabled."
        return None, error_msg

def extract_website_text(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        text = "\n".join([l for l in text.splitlines() if len(l.strip()) > 30])
        return text[:15000], None
    except Exception as e:
        return None, str(e)

def image_to_base64(image_file):
    bytes_data = image_file.read()
    return base64.b64encode(bytes_data).decode("utf-8")

def build_index(text, embed_model):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)
    if not chunks:
        return None, []
    embeddings = embed_model.encode(chunks, show_progress_bar=False)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    return index, [{"text": c, "source": "document"} for c in chunks]

def retrieve(query, index, chunks, embed_model, top_k=4):
    query_embedding = embed_model.encode([query])
    distances, indices = index.search(np.array(query_embedding), top_k)
    results = []
    for idx in indices[0]:
        if idx < len(chunks):
            item = chunks[idx]
            if isinstance(item, dict):
                results.append(item["text"])
            else:
                results.append(item)
    return results

def web_search(query, num_results=5):
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            print("SERPER_API_KEY not found")
            return []

        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "num": num_results
        }

        response = requests.post(url, headers=headers, json=payload, timeout=10)
        data = response.json()

        results = []

        # Organic results
        for r in data.get("organic", [])[:num_results]:
            results.append({
                "title": r.get("title", ""),
                "snippet": r.get("snippet", ""),
                "url": r.get("link", "")
            })

        # Answer box if available
        if "answerBox" in data:
            box = data["answerBox"]
            results.insert(0, {
                "title": box.get("title", "Answer"),
                "snippet": box.get("answer", box.get("snippet", "")),
                "url": box.get("link", "")
            })

        # Knowledge graph if available
        if "knowledgeGraph" in data:
            kg = data["knowledgeGraph"]
            results.insert(0, {
                "title": kg.get("title", ""),
                "snippet": kg.get("description", ""),
                "url": kg.get("website", "")
            })

        print(f"Web search returned {len(results)} results")
        return results

    except Exception as e:
        print(f"Web search error: {e}")
        return []