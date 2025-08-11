import speech_recognition as sr
import pyttsx3
import requests
import threading
import time

class SimpleAssistant:
    def __init__(self):
        print("🤖 Inicjalizacja asystenta...")
        
        # Speech Recognition
        self.r = sr.Recognizer()
        self.r.energy_threshold = 300
        self.r.pause_threshold = 0.8
        self.mic = sr.Microphone()
        
        # Kalibracja mikrofonu
        print("🎤 Kalibracja mikrofonu...")
        with self.mic as source:
            self.r.adjust_for_ambient_noise(source, duration=1)
        
        # TTS Setup
        self.tts = pyttsx3.init()
        self.tts.setProperty('rate', 180)
        self.tts.setProperty('volume', 0.9)
        
        # Status
        self.is_speaking = False
        self.wake_mode = True
        self.listening = False
        
        print("✅ Asystent gotowy!")
        print("💬 Powiedz 'hej mercedes' aby aktywować")
    
    def speak_async(self, text):
        """Mów w osobnym wątku"""
        def _speak():
            self.is_speaking = True
            print(f"🤖: {text}")
            try:
                self.tts.say(text)
                self.tts.runAndWait()
            finally:
                self.is_speaking = False
        
        thread = threading.Thread(target=_speak, daemon=True)
        thread.start()
        return thread
    
    def listen_once(self, timeout=2):
        """Jednorazowe słuchanie"""
        try:
            with self.mic as source:
                print("🎤 Słucham...", end="", flush=True)
                audio = self.r.listen(source, timeout=timeout, phrase_time_limit=4)
                print("\r🎤 Przetwarzam...", end="", flush=True)
            
            text = self.r.recognize_google(audio, language='pl-PL')
            print(f"\r👤: {text}")
            return text.lower().strip()
            
        except sr.WaitTimeoutError:
            print("\r⏱️ Timeout")
            return None
        except sr.UnknownValueError:
            print("\r❓ Nie rozpoznano")  
            return None
        except Exception as e:
            print(f"\r❌ Błąd: {e}")
            return None
    
    def get_ollama_response(self, text):
        """Odpowiedź z Ollama"""
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'qwen2.5:0.5b',
                    'prompt': f"Odpowiedz krótko (max 20 słów): {text}",
                    'stream': False,
                    'options': {'num_predict': 30}
                },
                timeout=8
            )
            
            if response.status_code == 200:
                return response.json()['response'].strip()
            else:
                return "Mam problem z odpowiedzią."
                
        except Exception as e:
            print(f"❌ Ollama error: {e}")
            return "Przepraszam, nie mogę odpowiedzieć."
    
    def run(self):
        """Główna pętla"""
        print("\n" + "="*40)
        print("🎤 ASYSTENT AKTYWNY")
        print("="*40)
        
        try:
            while True:
                # Sprawdź czy nie mówi
                if self.is_speaking:
                    time.sleep(0.5)
                    continue
                
                # Słuchaj
                text = self.listen_once(timeout=1 if not self.listening else 3)
                
                if not text:
                    continue
                
                # Wake word detection
                if self.wake_mode and not self.listening:
                    if "hej mercedes" in text or "mercedes" in text:
                        print("🔥 Aktywacja!")
                        self.speak_async("Słucham!")
                        self.listening = True
                        time.sleep(2)  # Poczekaj na skończenie mowy
                    continue
                
                # Komendy systemowe
                if "stop" in text or "zakończ" in text:
                    self.speak_async("Pa pa!")
                    time.sleep(2)
                    break
                
                if "tryb ciągły" in text:
                    self.wake_mode = False
                    self.listening = True
                    self.speak_async("Tryb ciągły włączony")
                    continue
                
                if "tryb wake" in text or "tryb aktywacji" in text:
                    self.wake_mode = True
                    self.listening = False
                    self.speak_async("Tryb aktywacji włączony")
                    continue
                
                # Normalna odpowiedź
                if self.listening or not self.wake_mode:
                    print("🤔 Myślę...")
                    response = self.get_ollama_response(text)
                    
                    # Mów odpowiedź
                    speech_thread = self.speak_async(response)
                    
                    # W trybie wake word - dezaktywuj po odpowiedzi
                    if self.wake_mode:
                        def deactivate():
                            speech_thread.join()  # Poczekaj na koniec mowy
                            time.sleep(0.5)
                            self.listening = False
                            print("💤 Dezaktywacja - powiedz 'hej mercedes'")
                        
                        threading.Thread(target=deactivate, daemon=True).start()
                
        except KeyboardInterrupt:
            print("\n👋 Kończę pracę...")
        except Exception as e:
            print(f"\n❌ Błąd: {e}")

def main():
    # Test Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        print("✅ Ollama działa")
    except:
        print("❌ Ollama nie działa! Uruchom: ollama serve")
        return
    
    # Uruchom asystenta
    assistant = SimpleAssistant()
    assistant.run()

if __name__ == "__main__":
    main()