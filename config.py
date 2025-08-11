# config.py - Konfiguracja asystenta

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
