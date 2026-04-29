import speech_recognition as sr
import requests
import subprocess
import sys
from browser import get_news, search_jobs, close_browser, search_and_show, open_specific_site
from commands import (open_app, close_app, get_battery, get_time,
                      volume_up, volume_down, volume_mute,
                      take_screenshot, get_system_info,
                      lock_pc, shutdown_pc, restart_pc, cancel_shutdown)

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
        "qa engineer", "react developer", "react.js", "frontend developer",
        "front end developer", "backend developer", "full stack developer",
        "fullstack developer", "python developer", "java developer",
        "web developer", "android developer", "ios developer",
        "data analyst", "data scientist", "machine learning", "ml engineer",
        "devops", "cloud engineer", "ui ux", "graphic designer",
        "content writer", "digital marketing", "business analyst",
        "project manager", "product manager", "hr", "accountant",
        "software developer", "software engineer", "fresher developer",
        "fresher engineer", "junior developer", "junior engineer",
        "node developer", "node.js", "mern", "mean", "php developer",
        "laravel developer", "django developer", "flask developer",
        "manual tester", "automation tester", "selenium tester"
    ]

    locations = [
        "mumbai", "pune", "delhi", "bangalore", "hyderabad", "chennai",
        "kolkata", "ahmedabad", "navi mumbai", "thane", "noida",
        "gurgaon", "remote", "work from home", "wfh", "anywhere"
    ]

    detected_role = None
    detected_location = None

    # Detect role directly from text
    for role in job_roles:
        if role in text:
            detected_role = role
            break

    # Detect location directly from text
    for location in locations:
        if location in text:
            detected_location = location
            break

    # If role still not found — extract key words manually
    if not detected_role:
        # Remove common filler words and extract what's left
        filler = ["show", "me", "find", "search", "look", "for", "a", "an",
                  "the", "current", "openings", "opening", "jobs", "job",
                  "vacancy", "vacancies", "hiring", "fresher", "freshers",
                  "position", "positions", "in", "at", "on", "please",
                  "can", "you", "could", "would", "i", "want", "need"]
        words = [w for w in text.split() if w not in filler]
        detected_role = " ".join(words[:3]).strip() if words else "software developer"

    if not detected_location:
        detected_location = "Mumbai"

    # Clean up role — remove any punctuation
    detected_role = detected_role.replace("!", "").replace("?", "").replace(",", "").strip()

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

def handle_pc_command(text):
    """Handle PC control commands - returns True if handled"""

    # Time and date
    if any(w in text for w in ["what time", "what's the time", "current time", "what date", "today's date"]):
        speak(get_time())
        return True

    # Battery
    if any(w in text for w in ["battery", "charge", "charging"]):
        speak(get_battery())
        return True

    # Volume
    if any(w in text for w in ["volume up", "increase volume", "louder"]):
        speak(volume_up())
        return True
    if any(w in text for w in ["volume down", "decrease volume", "quieter", "lower volume"]):
        speak(volume_down())
        return True
    if any(w in text for w in ["mute", "silence"]):
        speak(volume_mute())
        return True

    # Screenshot
    if any(w in text for w in ["screenshot", "screen capture", "capture screen", "take a screen", "take screen"]):
        result = take_screenshot()
        speak(result)
        return True

    # System info
    if any(w in text for w in ["system info", "cpu", "ram usage", "memory usage"]):
        speak(get_system_info())
        return True

    # Lock PC
    if any(w in text for w in ["lock pc", "lock computer", "lock the pc"]):
        speak(lock_pc())
        return True

    # Shutdown
    if any(w in text for w in ["shutdown", "shut down", "turn off pc"]):
        speak(shutdown_pc())
        return True

    # Restart
    if any(w in text for w in ["restart", "reboot"]):
        speak(restart_pc())
        return True

    # Cancel shutdown
    if any(w in text for w in ["cancel shutdown", "cancel restart", "abort shutdown"]):
        speak(cancel_shutdown())
        return True

    # Open app
    # Open app — only trigger if it's clearly an app, not a website or search
    if any(w in text for w in ["open", "launch", "start"]):
        app_name = text.replace("open", "").replace("launch", "") \
                   .replace("start", "").replace("the", "") \
                   .replace("app", "").replace("application", "") \
                   .replace("for me", "").strip()
    
    # Skip if it looks like a browser/search/job request
        skip_words = ["website", "browser", "google", "search", "show me",
                        "opening", "openings", "vacancy", "job", "news",
                        "youtube", "netflix", "instagram", "facebook",
                        "twitter", "linkedin", "naukri", "amazon", "flipkart"]
    
        if app_name and not any(w in text for w in skip_words):
            result = open_app(app_name)
        # Only speak if it's not an error from PowerShell fallback
            if "Trying to open" not in result:
                speak(result)
                return True
            else:
                return False  # let handle_input take over

    # Close app
    if any(w in text for w in ["close", "exit", "kill"]):
        app_name = text.replace("close", "").replace("exit", "") \
                       .replace("kill", "").replace("the", "") \
                       .replace("app", "").replace("for me", "").strip()
        if app_name:
            speak(close_app(app_name))
            return True

    return False  # not a PC command

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

    # News
    if any(word in text for word in ["news", "headlines", "what's happening", "current world"]):
        speak("On it Abhishek, opening the news right now.")
        results = get_news()
        if results and len(results) > 50:
            summary = ask_kairo(f"""Here are the news headlines found: {results}
Summarize ONLY the actual news found. Tell Abhishek:
1. Top 3 to 4 headlines
2. One line about each headline
Do NOT add any suggestions or extra info. Only what is in the data.""")
            speak(summary)
        else:
            speak("News tabs are open on your screen, take a look!")

    # Jobs
    elif any(word in text for word in ["job", "opening", "vacancy", "hiring", "recruitment", "position"]):
        role, location = extract_job_details(user_input)
        speak(f"Sure! Searching {role} openings in {location} for you right now.")
        results = search_jobs(role, location)
        if results and len(results) > 50:
            summary = ask_kairo(f"""Abhishek is looking for {role} jobs in {location}.
Here are the job listings found: {results}
Summarize ONLY the actual jobs found. Tell him:
1. How many jobs were found
2. Company names and job titles
3. Any salary info if available
Do NOT add any suggestions or extra info. Only what is in the data.""")
            speak(summary)
        else:
            speak(f"I have opened LinkedIn, Naukri and Internshala for {role} jobs in {location}. Check the screen!")

    # Open specific website
    elif any(word in text for word in ["open", "go to", "visit", "launch"]):
        url = extract_url(user_input)
        site_name = url.replace("https://", "").replace("www.", "").split("/")[0]
        speak(f"Opening {site_name} for you.")
        try:
            results = open_specific_site(url, site_name)
            if results and len(results) > 30:
                summary = ask_kairo(f"""Here is the content from {site_name}: {results}
Summarize ONLY what is actually on the page.
Do NOT add suggestions or extra info.""")
                speak(summary)
        except Exception as e:
            speak(f"Opened {site_name} for you. Take a look at the screen!")

    # Everything else
    else:
        query = extract_search_query(user_input)
        speak("Let me pull that up for you.")
        results = search_and_show(query)
        if results and len(results) > 50:
            summary = ask_kairo(f"""Abhishek asked: '{user_input}'
Here are the search results found: {results}
Answer his question using ONLY the data above.
Keep it to 3 to 4 sentences.
Do NOT add suggestions or extra info.""")
            speak(summary)
        else:
            speak("Results are on your Chrome screen. Take a look!")

def run_assistant_once():
    """Listen once and respond then go back to wake word mode"""
    try:
        user_input = listen()
        if not user_input:
            return

        if user_input.lower().strip() in ["exit", "quit", "bye kairo", "goodbye kairo"]:
            speak("Goodbye Abhishek. I will be here when you need me!")
            return

        if any(word in user_input.lower() for word in ["close browser", "close chrome", "close the browser"]):
            close_browser()
            speak("Browser closed. What else can I do for you?")
            return

        if handle_pc_command(user_input.lower()):
            return

        handle_input(user_input)

    except Exception as e:
        print(f"Error: {e}")

def run_assistant():
    """Full conversation loop"""
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

            if handle_pc_command(user_input.lower()):
                continue

            handle_input(user_input)

        except KeyboardInterrupt:
            speak("Shutting down. Take care Abhishek!")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue

def on_wake():
    speak("Yes Abhishek, I am listening.")
    
    # Keep listening until Abhishek says goodbye or is silent
    while True:
        try:
            user_input = listen()
            if not user_input:
                continue

            if user_input.lower().strip() in ["exit", "quit", "bye kairo", 
                                               "goodbye kairo", "goodbye",
                                               "that's all", "stop", "thanks kairo"]:
                speak("Alright Abhishek, going back to sleep. Say Hey KAIRO when you need me!")
                break

            if any(word in user_input.lower() for word in ["close browser", "close chrome", "close the browser"]):
                close_browser()
                speak("Browser closed. Anything else?")
                continue

            if handle_pc_command(user_input.lower()):
                continue

            handle_input(user_input)

        except Exception as e:
            print(f"Error: {e}")
            break

def main():
    print("=" * 40)
    print("   KAIRO - Personal AI Assistant")
    print("=" * 40)

    if "--nowake" in sys.argv:
        speak("KAIRO online. Good to see you Abhishek. How can I help you today?")
        run_assistant()
    else:
        print("KAIRO running in background...")
        print("Say 'Hey KAIRO' to wake him up!")
        print("Or run with --nowake to skip wake word\n")

        try:
            from wakeword import listen_for_wake_word

            def on_wake():
                speak("Yes Abhishek, I am listening.")
                
                while True:
                    try:
                        user_input = listen()
                        if not user_input:
                            continue

                        if user_input.lower().strip() in ["exit", "quit", "bye kairo",
                                                          "goodbye kairo", "goodbye",
                                                          "that's all", "stop",
                                                          "thanks kairo", "thank you kairo"]:
                            speak("Alright Abhishek, going back to sleep. Say Hey KAIRO when you need me!")
                            break

                        if any(word in user_input.lower() for word in ["close browser", "close chrome", "close the browser"]):
                            close_browser()
                            speak("Browser closed. Anything else?")
                            continue

                        if handle_pc_command(user_input.lower()):
                            continue

                        handle_input(user_input)

                    except KeyboardInterrupt:
                        raise
                    except Exception as e:
                        print(f"Error: {e}")
                        continue

            listen_for_wake_word(on_wake)

        except KeyboardInterrupt:
            speak("Shutting down. Take care Abhishek!")
        except Exception as e:
            print(f"Error: {e}")
            print("Starting in direct mode...")
            speak("KAIRO online. How can I help you Abhishek?")
            run_assistant()

if __name__ == "__main__":
    main()

# if __name__ == "__main__":
#     main()