live project link : https://voiceassistant-gn8eytfqkbqfjqtapgkcma.streamlit.app/

🗣️ Personal Voice Assistant using Streamlit + Groq
This project is a voice-enabled personal assistant built using Streamlit, Groq LLM, SpeechRecognition, and Text-to-Speech (pyttsx3). It allows users to interact through voice or text, and get concise AI-generated responses spoken back to them.

🔥 Key Features
🎤 Voice Input: Speak your queries via microphone

💬 Chat Interface: Type and view conversations

🧠 AI-Powered Responses: Integrated with Groq’s LLM (llama-3.3-70b-versatile)

🗣️ Text-to-Speech: AI responses are spoken back

🧑‍💻 Custom Voice Settings: Choose between male or female voice

🧹 Clear Chat History: Reset conversation at any time

🌐 Streamlit UI: Responsive and intuitive web-based interface

🚀 Getting Started
📦 Prerequisites
Python 3.8+

Groq API key (required for LLM access)

Microphone access enabled

🔧 Installation
bash
Copy
Edit
# Clone the repository
git clone https://github.com/your-username/streamlit-voice-assistant.git
cd streamlit-voice-assistant

# Install dependencies
pip install -r requirements.txt
Create a .env file to store your Groq API key:

ini
Copy
Edit
Groq_Api_Key=your_groq_api_key_here
▶️ Running the App
Start the Streamlit app:

bash
Copy
Edit
streamlit run voice_assistant.py
🧠 How It Works
1. 🎙️ Voice Input
The assistant uses speech_recognition to capture and transcribe spoken text using your system's microphone.

2. 🔗 Integration with Groq
It sends your input to Groq’s LLM to get a smart and concise reply.

3. 📢 Text-to-Speech
The reply is read aloud using pyttsx3, and the voice can be adjusted via the sidebar.

4. 💬 Interactive Chat UI
All interactions are stored and displayed in a scrollable chat window, with the ability to reset the conversation.

📁 Project Structure
bash
Copy
Edit
.
├── voice_assistant.py     # Main Streamlit app
├── .env                   # Environment variable with Groq API key
├── README.md              # Project documentation
└── requirements.txt       # Python dependencies
📦 Dependencies
streamlit

speechrecognition

pyttsx3

groq

python-dotenv

Install them with:

bash
Copy
Edit
pip install streamlit speechrecognition pyttsx3 groq python-dotenv
🧪 Example Usage
✅ Start the app

🎤 Press "Start voice input" to speak a message

💬 Or type a message in the text box

🧠 The assistant replies concisely using Groq LLM

🔊 The reply is spoken out if TTS is enabled

♻️ Use Clear Chat History to reset

👤 Developed By
Sai Praneeth
Made with ❤️ using Streamlit and Groq

📜 License
This project is licensed under the MIT License – feel free to use, modify, and share!
