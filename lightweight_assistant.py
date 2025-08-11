# lightweight_assistant.py - Ultra lekka wersja

import speech_recognition as sr
import pyttsx3
import threading
import time
import requests

class SimplestAssistant:
    def __init__(self):
        # Najprostsze ustawienia
        self.r = sr.Recognizer()
        self.r.energy_threshold = 4000  # Wyższa = mniej czuły
        self.r.pause_threshold = 1.0
        
        self.mic = sr.Microphone()
        
        # TTS
        self.tts = pyttsx3.init()
        self.tts.setProperty('rate', 200)
        
        # Kalibracja
        with self.mic as source:
            self.r.adjust_for_ambient_noise(source)
        
        self.listening = False
        print("💬 Powiedz 'hej' aby aktywować")
    
    def speak(self, text):
        """Najprostsza synteza"""
        print(f"🤖: {text}")
        self.tts.say(text)
        self.tts.runAndWait()
    
    def get_response(self, text):
        """Ultraszybka odpowiedź"""
        try:
            # Tylko lokalne, proste odpowiedzi
            text = text.lower()
            
            if "cześć" in text or "hej" in text:
                return "Cześć! Jak mogę pomóc?"
            elif "czas" in text or "godzina" in text:
                return f"Jest {time.strftime('%H:%M')}"
            elif "dzień" in text:
                return "Miłego dnia!"
            elif "imię" in text or "nazywasz" in text:
                return "Jestem twoim asystentem"
            else:
                # Tylko jeśli NAPRAWDĘ potrzeba Ollama
                try:
                    resp = requests.post('http://localhost:11434/api/generate',
                        json={'model': 'qwen2.5:0.5b', 'prompt': text, 'stream': False},
                        timeout=5)
                    return resp.json()['response'][:100] + "..."
                except:
                    return "Nie rozumiem. Spróbuj ponownie."
        except:
            return "Przepraszam, mam problem."
    
    def listen_once(self):
        """Jedna próba słuchania"""
        try:
            with self.mic as source:
                audio = self.r.listen(source, timeout=2, phrase_time_limit=3)
            
            text = self.r.recognize_google(audio, language='pl-PL')
            return text.lower()
        except:
            return None
    
    def run(self):
        """Prosta pętla"""
        while True:
            if not self.listening:
                # Czekaj na aktywację
                text = self.listen_once()
                if text and "hej" in text:
                    self.speak("Słucham")
                    self.listening = True
            else:
                # Słuchaj komendy
                text = self.listen_once()
                if text:
                    print(f"👤: {text}")
                    
                    if "stop" in text:
                        self.speak("Pa!")
                        break
                    
                    response = self.get_response(text)
                    self.speak(response)
                    self.listening = False  # Wyłącz po odpowiedzi

if __name__ == "__main__":
    SimplestAssistant().run()