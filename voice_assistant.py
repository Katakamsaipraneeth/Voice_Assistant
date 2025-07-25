import streamlit as st

st.set_page_config( page_title ="Voice Assistant", layout = "wide")

# Libraries
import os
import time
import pyttsx3

from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
import av
import queue
import threading
import speech_recognition as sr
from groq import Groq
from dotenv import load_dotenv 

# Ensure the required libraries are installed
# Loading the api key from environment variables for safty purpose
load_dotenv()
Groq_Api_Key = os.getenv("Groq_Api_Key")

if not Groq_Api_Key:
    st.error("Please set the environment variable 'groq_api' with your Groq API key.")
    st.stop()

# Initialize Groq client
client = Groq(api_key=Groq_Api_Key)
MODEL = "llama-3.3-70b-versatile"

# Initialize speech recognizer
@st.cache_resource
def get_recognizer():
    return sr.Recognizer()
Recognizer = get_recognizer()

# Initialize text-to-speech engine
def get_tts_engine():
    try:
        engine = pyttsx3.init()
        return engine
    except Exception as e:
        st.error(f"Error initializing text-to-speech engine: {e}")
        return None

# Function to recognize speech
def speak(text, voice_gender="boy"):
    try:
        engine = get_tts_engine()
        if engine is None:
            return

        voices = engine.getProperty('voices')

        # Set voice explicitly based on gender
        for voice in voices:
            if voice_gender == "girl" and "zira" in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
            elif voice_gender == "boy" and "david" in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break

        engine.setProperty('rate', 200)   # Speed of speech
        engine.setProperty('volume', 0.8) # Volume (0.0 to 1.0)

        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        st.error(f"TTS error: {e}")

# Function to listen for speech
audio_queue = queue.Queue()

class AudioProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def recv(self, frame: av.AudioFrame):
        audio_data = frame.to_ndarray().flatten().astype("int16").tobytes()
        audio_queue.put(audio_data)
        return frame

    
# Connect with LLM model through Groq Cloud
def get_ai_response(messages):
    try:
        response = client.chat.completions.create(
        model = MODEL,
        messages = messages, 
        temperature = 0.7,
        )

        result = response.choices[0].message.content
        return result.strip() if result else "No response from AI"
    except Exception as e:
        return f"Error connecting to AI: {e}"
    
# Main function to run the voice assistant
def main():
    st.title("My Personal Voice Assistant")
    st.markdown("---")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "system", "content": "You are a helpful assistant. Reply only one line"}
             ]
    
    # Initialize session state for messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.header("Voice Assistant Settings")

        tts_enabled = st.checkbox("Enable Text-to-Speech", value=True)
    
        voice_gender = st.selectbox(
            "Voice Gender",
            options= ["girl", "boy"],
            index = 0,
            help = "Choose the voice"

        )
        webrtc_streamer(
    key="speech",
    mode=WebRtcMode.SENDONLY,
    audio_receiver_size=1024,
    client_settings=ClientSettings(
        media_stream_constraints={"audio": True, "video": False},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    ),
    audio_processor_factory=AudioProcessor,
)

if st.button("Transcribe", use_container_width=True):
    st.info("Listening... Please speak.")
    recognizer = sr.Recognizer()
    audio_data = b""
    
    while not audio_queue.empty():
        audio_data += audio_queue.get()
    
    try:
        with sr.AudioFile(sr.AudioData(audio_data, 16000, 2)) as source:
            audio = recognizer.record(source)
            user_input = recognizer.recognize_google(audio)
    except Exception as e:
        user_input = "Sorry, I couldn't understand."

    if user_input and user_input != "Sorry, I couldn't understand.":
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.spinner("Processing..."):
            ai_response = get_ai_response(st.session_state.chat_history)
            st.session_state.messages.append({"role": "user", "content": ai_response})
            st.session_state.chat_history.append({"role": "user", "content": ai_response})

        if tts_enabled:
            speak(ai_response, voice_gender)

        st.rerun()


        st.markdown("---")

        st.header("Chat History")
        user_text = st.text_input("Type your message here:", key="user_input")

        if st.button("Send", type="secondary", use_container_width=True) and user_text:
            st.session_state.messages.append({"role": "user", "content": user_text})
            st.session_state.chat_history.append({"role": "user", "content": user_text})

            # get ai response
            with st.spinner("Processing..."):
                ai_response = get_ai_response(st.session_state.chat_history)
                st.session_state.messages.append({"role": "user", "content": ai_response})# to pass conversation to LLM
                st.session_state.chat_history.append({"role": "user", "content": ai_response}) # for display data on screen


            # speak the reply if enabled
            if tts_enabled:
                speak(ai_response, voice_gender)

            st.rerun()
        
        st.markdown("---")
        # Clear chat history
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
            with st.chat_message("Assistant"):
                st.write(message["content"])
    

    # Welcome message
    if not st.session_state.chat_history:
        st.info("Welcome to your personal voice assistant! Speak or type your message to get started.")
    else:
        st.info("You can continue the conversation or clear the chat history using the sidebar options.")

    st.markdown("---")
    st.markdown("""
        <div style="text-align: center;">
            <p>Developed by <a href="https://praneethportfoli0.pythonanywhere.com/" target="_blank">Sai Praneeth</a></p>
            <p>Powered by GROQ AND Streamlit * Copyright 2025 . Made by Sai Praneeth</p
        </div>
        """,
        unsafe_allow_html=True
    )



if __name__== "__main__":
    main()
    
