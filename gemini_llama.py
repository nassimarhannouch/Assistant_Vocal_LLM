import requests
import pyttsx3
import whisper
import sounddevice as sd
import tempfile
import wave
import socket
import time

# ===== CONFIG =====
LMSTUDIO_URL = "http://localhost:1234/v1/chat/completions"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=AIzaSyCuXp1ZviHx8ZdrEUFJPMfuu7o6ue0DyFU"

# ===== ÉTAT DU VÉHICULE =====
car_state = {
    "climatisation": "éteinte",
    "vitres": "fermées",
    "navigation": "désactivée",
    "musique": "arrêtée",
    "communication": "aucun appel ni message"
}

# ===== OUTILS =====
def internet_ok():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except:
        return False

def record_audio(filename, duration=5, rate=16000):
    print("🎙️ Parlez maintenant...")
    audio = sd.rec(int(duration * rate), samplerate=rate, channels=1, dtype='int16')
    sd.wait()
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(audio.tobytes())
    return filename

def transcribe_audio(model, file_path):
    result = model.transcribe(file_path)
    return result["text"]

def ask_lmstudio(prompt):
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "local-model",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = requests.post(LMSTUDIO_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("Erreur LM Studio:", e)
        return "Désolé, je ne peux pas répondre pour le moment."

def ask_gemini(prompt):
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {"parts": [{"text": f"Réponds de manière concise et claire : {prompt}"}]}
        ]
    }
    try:
        response = requests.post(GEMINI_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print("Erreur Gemini:", e)
        print("Réponse brute:", response.text)
        return "Désolé, je ne peux pas répondre pour le moment."

# === Gestion des commandes ===
def process_command(user_text):
    user_text = user_text.lower()
    if "clim" in user_text or "climatisation" in user_text:
        car_state["climatisation"] = "allumée"
        return "Climatisation allumée."
    elif "ouvrir" in user_text and "vitre" in user_text:
        car_state["vitres"] = "ouvertes"
        return "Vitres ouvertes."
    elif "fermer" in user_text and "vitre" in user_text:
        car_state["vitres"] = "fermées"
        return "Vitres fermées."
    elif "aller" in user_text or "navigation" in user_text:
        car_state["navigation"] = "activée"
        return "Navigation activée vers votre destination."
    elif "musique" in user_text or "lecture" in user_text:
        car_state["musique"] = "en lecture"
        return "Lecture de musique lancée."
    elif "appel" in user_text or "message" in user_text:
        car_state["communication"] = "appel/message en cours"
        return "Appel ou message en cours."
    elif "état" in user_text or "status" in user_text or "voiture" in user_text:
        return (f"Climatisation: {car_state['climatisation']}, Vitres: {car_state['vitres']}, "
                f"Navigation: {car_state['navigation']}, Musique: {car_state['musique']}, "
                f"Communication: {car_state['communication']}.")
    else:
        return None

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# ===== MAIN =====
def main():
    print("Assistant vocal démarré. Dites 'stop' pour quitter.")
    whisper_model = whisper.load_model("base")

    while True:
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        record_audio(temp_audio, duration=5)
        user_text = transcribe_audio(whisper_model, temp_audio).strip()
        print(f"Vous: {user_text}")

        if user_text.lower() in ["stop", "quit", "exit"]:
            print("Assistant arrêté.")
            break

        # Vérifier si c'est une commande locale
        command_response = process_command(user_text)
        if command_response:
            print(f"[Commande] {command_response}")
            speak(command_response)
            continue  # Ne pas appeler Gemini si c'est une commande

        # Sinon, passer par Gemini ou LM Studio
        if internet_ok():
            ai_response = ask_gemini(user_text)
            print(f"[Gemini] {ai_response}")
        else:
            ai_response = ask_lmstudio(user_text)
            print(f"[LLaMA] {ai_response}")

        speak(ai_response)
        time.sleep(0.5)

if __name__ == "__main__":
    main()
