import speech_recognition as sr
import pyttsx3
import requests
import json
import threading
import queue
import time
from collections import deque
import numpy as np

class VoiceAssistant:
    def __init__(self):
        # Konfiguracja
        self.WAKE_WORD = "hej mercedes"
        self.wake_mode_active = True  # True = aktywacja frazą, False = ciągłe słuchanie
        self.is_listening = False
        self.is_speaking = False
        
        # Kolejka do komunikacji między wątkami
        self.audio_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
        # Inicjalizacja komponentów
        self.setup_speech_recognition()
        self.setup_tts()
        self.setup_ollama()
        
        print("🤖 Asystent gotowy!")
        if self.wake_mode_active:
            print(f"💬 Powiedz '{self.WAKE_WORD}' aby aktywować")
        else:
            print("🎤 Słucham ciągle...")
    
    def setup_speech_recognition(self):
        """Konfiguracja rozpoznawania mowy - bardziej wydajne ustawienia"""
        self.recognizer = sr.Recognizer()
        
        # Optymalizacja dla lepszej wydajności
        self.recognizer.energy_threshold = 100  # Próg energii (niższy = bardziej czuły)
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8  # Krótsze pauzy
        self.recognizer.phrase_threshold = 0.3  # Szybsze wykrywanie początku mowy
        
        # Mikrofon
        self.microphone = sr.Microphone()
        
        # Kalibracja szumu otoczenia
        print("🎤 Kalibracja mikrofonu...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("✅ Mikrofon skalibrowany")
    
    def setup_tts(self):
        """Konfiguracja syntezy mowy"""
        self.tts_engine = pyttsx3.init()
        
        # Ustawienia głosu
        voices = self.tts_engine.getProperty('voices')
        if voices:
            # Wybierz żeński głos jeśli dostępny
            for voice in voices:
                pass
                # if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                #     self.tts_engine.setProperty('voice', voice.id)
                #     break
            else:
                self.tts_engine.setProperty('voice', voices[0].id)
        
        # Parametry mowy
        self.tts_engine.setProperty('rate', 180)  # Prędkość
        self.tts_engine.setProperty('volume', 0.9)  # Głośność
        
        print("🔊 Synteza mowy gotowa")
    
    def setup_ollama(self):
        """Test połączenia z Ollama"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=3)
            models = response.json()['models']
            
            # Wybierz najszybszy model
            self.ollama_model = "qwen2.5:0.5b"  # Najszybszy
            for model in models:
                if model['name'] == self.ollama_model:
                    break
            else:
                self.ollama_model = models[0]['name'] if models else "qwen2.5:0.5b"
            
            print(f"🦙 Ollama gotowy - model: {self.ollama_model}")
            
        except Exception as e:
            print(f"❌ Błąd Ollama: {e}")
            print("💡 Upewnij się że Ollama działa: ollama serve")
            exit(1)
    
    def speak(self, text):
        """Synteza mowy - w osobnym wątku"""
        if not text.strip():
            return
        
        def _speak():
            self.is_speaking = True
            print(f"🤖 Mówię: {text}")
            
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"❌ Błąd TTS: {e}")
            finally:
                self.is_speaking = False
        
        # Uruchom w osobnym wątku
        speech_thread = threading.Thread(target=_speak, daemon=True)
        speech_thread.start()
    
    def get_ollama_response(self, prompt):
        """Szybka odpowiedź z Ollama"""
        return "siema"
        # try:
        #     # Krótki prompt dla szybszej odpowiedzi
        #     system_prompt = "Odpowiadaj krótko i zwięźle. Max 2-3 zdania."
        #     full_prompt = f"{system_prompt}\n\nPytanie: {prompt}\nOdpowiedź:"
            
        #     response = requests.post(
        #         'http://localhost:11434/api/generate',
        #         json={
        #             'model': self.ollama_model,
        #             'prompt': full_prompt,
        #             'stream': False,
        #             'options': {
        #                 'temperature': 0.7,
        #                 'num_predict': 50,  # Ograniczenie długości
        #                 'top_p': 0.9
        #             }
        #         },
        #         timeout=10
        #     )
            
        #     if response.status_code == 200:
        #         result = response.json()['response'].strip()
        #         return result if result else "Nie rozumiem pytania."
        #     else:
        #         return "Przepraszam, mam problemy z odpowiedzią."
                
        # except Exception as e:
        #     print(f"❌ Błąd Ollama: {e}")
        #     return "Przepraszam, nie mogę teraz odpowiedzieć."
    
    def listen_for_audio(self):
        """Wątek nasłuchiwania audio"""
        while True:
            try:
                # Sprawdź czy może nasłuchiwać
                if self.is_speaking:
                    time.sleep(0.2)  # Trochę dłużej gdy mówi
                    continue
                
                with self.microphone as source:
                    # Krótszy timeout podczas normalnej pracy
                    timeout = 0.5 if not self.is_listening else 1.0
                    audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=4)
                    self.audio_queue.put(audio)
                    
            except sr.WaitTimeoutError:
                pass  # Timeout to normalne
            except Exception as e:
                print(f"❌ Błąd nagrywania: {e}")
                time.sleep(0.5)
    
    def process_audio(self):
        """Wątek przetwarzania audio"""
        while True:
            try:
                # Pobierz audio z kolejki
                audio = self.audio_queue.get(timeout=1)
                
                # Rozpoznawanie mowy - używamy Google (szybsze niż Whisper dla krótkich fraz)
                try:
                    text = self.recognizer.recognize_google(audio, language='pl-PL')
                    text = text.lower().strip()
                    
                    if not text:
                        continue
                    
                    print(f"🎤 Słyszę: {text}")
                    
                    # Sprawdź wake word
                    if self.wake_mode_active:
                        if self.WAKE_WORD in text:
                            print("🔥 Wake word detected!")
                            # Natychmiastowa odpowiedź w osobnym wątku
                            threading.Thread(target=lambda: self.speak("Słucham!"), daemon=True).start()
                            self.is_listening = True
                            continue
                        elif not self.is_listening:
                            continue  # Ignoruj jeśli nie aktywowany
                    
                    # Komendy systemowe
                    if "stop" in text or "zakończ" in text:
                        threading.Thread(target=lambda: self.speak("Kończę pracę"), daemon=True).start()
                        time.sleep(2)  # Poczekaj na dokończenie mowy
                        break
                    elif "tryb ciągły" in text:
                        self.wake_mode_active = False
                        self.is_listening = True
                        threading.Thread(target=lambda: self.speak("Przełączam na tryb ciągły"), daemon=True).start()
                        continue
                    elif "tryb aktywacji" in text:
                        self.wake_mode_active = True
                        self.is_listening = False
                        threading.Thread(target=lambda: self.speak("Przełączam na tryb aktywacji"), daemon=True).start()
                        continue
                    
                    # Wysłij do Ollama
                    if self.is_listening or not self.wake_mode_active:
                        response = self.get_ollama_response(text)
                        self.speak(response)
                        
                        # W trybie wake word, dezaktywuj po odpowiedzi
                        if self.wake_mode_active:
                            self.is_listening = False
                
                except sr.UnknownValueError:
                    pass  # Nie rozpoznano mowy - to normalne
                except sr.RequestError as e:
                    print(f"❌ Błąd rozpoznawania: {e}")
                    # Fallback do offline recognition jeśli Google nie działa
                    try:
                        text = self.recognizer.recognize_sphinx(audio)
                        print(f"🎤 (Offline) Słyszę: {text}")
                    except:
                        pass
                        
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Błąd przetwarzania: {e}")
    
    def toggle_mode(self):
        """Przełącz tryb pracy"""
        self.wake_mode_active = not self.wake_mode_active
        if self.wake_mode_active:
            self.is_listening = False
            print(f"🔄 Tryb aktywacji: '{self.WAKE_WORD}'")
        else:
            self.is_listening = True
            print("🔄 Tryb ciągły")
    
    def run(self):
        """Główna pętla programu"""
        # Uruchom wątki
        audio_thread = threading.Thread(target=self.listen_for_audio, daemon=True)
        process_thread = threading.Thread(target=self.process_audio, daemon=True)
        
        audio_thread.start()
        process_thread.start()
        
        # Interfejs użytkownika
        print("\n" + "="*50)
        print("🎤 ASYSTENT GŁOSOWY AKTYWNY")
        print("="*50)
        print("Komendy:")
        print("- 'stop' / 'zakończ' - zakończ program")
        print("- 'tryb ciągły' - słuchaj ciągle")
        print("- 'tryb aktywacji' - aktywacja frazą")
        print("- Ctrl+C - szybkie wyjście")
        print("- 'm' + Enter - przełącz tryb")
        print("="*50)
        
        try:
            while True:
                user_input = input().strip().lower()
                if user_input == 'm':
                    self.toggle_mode()
                elif user_input in ['quit', 'exit', 'q']:
                    break
                    
        except KeyboardInterrupt:
            print("\n👋 Zamykanie asystenta...")
        
        print("🛑 Asystent zakończył pracę")

def main():
    """Główna funkcja"""
    print("🚀 Uruchamianie asystenta głosowego...")
    
    try:
        assistant = VoiceAssistant()
        assistant.run()
    except Exception as e:
        print(f"❌ Błąd krytyczny: {e}")
        print("💡 Sprawdź czy masz zainstalowane:")
        print("   pip install speechrecognition pyttsx3 pyaudio requests")

if __name__ == "__main__":
    main()