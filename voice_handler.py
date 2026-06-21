import os
import base64
import tempfile
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def transcribe_audio(audio_bytes):
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name

        with open(tmp_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=("recording.wav", audio_file, "audio/wav"),
                language="en"
            )

        os.unlink(tmp_path)
        return transcription.text.strip(), None

    except Exception as e:
        return None, str(e)

def text_to_speech_base64(text, lang="en"):
    try:
        from gtts import gTTS
        import io

        tts = gTTS(text=text[:500], lang=lang, slow=False)
        mp3_buffer = io.BytesIO()
        tts.write_to_fp(mp3_buffer)
        mp3_buffer.seek(0)

        audio_base64 = base64.b64encode(mp3_buffer.read()).decode("utf-8")
        return audio_base64, None

    except Exception as e:
        return None, str(e)

LANG_CODES = {
    "English": "en",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Arabic": "ar",
    "Chinese": "zh",
    "Japanese": "ja",
    "Portuguese": "pt",
    "Telugu": "te",
    "Tamil": "ta"
}