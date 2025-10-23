from faster_whisper import WhisperModel
import requests

# === 1) Transcrire un fichier audio ===
AUDIO_PATH = r"C:\Users\Lenovo\Downloads\salma et nassima-PFA 2025\audio.mp3"  # Remplace par ton fichier

print("⏳ Transcription en cours...")
model = WhisperModel("small", device="cpu")  # ou "medium", "large-v3" si tu veux mieux
segments, _ = model.transcribe(AUDIO_PATH, language=None)
transcription = "".join([segment.text for segment in segments]).strip()

print("✅ Texte transcrit :", transcription)

# === 2) Envoyer à LM Studio (modèle LLaMA ou autre dans LM Studio) ===
LM_URL = "http://localhost:1234/v1/chat/completions"
headers = {
    "Authorization": "Bearer lm-studio",
    "Content-Type": "application/json"
}
payload = {
    "model": "Llama-3.2-1B-Instruct",  # ou le nom exact dans LM Studio
    "messages": [
        {"role": "system", "content": "Tu es un assistant intelligent et clair."},
        {"role": "user", "content": transcription}
    ],
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 256
}

print("⏳ Envoi à LM Studio...")
response = requests.post(LM_URL, headers=headers, json=payload)

if response.status_code == 200:
    result = response.json()
    reply = result["choices"][0]["message"]["content"]
    print("✅ Réponse de LM Studio :\n", reply)
else:
    print("❌ Erreur:", response.status_code, response.text)
