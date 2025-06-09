import streamlit as st
import requests
import speech_recognition as sr
import tempfile
import pyttsx3

# Groq setup from Streamlit secrets
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-8b-8192"

# Chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": "You are a smart coding assistant. Help users with code suggestions, debugging, explanations, and test generation in a polite and clear manner."}
    ]

def get_groq_response(messages):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": 800
    }
    try:
        res = requests.post(GROQ_API_URL, headers=headers, json=payload)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Error: {e}"

def transcribe_audio(file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except Exception:
        return "Sorry, could not understand the audio."

def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

st.set_page_config(page_title="✨ Coding Copilot", page_icon="💡", layout="wide")

st.sidebar.title("⚙️ Settings")
theme = st.sidebar.radio("Theme", ["🌞 Light", "🌙 Dark"])
task = st.sidebar.selectbox("Task", ["Code Suggestion", "Debugging", "Code Explanation", "Test Generation", "Chat"])
tts_enabled = st.sidebar.checkbox("🔊 Speak Responses")

st.markdown("<h1 style='text-align:center; font-size:3em;'>💻 Ultra Coding Copilot</h1>", unsafe_allow_html=True)

st.markdown("### 🎙️ Speak to Your Copilot")
audio_file = st.file_uploader("Upload your voice (WAV)", type=["wav"])
if audio_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_file.read())
        transcribed = transcribe_audio(tmp.name)
        st.success("📜 Transcription: " + transcribed)
        if st.button("🎤 Submit Voice"):
            st.session_state.chat_history.append({"role": "user", "content": transcribed})
            result = get_groq_response(st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "assistant", "content": result})
            if tts_enabled:
                speak_text(result)

st.markdown("### 💬 Type Your Code or Question")
user_input = st.text_input("Ask or paste your code here...")
if st.button("🧠 Submit Text"):
    prompt_map = {
        "Code Suggestion": f"Suggest code to continue:\n{user_input}",
        "Debugging": f"Debug and explain issues in the code:\n{user_input}",
        "Code Explanation": f"Explain this code:\n{user_input}",
        "Test Generation": f"Generate test cases for this code:\n{user_input}",
        "Chat": user_input
    }
    st.session_state.chat_history.append({"role": "user", "content": prompt_map[task]})
    result = get_groq_response(st.session_state.chat_history)
    st.session_state.chat_history.append({"role": "assistant", "content": result})
    if tts_enabled:
        speak_text(result)

st.markdown("### 🗂️ Your Copilot Conversation")
for msg in st.session_state.chat_history[1:]:
    if msg["role"] == "user":
        st.markdown(f"<div style='padding:10px;border-radius:8px;background:#2b2b4f;margin:5px 0'><b>👤 You:</b><br>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='padding:10px;border-radius:8px;background:#44475a;margin:5px 0'><b>🤖 Copilot:</b><br>{msg['content']}</div>", unsafe_allow_html=True)