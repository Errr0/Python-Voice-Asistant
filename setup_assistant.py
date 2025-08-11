# setup_assistant.py - Instalacja i konfiguracja

import subprocess
import sys
import os

def install_requirements():
    """Instalacja wymaganych bibliotek"""
    requirements = [
        'speechrecognition',
        'pyttsx3', 
        'pyaudio',
        'requests',
        'numpy'
    ]
    
    print("📦 Instalowanie wymaganych bibliotek...")
    for req in requirements:
        try:
            print(f"   Installing {req}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', req])
        except subprocess.CalledProcessError:
            print(f"❌ Błąd instalacji {req}")
            if req == 'pyaudio':
                print("💡 Dla PyAudio na Windows spróbuj:")
                print("   pip install pipwin")
                print("   pipwin install pyaudio")

def test_microphone():
    """Test mikrofonu"""
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        
        print("🎤 Testowanie mikrofonu...")
        with sr.Microphone() as source:
            print("   Kalibracja...")
            r.adjust_for_ambient_noise(source, duration=1)
            print("   ✅ Mikrofon działa!")
            return True
    except Exception as e:
        print(f"❌ Problem z mikrofonem: {e}")
        return False

def test_speakers():
    """Test głośników"""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        print("🔊 Testowanie głośników...")
        engine.say("Test głośników")
        engine.runAndWait()
        print("   ✅ Głośniki działają!")
        return True
    except Exception as e:
        print(f"❌ Problem z głośnikami: {e}")
        return False

def test_ollama():
    """Test połączenia z Ollama"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        models = response.json()['models']
        
        print("🦙 Ollama działa!")
        print("   Dostępne modele:")
        for model in models:
            print(f"   - {model['name']}")
        return True
    except Exception as e:
        print(f"❌ Ollama nie działa: {e}")
        print("💡 Uruchom: ollama serve")
        return False

def create_simple_config():
    """Stwórz prosty plik konfiguracyjny"""
    config = '''# config.py - Konfiguracja asystenta

# Fraza aktywacyjna
WAKE_WORD = "hej mercedes"

# Model Ollama (szybkie opcje dla słabego sprzętu)
OLLAMA_MODEL = "qwen2.5:0.5b"  # Najszybszy (~394MB)
# OLLAMA_MODEL = "llama3.2:1b"   # Wolniejszy ale lepszy (~1.3GB)

# Ustawienia rozpoznawania mowy
ENERGY_THRESHOLD = 300         # Czułość mikrofonu (niższe = bardziej czuły)
PAUSE_THRESHOLD = 0.8         # Czas pauzy przed zakończeniem nagrania
PHRASE_THRESHOLD = 0.3        # Czas do rozpoczęcia nagrania

# Ustawienia TTS
TTS_RATE = 180               # Prędkość mowy (słów/min)
TTS_VOLUME = 0.9             # Głośność (0.0-1.0)

# Język
LANGUAGE = "pl-PL"           # pl-PL dla polskiego, en-US dla angielskiego

# Tryb pracy
DEFAULT_WAKE_MODE = True     # True = aktywacja frazą, False = ciągłe słuchanie
'''
    
    with open('config.py', 'w', encoding='utf-8') as f:
        f.write(config)
    
    print("📝 Utworzono config.py")

def main():
    print("🛠️  SETUP ASYSTENTA GŁOSOWEGO")
    print("="*40)
    
    # Sprawdź Python
    print(f"🐍 Python {sys.version}")
    
    # Instaluj biblioteki
    install_requirements()
    print()
    
    # Testy sprzętu
    mic_ok = test_microphone()
    speaker_ok = test_speakers()
    ollama_ok = test_ollama()
    
    print("\n" + "="*40)
    print("📊 WYNIKI TESTÓW:")
    print(f"🎤 Mikrofon:  {'✅' if mic_ok else '❌'}")
    print(f"🔊 Głośniki:  {'✅' if speaker_ok else '❌'}")
    print(f"🦙 Ollama:    {'✅' if ollama_ok else '❌'}")
    
    if all([mic_ok, speaker_ok, ollama_ok]):
        print("\n🎉 Wszystko gotowe! Możesz uruchomić asystenta.")
        create_simple_config()
    else:
        print("\n⚠️  Napraw błędy przed uruchomieniem asystenta.")
        
        if not ollama_ok:
            print("\n💡 Aby uruchomić Ollama:")
            print("   1. Zainstaluj: https://ollama.ai/download")
            print("   2. Uruchom: ollama serve")
            print("   3. Pobierz model: ollama pull qwen2.5:0.5b")
    
    print("\n🚀 Aby uruchomić asystenta: python voice_assistant.py")

if __name__ == "__main__":
    main()