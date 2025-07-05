import os
import uuid
import queue
import numpy as np
import streamlit as st
from gtts import gTTS
from groq import Groq
from pathlib import Path
import pydub
import av
from deepspeech import Model
from streamlit_webrtc import WebRtcMode, webrtc_streamer

# Load API Key from Streamlit secrets
Groq_Api_Key = st.secrets.get("Groq_Api_Key")
if not Groq_Api_Key:
    st.error("Missing Groq API Key. Please add it in Streamlit Cloud secrets.")
    st.stop()

# Init Groq Client
client = Groq(api_key=Groq_Api_Key)
MODEL = "llama-3.3-70b-versatile"

# Load DeepSpeech model
MODEL_PATH = "models/deepspeech-0.9.3-models.pbmm"
SCORER_PATH = "models/deepspeech-0.9.3-models.scorer"
ds_model = Model(MODEL_PATH)
ds_model.enableExternalScorer(SCORER_PATH)
ds_model.setScorerAlphaBeta(0.931289039105002, 1.1834137581510284)
ds_model.setBeamWidth(100)

st.set_page_config(page_title="Voice Assistant", layout="wide")

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

def speak(text):
    try:
        tts = gTTS(text=text)
        filename = f"audio_{uuid.uuid4().hex}.mp3"
        tts.save(filename)
        st.audio(filename, format="audio/mp3", start_time=0)
    except Exception as e:
        st.error(f"TTS Error: {e}")

def transcribe_audio(audio_frames):
    sound_chunk = pydub.AudioSegment.empty()
    for audio_frame in audio_frames:
        audio = audio_frame.to_ndarray()
        segment = pydub.AudioSegment(
            data=audio.tobytes(),
            sample_width=audio_frame.format.bytes,
            frame_rate=audio_frame.sample_rate,
            channels=len(audio_frame.layout.channels),
        )
        sound_chunk += segment
    if len(sound_chunk) > 0:
        sound_chunk = sound_chunk.set_channels(1).set_frame_rate(ds_model.sampleRate())
        buffer = np.array(sound_chunk.get_array_of_samples())
        return ds_model.stt(buffer)
    return ""

def main():
    st.title("My Cloud-Compatible Voice Assistant")
    st.markdown("---")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{"role": "system", "content": "You are a helpful assistant. Reply only one line"}]
    
    tts_enabled = st.sidebar.checkbox("Enable TTS (Text to Speech)", value=True)

    # Mic input section
    st.subheader("🎙️ Speak Now")
    webrtc_ctx = webrtc_streamer(
        key="stt",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=1024,
        media_stream_constraints={"video": False, "audio": True},
    )

    if webrtc_ctx.audio_receiver:
        try:
            audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=3)
            if audio_frames:
                st.success("Voice received. Transcribing...")
                user_input = transcribe_audio(audio_frames)
                st.write(f"🧠 You said: **{user_input}**")

                if user_input:
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    ai_response = get_ai_response(st.session_state.chat_history)
                    st.session_state.chat_history.append({"role": "user", "content": ai_response})
                    st.write(f"🤖 Assistant: {ai_response}")
                    if tts_enabled:
                        speak(ai_response)
        except queue.Empty:
            st.warning("No audio received. Try again.")

    st.subheader("📜 Chat History")
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            with st.chat_message("user"): st.write(msg["content"])
        else:
            with st.chat_message("assistant"): st.write(msg["content"])

    st.sidebar.markdown("---")
    if st.sidebar.button("Clear History"):
        st.session_state.chat_history = [{"role": "system", "content": "You are a helpful assistant. Reply only one line"}]
        st.rerun()

    st.markdown("---")
    st.markdown("""
        <div style="text-align: center;">
            <p>Developed by <a href="https://praneethportfoli0.pythonanywhere.com/" target="_blank">Sai Praneeth</a></p>
            <p>Powered by GROQ & Streamlit. Copyright 2025.</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
