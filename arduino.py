import whisper
import sounddevice as sd
import numpy as np

# --- Charger le modèle Whisper ---
model = whisper.load_model("medium")  # tu peux mettre "base" ou "small" si c'est trop lourd

# --- Paramètres audio ---
duration = 5   # durée en secondes
fs = 16000     # fréquence d'échantillonnage

# --- Fonction pour écouter et transcrire ---
def listen_command():
    print("🎙️ Parle maintenant...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()  # attendre la fin de l'enregistrement
    audio = np.squeeze(audio)

    # transcription avec Whisper
    result = model.transcribe(audio, language="fr")
    text = result["text"].strip()
    print("📝 Tu as dit:", text)
    return text

# --- Test ---
if __name__ == "__main__":
    listen_command()
