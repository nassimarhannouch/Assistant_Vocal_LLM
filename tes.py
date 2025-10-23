import requests
import pyttsx3
import google.generativeai as genai

# --------- CONFIGURATION GEMINI ---------
API_KEY = "AIzaSyDNoxjGO-3WE6753lPlqcDUVEBYVxaLHRQ"  # Ta clé Gemini
genai.configure(api_key=API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")  # rapide

# --------- CONFIGURATION LM STUDIO ---------
lm_url = "http://localhost:1234/v1/chat/completions"
lm_headers = {"Content-Type": "application/json", "Authorization": "Bearer no-key"}
lm_model = "llama-3.2-1b-instruct"

# --------- VOIX ---------
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1)

print("Assistant : Bonjour ! Je suis votre assistant embarqué. (Dites 'stop' pour quitter)")
engine.say("Bonjour ! Je suis votre assistant embarqué.")
engine.runAndWait()

# --------- BOUCLE DE DISCUSSION ---------
while True:
    texte = input("Vous : ").strip()
    if texte.lower() in ["stop", "quitte", "au revoir"]:
        print("Assistant : Discussion terminée. Bonne route !")
        engine.say("Discussion terminée. Bonne route !")
        engine.runAndWait()
        break

    # Prompt amélioré
    prompt = f"""
    Tu es un assistant vocal embarqué dans une voiture.
    Tu dois :
    - Répondre aux commandes vocales liées à la voiture (climatisation, navigation, musique, appels...).
    - Répondre aussi de manière naturelle à toute autre question ou discussion (comme un assistant vocal).
    - Être toujours clair, concis et poli.
    - Ne jamais répondre par "je ne suis pas conçu pour cela" sauf si c’est vraiment hors sujet.
    - Ne donne pas de commentaires inutiles.

    Utilisateur : {texte}
    Assistant :
    """

    # --------- 1. ESSAYER GEMINI ---------
    try:
        response = gemini_model.generate_content(prompt)
        reponse_ia = response.text.strip()
        source = "Gemini"
    except Exception:
        # --------- 2. SI GEMINI ÉCHOUE → LM STUDIO ---------
        try:
            data = {
                "model": lm_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            }
            response = requests.post(lm_url, headers=lm_headers, json=data)
            reponse_ia = response.json()["choices"][0]["message"]["content"].strip()
            source = "LM Studio"
        except:
            reponse_ia = "Je n'ai pas pu obtenir de réponse pour le moment."
            source = "Aucun"

    # --------- AFFICHAGE + VOIX ---------
    print(f"Assistant ({source}) :", reponse_ia)
    engine.say(reponse_ia)
    engine.runAndWait()
