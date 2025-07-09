import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from gtts import gTTS
import tempfile
import os

st.set_page_config(page_title="Voice Assistant", layout="wide")

# Load environment
load_dotenv()
Groq_Api_Key = st.secrets.get("Groq_Api_Key")

if not Groq_Api_Key:
    st.error("Missing Groq API Key. Please add it in Streamlit Cloud secrets.")
    st.stop()

client = Groq(api_key=Groq_Api_Key)
MODEL = "llama-3.3-70b-versatile"

# Text-to-speech using gTTS and streamlit.audio()
def speak(text):
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        
        st.success("✅ Audio generated!")
        st.audio(mp3_fp, format='audio/mp3', autoplay=True)
    except Exception as e:
        st.error(f"TTS error: {e}")

# Connect with LLM model through Groq Cloud
def get_ai_response(messages):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
        )
        result = response.choices[0].message.content
        return result.strip() if result else "No response from AI"
    except Exception as e:
        return f"Error connecting to AI: {e}"

# Main function
def main():
    st.title("My Personal Voice Assistant")
    st.markdown("---")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "system", "content": "You are a helpful assistant. Reply only one line"}
        ]

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.header("Voice Assistant Settings")

        tts_enabled = st.checkbox("Enable Text-to-Speech", value=True)

        voice_gender = st.selectbox(
            "Voice Gender",
            options=["girl", "boy"],
            index=0,
            help="Choose the voice"
        )

        user_text = st.text_input("Type your message here:", key="user_input")

        if st.button("Send", type="primary", use_container_width=True) and user_text:
            st.session_state.messages.append({"role": "user", "content": user_text})
            st.session_state.chat_history.append({"role": "user", "content": user_text})

            with st.spinner("Processing..."):
                ai_response = get_ai_response(st.session_state.chat_history)
                st.session_state.messages.append({"role": "user", "content": ai_response})
                st.session_state.chat_history.append({"role": "user", "content": ai_response})

            if tts_enabled:
                speak(ai_response)

            st.rerun()

        st.markdown("---")

        if st.button("Clear Chat History", type="secondary", use_container_width=True):
            st.session_state.chat_history = [
                {"role": "system", "content": "You are a helpful assistant. Reply only one line"}
            ]
            st.session_state.messages = []
            st.rerun()

    st.subheader("Chat History")
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])

    st.info("Welcome to your personal voice assistant! Type your message to get started.")

    st.markdown("---")
    st.markdown("""
        <div style="text-align: center;">
            <p>Developed by <a href="https://praneethportfoli0.pythonanywhere.com/" target="_blank">Sai Praneeth</a></p>
            <p>Powered by GROQ AND Streamlit * Copyright 2025 . Made by Sai Praneeth</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
