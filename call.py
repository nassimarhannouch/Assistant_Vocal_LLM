import qrcode
import urllib.parse

class AssistantVocal:
    def __init__(self):
        self.shortcuts = {
            "call": "shortcuts://run-shortcut?name=AppelerContact",
            "sms": "shortcuts://run-shortcut?name=EnvoyerSMS",
            "verif": "shortcuts://run-shortcut?name=VerifierContact"
        }

    def extract_contact_name(self, text):
        ignore_words = ["appel", "appelle", "message", "sms", "envoie", "à", "le", "la", "un", "une", "de"]
        words = text.lower().split()
        keywords = ["appelle", "appel", "message", "sms", "envoie"]

        for i, word in enumerate(words):
            if any(keyword in word for keyword in keywords):
                contact_words = [w for w in words[i+1:] if w not in ignore_words]
                return " ".join(contact_words).title()
        return None

    def generer_qr_raccourci(self, contact_name, action_type="call"):
        if not contact_name:
            print("❌ Aucun nom détecté.")
            return

        base_url = self.shortcuts.get(action_type)
        if not base_url:
            print("❌ Action non supportée.")
            return

        encoded_name = urllib.parse.quote(contact_name)
        full_url = f"{base_url}&input={encoded_name}"
        print(f"🔗 URL à ouvrir sur l’iPhone : {full_url}")

        qr = qrcode.make(full_url)
        qr.show()

    def generer_qr_verification(self, contact_name):
        encoded_name = urllib.parse.quote(contact_name)
        verif_url = f"{self.shortcuts['verif']}&input={encoded_name}"
        print(f"📲 Scanne ce QR code pour vérifier si {contact_name} existe dans ton iPhone.")
        qr = qrcode.make(verif_url)
        qr.show()

# ============ Exemple d'utilisation =============

assistant = AssistantVocal()

commande = input("👉 Que veux-tu faire ?  : ")
contact = assistant.extract_contact_name(commande)

# Génère le QR pour vérifier le contact avant
assistant.generer_qr_verification(contact)

# Une fois confirmé dans l'iPhone : générer appel ou sms
if "sms" in commande.lower() or "message" in commande.lower():
    assistant.generer_qr_raccourci(contact, action_type="sms")
else:
    assistant.generer_qr_raccourci(contact, action_type="call")
