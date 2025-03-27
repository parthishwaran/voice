from flask import Flask, render_template, jsonify
from flask_cors import CORS
import speech_recognition as sr
import google.generativeai as genai
import pyttsx3
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty("rate", 150)

def get_ai_response(user_input=None):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        if user_input:
            prompt = f"Respond concisely to this: {user_input}"
        else:
            prompt = "Greet me and ask what I'd like to discuss today. Keep it under 2 sentences."
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"AI Error: {str(e)}"

def recognize_speech():
    recognizer = sr.Recognizer()
    source = None
    try:
        source = sr.Microphone()
        with source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            text = recognizer.recognize_google(audio)
            return text
    except sr.WaitTimeoutError:
        return "No speech detected"
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as e:
        return f"Speech service error: {str(e)}"
    except Exception as e:
        return f"Recognition error: {str(e)}"
    finally:
        if source:
            try:
                source.__exit__(None, None, None)
            except:
                pass

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/first_message")
def first_message():
    try:
        ai_response = get_ai_response()  # Get initial greeting
        return jsonify({
            "status": "success",
            "ai_message": ai_response
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Server error: {str(e)}"
        })

@app.route("/voice", methods=["POST"])
def voice_chat():
    try:
        user_input = recognize_speech()
        
        if any(error_keyword in user_input.lower() 
               for error_keyword in ["error", "sorry", "no speech", "could not"]):
            return jsonify({
                "status": "error",
                "type": "recognition",
                "message": user_input
            })

        ai_response = get_ai_response(user_input)
        
        return jsonify({
            "status": "success",
            "user_message": user_input,
            "ai_message": ai_response
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "type": "server",
            "message": f"Server error: {str(e)}"
        })

if __name__ == "__main__":
    app.run(debug=True, port=5000)