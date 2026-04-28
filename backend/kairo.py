import speech_recognition as sr
import requests
import subprocess
from browser import get_news, search_jobs, close_browser, search_and_show, open_specific_site

KAIRO_API = "http://127.0.0.1:8000/chat"

CHAT_ONLY_PHRASES = [
    "how are you", "what are you", "who are you", "tell me about yourself",
    "what can you do", "are you", "do you", "what do you think",
    "i am", "i'm", "i feel", "i need help", "help me",
    "what should i", "suggest me", "give me advice", "motivate me",
    "good morning", "good night", "good evening", "hello", "hi kairo",
    "hey kairo", "thank you", "thanks", "okay", "yes", "no", "great",
    "nice", "cool", "wow", "i'm stressed", "i'm tired", "i'm bored",
    "kaise ho", "kaisa hai", "shukriya", "dhanyawad", "kem cho"
]

def speak(text):
    print(f"\nKAIRO: {text}\n")
    clean_text = text.replace('"', '').replace("'", '')
    command = f'Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Rate = 2; $s.Speak("{clean_text}")'
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

def extract_job_details(user_input):
    text = user_input.lower()

    job_roles = [
        "data entry", "software tester", "quality assurance", "qa tester",
        "react developer", "frontend developer", "backend developer",
        "full stack developer", "python developer", "java developer",
        "web developer", "android developer", "ios developer",
        "data analyst", "data scientist", "machine learning",
        "devops", "cloud engineer", "ui ux", "graphic designer",
        "content writer", "digital marketing", "business analyst",
        "project manager", "product manager", "hr", "accountant"
    ]

    locations = [
        "mumbai", "pune", "delhi", "bangalore", "hyderabad", "chennai",
        "kolkata", "ahmedabad", "navi mumbai", "thane", "noida",
        "gurgaon", "remote", "work from home", "wfh"
    ]

    detected_role = None
    detected_location = None

    for role in job_roles:
        if role in text:
            detected_role = role
            break

    for location in locations:
        if location in text:
            detected_location = location
            break

    if not detected_role:
        prompt = f"What job role is this person looking for? Reply with ONLY the job role title, nothing else. Sentence: '{user_input}'"
        response = requests.post(KAIRO_API, json={"message": prompt})
        detected_role = response.json()["response"].strip().split("\n")[0]

    if not detected_location:
        detected_location = "Mumbai"

    print(f"Detected role: {detected_role} | Location: {detected_location}")
    return detected_role, detected_location

def extract_search_query(user_input):
    prompt = f"Convert this spoken request into a short Google search query. Reply with ONLY the search query, nothing else: '{user_input}'"
    response = requests.post(KAIRO_API, json={"message": prompt})
    query = response.json()["response"].strip().replace('"', '')
    return query

def extract_url(user_input):
    text = user_input.lower()
    
    # Clean up the input to get just the site name
    site_name = text.replace("open", "").replace("go to", "") \
                    .replace("visit", "").replace("launch", "") \
                    .replace("website", "").replace("for me", "") \
                    .replace("the", "").replace("site", "") \
                    .replace("please", "").strip()
    
    return site_name  # return the name, browser will Google it

def needs_browser(text):
    text = text.lower()
    for phrase in CHAT_ONLY_PHRASES:
        if phrase in text:
            return False
    browser_triggers = [
        "search", "find", "look up", "open", "show me", "news",
        "job", "weather", "price", "latest", "current", "today",
        "what is happening", "who is", "what is", "how to",
        "vacancy", "hiring", "headlines", "go to", "visit", "launch"
    ]
    for trigger in browser_triggers:
        if trigger in text:
            return True
    return False

def handle_input(user_input):
    text = user_input.lower()

    if not needs_browser(text):
        reply = ask_kairo(user_input)
        speak(reply)
        return

    if any(word in text for word in ["news", "headlines", "what's happening", "current world"]):
        speak("On it Abhishek, opening the news right now.")
        results = get_news()
        if results and len(results) > 50:
            summary = ask_kairo(f"Summarize these news headlines naturally for Abhishek in 4 sentences: {results}")
            speak(summary)
        else:
            speak("News tabs are open on your screen, take a look!")

    elif any(word in text for word in ["job", "opening", "vacancy", "hiring", "recruitment", "position"]):
        role, location = extract_job_details(user_input)
        speak(f"Sure! Searching {role} openings in {location} for you right now.")
        results = search_jobs(role, location)
        if results and len(results) > 50:
            summary = ask_kairo(f"Summarize these {role} job listings conversationally for Abhishek in 4 sentences: {results}")
            speak(summary)
        else:
            speak(f"I have opened the job portals for {role} jobs. Check the screen!")

    elif any(word in text for word in ["open", "go to", "visit", "launch"]):
        url = extract_url(user_input)
        site_name = url.replace("https://", "").replace("www.", "").split("/")[0]
        speak(f"Opening {site_name} for you.")
        try:
            results = open_specific_site(url, site_name)
            if results and len(results) > 30:
                summary = ask_kairo(f"Briefly describe what is on {site_name} based on: {results}")
                speak(summary)
        except Exception as e:
            speak(f"Opened {site_name} for you. Take a look at the screen!")

    else:
        query = extract_search_query(user_input)
        speak("Let me pull that up for you.")
        results = search_and_show(query)
        if results and len(results) > 50:
            summary = ask_kairo(f"Answer this conversationally for Abhishek in 4 sentences: '{user_input}'. Results: {results}")
            speak(summary)
        else:
            speak("Results are on your Chrome screen. Take a look!")

def main():
    print("=" * 40)
    print("   KAIRO - Personal AI Assistant")
    print("=" * 40)
    speak("KAIRO online. Good to see you Abhishek. How can I help you today?")

    while True:
        try:
            user_input = listen()
            if not user_input:
                continue

            if user_input.lower().strip() in ["exit", "quit", "bye kairo", "goodbye kairo"]:
                speak("Goodbye Abhishek. I will be here when you need me!")
                break

            if any(word in user_input.lower() for word in ["close browser", "close chrome", "close the browser"]):
                close_browser()
                speak("Browser closed. What else can I do for you?")
                continue

            handle_input(user_input)

        except KeyboardInterrupt:
            speak("Shutting down. Take care Abhishek!")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue

if __name__ == "__main__":
    main()