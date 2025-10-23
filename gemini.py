import google.generativeai as genai
import pyttsx3

# --------- CONFIGURATION GEMINI ---------
API_KEY = "AIzaSyDNoxjGO-3WE6753lPlqcDUVEBYVxaLHRQ"  # ⚠️ Mets ta clé ici
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")  # rapide et économique

# --------- VOIX ---------
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # vitesse
engine.setProperty('volume', 1)  # volume

# --------- CONTEXTE DE DISCUSSION ---------
conversation_history = [
    {"role": "system", "content": "Tu es un assistant vocal embarqué dans une voiture. Sois clair, concis, poli et utile."}
]

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

    # Ajout du message utilisateur à l'historique
    conversation_history.append({"role": "user", "content": texte})

    # Requête à Gemini
    try:
        response = model.generate_content(
            "\n".join([msg["content"] for msg in conversation_history])
        )
        reponse_ia = response.text.strip()
    except Exception as e:
        reponse_ia = "Je n'ai pas pu obtenir de réponse pour le moment."

    # Ajout de la réponse IA à l'historique
    conversation_history.append({"role": "assistant", "content": reponse_ia})

    # Affichage et voix
    print("Assistant :", reponse_ia)
    engine.say(reponse_ia)
    engine.runAndWait()
