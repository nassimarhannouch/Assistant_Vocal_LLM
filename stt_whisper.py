import whisper
import os

audio_path = r"C:\Users\Lenovo\Downloads\salma et nassima-PFA 2025\audio.mp3"

if not os.path.exists(audio_path):
    print(f"❌ Fichier introuvable : {audio_path}")
else:
    model = whisper.load_model("small")
    result = model.transcribe(audio_path)
    print(result["text"])
