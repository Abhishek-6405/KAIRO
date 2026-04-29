import speech_recognition as sr
import time

# Global flag to pause wake word detection during conversation
is_busy = False

def listen_for_wake_word(callback):
    """Listen for 'Hey KAIRO' wake word continuously"""
    global is_busy
    
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 0.5
    recognizer.energy_threshold = 3000
    
    print("👂 KAIRO is in background — say 'Hey KAIRO' to wake him up")
    
    while True:
        # Don't listen for wake word while KAIRO is busy
        if is_busy:
            time.sleep(0.5)
            continue
            
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)
            
            try:
                text = recognizer.recognize_google(audio).lower().strip()
                print(f"Heard: {text}")
                
                wake_words = [
                    "hey kairo", "hi kairo", "okay kairo", "ok kairo",
                    "kairo", "cairo", "hey cairo", "hi cairo",
                    "hey kayro", "kayro", "hey karo", "karo",
                    "hey kay", "he kairo", "he cairo",
                    "he kayro", "hey kai", "kai ro",
                    "a kairo", "hey kyro", "kyro"
                ]
                
                if any(wake in text for wake in wake_words):
                    print("🔥 Wake word detected!")
                    is_busy = True
                    time.sleep(0.5)  # let mic release
                    callback()
                    time.sleep(0.5)  # let mic release after conversation
                    is_busy = False
                    print("\n👂 KAIRO back in background — say 'Hey KAIRO' again")

                elif any(w in text for w in ["kai", "karo", "kayro", "cairo", "kyro"]):
                    print("🔥 Wake word detected!")
                    is_busy = True
                    time.sleep(0.5)
                    callback()
                    time.sleep(0.5)
                    is_busy = False
                    print("\n👂 KAIRO back in background — say 'Hey KAIRO' again")
            except sr.UnknownValueError:
                pass
            except sr.RequestError:
                pass
                
        except Exception as e:
            pass
        
        time.sleep(0.1)