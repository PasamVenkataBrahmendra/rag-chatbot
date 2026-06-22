import os
import multiprocessing

multiprocessing.freeze_support()
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json

app = FastAPI(title="RAG Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

bot = None

@app.on_event("startup")
async def startup_event():
    global bot
    print("Initializing RAG Chatbot...")
    from rag_pipeline import RAGChatbot
    from database import init_db
    init_db()
    bot = RAGChatbot()
    print("API Ready!")

@app.get("/")
def root():
    return {"status": "RAG Chatbot API Running"}

@app.post("/api/chat")
async def chat(
    message: str = Form(...),
    language: str = Form("English"),
    session_id: str = Form(None)
):
    async def generate():
        full_response = ""
        source = ""
        followups = []
        confidence = None
        citations = []

        try:
            for delta, src, fups, conf, cits in bot.answer_stream(message, language):
                if delta:
                    full_response += delta
                    yield f"data: {json.dumps({'type': 'delta', 'content': delta})}\n\n"
                if src:
                    source = src
                if fups:
                    followups = fups
                if conf is not None:
                    confidence = conf
                if cits:
                    citations = cits

            yield f"data: {json.dumps({'type': 'done', 'source': source, 'followups': followups, 'confidence': confidence, 'citations': citations})}\n\n"

            if session_id:
                from database import save_message
                save_message(int(session_id), "user", message)
                save_message(int(session_id), "assistant", full_response)

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/api/web-search")
async def web_search_endpoint(
    query: str = Form(...),
    language: str = Form("English")
):
    try:
        from media_handler import web_search
        results = web_search(query)

        system_prompt = f"""You are a helpful web search assistant.
Answer in {language} using LIVE search results. Be direct."""

        context = "\n\n".join([
            f"Result {i+1}:\nTitle: {r['title']}\nInfo: {r['snippet']}\nURL: {r['url']}"
            for i, r in enumerate(results)
        ]) if results else "No results found."

        response = bot.groq_call(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Search results for '{query}':\n\n{context}\n\nAnswer: {query}"}
            ],
            temperature=0.0,
            max_tokens=512
        )

        return {
            "answer": response.choices[0].message.content,
            "results": results
        }
    except Exception as e:
        return {"error": str(e), "answer": f"Error: {str(e)}", "results": []}

@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        import fitz
        from media_handler import build_index
        content = await file.read()
        doc = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()

        index, chunks = build_index(text, bot.embed_model)
        bot.current_pdf_index = index
        bot.current_pdf_chunks = chunks
        bot.current_pdf_name = file.filename

        return {"success": True, "filename": file.filename, "chunks": len(chunks)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/pdf-chat")
async def pdf_chat(
    message: str = Form(...),
    language: str = Form("English")
):
    if not hasattr(bot, 'current_pdf_index') or bot.current_pdf_index is None:
        return {"error": "No PDF uploaded"}

    async def generate():
        try:
            from media_handler import retrieve
            relevant_chunks = retrieve(
                message,
                bot.current_pdf_index,
                bot.current_pdf_chunks,
                bot.embed_model
            )
            context = "\n\n".join(relevant_chunks)

            for delta in bot.answer_from_context(message, context, bot.current_pdf_name, language):
                yield f"data: {json.dumps({'type': 'delta', 'content': delta})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/api/generate-image")
async def generate_image(prompt: str = Form(...)):
    try:
        img_b64, error = bot.generate_image(prompt)
        if error:
            return {"error": error}
        return {"image": img_b64}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/math")
async def solve_math(
    problem: str = Form(...),
    language: str = Form("English")
):
    async def generate():
        try:
            for delta in bot.solve_math(problem, language):
                yield f"data: {json.dumps({'type': 'delta', 'content': delta})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/api/code")
async def code_interpreter(
    query: str = Form(...),
    language: str = Form("English")
):
    async def generate():
        try:
            full_response = ""
            for delta in bot.answer_code(query, language):
                full_response += delta
                yield f"data: {json.dumps({'type': 'delta', 'content': delta})}\n\n"

            from code_executor import extract_python_code, execute_python_code, is_safe_code
            code = extract_python_code(full_response)
            if code:
                is_safe, reason = is_safe_code(code)
                if is_safe:
                    success, output = execute_python_code(code)
                    yield f"data: {json.dumps({'type': 'execution', 'success': success, 'output': output})}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/api/summarize")
async def summarize(
    topic: str = Form(...),
    language: str = Form("English")
):
    try:
        summary, source = bot.summarize_topic(topic, language)
        return {"summary": summary, "source": source}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/research")
async def research(
    topic: str = Form(...),
    language: str = Form("English")
):
    async def generate():
        try:
            for delta in bot.research_assistant(topic, language):
                yield f"data: {json.dumps({'type': 'delta', 'content': delta})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@app.get("/api/sessions")
async def get_sessions():
    try:
        from database import get_all_sessions
        return get_all_sessions()
    except Exception as e:
        return []

@app.post("/api/sessions")
async def create_new_session(name: str = Form("New Chat")):
    try:
        from database import create_session
        session_id = create_session(name)
        return {"id": session_id}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(session_id: int):
    try:
        from database import load_session_messages
        return load_session_messages(session_id)
    except Exception as e:
        return []

@app.delete("/api/sessions/{session_id}")
async def delete_session_endpoint(session_id: int):
    try:
        from database import delete_session
        delete_session(session_id)
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/clear-history")
async def clear_history():
    try:
        bot.clear_history()
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}