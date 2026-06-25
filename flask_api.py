import os
from deep_translator import GoogleTranslator
from youtube_transcript_api import YouTubeTranscriptApi
from gtts import gTTS
from flask import request, jsonify
import base64
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"

from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

print("1")
from rag_pipeline import RAGChatbot
print("2")

from database import init_db
print("3")

init_db()
print("4")

bot = RAGChatbot()
print("5")

print("Flask API Ready!")

@app.route("/api/youtube-translate", methods=["POST"])
def youtube_translate():

    try:
        video_id = request.form.get("video_id")
        language = request.form.get("language")

        if not video_id:
            return jsonify({
                "error": "video_id missing"
            }), 400

        transcript = YouTubeTranscriptApi.get_transcript(
            video_id
        )

        full_text = " ".join(
            [x["text"] for x in transcript]
        )

        translator = Translator()

        translated = translator.translate(
            full_text,
            dest=language.lower()
        )

        return jsonify({
            "success": True,
            "translation": translated.text
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route("/")
def root():
    return jsonify({"status": "RAG Chatbot API Running"})

@app.route("/api/chat", methods=["POST"])
def chat():
    message = request.form.get("message", "")
    language = request.form.get("language", "English")
    session_id = request.form.get("session_id")

    def generate():
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
                if src: source = src
                if fups: followups = fups
                if conf is not None: confidence = conf
                if cits: citations = cits

            yield f"data: {json.dumps({'type': 'done', 'source': source, 'followups': followups, 'confidence': confidence, 'citations': citations})}\n\n"

            if session_id:
                from database import save_message
                save_message(int(session_id), "user", message)
                save_message(int(session_id), "assistant", full_response)

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")

@app.route("/api/web-search", methods=["POST"])
def web_search_endpoint():
    query = request.form.get("query", "")
    language = request.form.get("language", "English")

    try:
        from media_handler import web_search
        results = web_search(query)

        context = "\n\n".join([
            f"Result {i+1}:\nTitle: {r['title']}\nInfo: {r['snippet']}\nURL: {r['url']}"
            for i, r in enumerate(results)
        ]) if results else "No results found."

        response = bot.groq_call(
            [
                {"role": "system", "content": f"Answer in {language} using LIVE search results. Be direct."},
                {"role": "user", "content": f"Search results for '{query}':\n\n{context}\n\nAnswer: {query}"}
            ],
            temperature=0.0,
            max_tokens=512
        )
        return jsonify({
            "answer": response.choices[0].message.content,
            "results": results
        })
    except Exception as e:
        return jsonify({"error": str(e), "answer": f"Error: {str(e)}", "results": []})

@app.route("/api/upload-pdf", methods=["POST"])
def upload_pdf():
    try:
        import fitz
        from media_handler import build_index
        file = request.files["file"]
        content = file.read()
        doc = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()

        index, chunks = build_index(text, bot.embed_model)
        bot.current_pdf_index = index
        bot.current_pdf_chunks = chunks
        bot.current_pdf_name = file.filename

        return jsonify({"success": True, "filename": file.filename, "chunks": len(chunks)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/pdf-chat", methods=["POST"])
def pdf_chat():
    message = request.form.get("message", "")
    language = request.form.get("language", "English")

    if not hasattr(bot, 'current_pdf_index') or bot.current_pdf_index is None:
        return jsonify({"error": "No PDF uploaded"})

    def generate():
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

    return Response(stream_with_context(generate()), mimetype="text/event-stream")

@app.route("/api/generate-image", methods=["POST"])
def generate_image():
    prompt = request.form.get("prompt", "")
    try:
        img_b64, error = bot.generate_image(prompt)
        if error:
            return jsonify({"error": error})
        return jsonify({"image": img_b64})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/api/math", methods=["POST"])
def solve_math():
    problem = request.form.get("problem", "")
    language = request.form.get("language", "English")

    def generate():
        try:
            for delta in bot.solve_math(problem, language):
                yield f"data: {json.dumps({'type': 'delta', 'content': delta})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")

@app.route("/api/code", methods=["POST"])
def code_interpreter():
    query = request.form.get("query", "")
    language = request.form.get("language", "English")

    def generate():
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

    return Response(stream_with_context(generate()), mimetype="text/event-stream")

@app.route("/api/sessions", methods=["GET"])
def get_sessions():
    try:
        from database import get_all_sessions
        return jsonify(get_all_sessions())
    except Exception as e:
        return jsonify([])

@app.route("/api/sessions", methods=["POST"])
def create_new_session():
    try:
        from database import create_session
        name = request.form.get("name", "New Chat")
        session_id = create_session(name)
        return jsonify({"id": session_id})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/api/sessions/<int:session_id>/messages", methods=["GET"])
def get_session_messages(session_id):
    try:
        from database import load_session_messages
        return jsonify(load_session_messages(session_id))
    except Exception as e:
        return jsonify([])

@app.route("/api/sessions/<int:session_id>", methods=["DELETE"])
def delete_session_endpoint(session_id):
    try:
        from database import delete_session
        delete_session(session_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/api/clear-history", methods=["POST"])
def clear_history():
    try:
        bot.clear_history()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False, threaded=True)