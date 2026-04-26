import speech_recognition as sr
import requests
import subprocess
import tempfile
import os

KAIRO_API = "http://127.0.0.1:8000/chat"

def speak(text):
    print(f"\nKAIRO: {text}\n")
    # Use Windows built-in PowerShell TTS - works 100% always
    command = f'Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Rate = 2; $s.Speak("{text}")'
    subprocess.run(["powershell", "-Command", command], capture_output=True)

def listen():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("\n🎤 Listening... Speak now Abhishek")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        recognizer.pause_threshold = 2.0  # waits 2 seconds of silence before stopping
        recognizer.phrase_threshold = 0.3
        audio = recognizer.listen(source, timeout=15, phrase_time_limit=20)

    print("Processing your voice...")
    text = recognizer.recognize_google(audio)
    print(f"You said: {text}")
    return text

def ask_kairo(message):
    response = requests.post(KAIRO_API, json={"message": message})
    data = response.json()
    return data["response"]

def main():
    print("KAIRO Voice Mode Active")
    print("=" * 40)
    speak("KAIRO online. Good to see you Abhishek. How can I help you today?")

    while True:
        try:
            user_input = listen()
            if not user_input:
                continue

            if any(word in user_input.lower() for word in ["exit", "quit", "bye kairo"]):
                speak("Goodbye Abhishek. See you soon.")
                break

            print("KAIRO is thinking...")
            reply = ask_kairo(user_input)
            speak(reply)

        except KeyboardInterrupt:
            speak("Shutting down. Goodbye Abhishek.")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue

if __name__ == "__main__":
    main()