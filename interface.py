import tkinter as tk
from tkinter import scrolledtext
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import sounddevice as sd
import numpy as np
import pyttsx3
import requests
from faster_whisper import WhisperModel
import tempfile
import wave
import threading
import time
from datetime import datetime
import json
import re
import socket
import webbrowser
import urllib.parse
from ddgs import DDGS
import html
import os
import pickle
from datetime import datetime
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog
import qrcode
import urllib.parse
from PIL import Image, ImageTk
import io
from langchain_community.llms import Ollama
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser
import langchain
import folium
import webbrowser
import tempfile
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import json
import re
import threading
import tkinter.simpledialog as simpledialog
import requests
import json
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium
from folium import plugins
import webbrowser
import tempfile
import os
import warnings
import urllib.parse
import webbrowser
warnings.filterwarnings("ignore", category=UserWarning, module="langchain")

class CarAssistantOutputParser(BaseOutputParser):
    """Parser personnalisé pour l'assistant automobile"""
    
    def parse(self, text: str) -> str:
        """Parse et nettoie la réponse de l'IA"""
        # Nettoyer la réponse
        cleaned = text.strip()
        
        # Limiter la longueur pour les réponses vocales
        if len(cleaned) > 200:
            sentences = cleaned.split('.')
            short_response = ""
            for sentence in sentences:
                if len(short_response + sentence) < 200:
                    short_response += sentence + "."
                else:
                    break
            cleaned = short_response if short_response else cleaned[:200]
        
        return cleaned

# ========== CONFIGURATION ==========
RATE = 16000
WHISPER_MODEL = "medium"
LM_URL = "http://localhost:1234/v1/chat/completions"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=AIzaSyCuXp1ZviHx8ZdrEUFJPMfuu7o6ue0DyFU"
HEADERS = {"Authorization": "Bearer lm-studio", "Content-Type": "application/json"}
MODEL_NAME = "Llama-3.2-1B-Instruct"


class CarSystem:
# ========== SYSTÈME AUTOMOBILE ==========
    def __init__(self):
        self.climate = {"on": False, "temp": 22}
        self.windows = {"front_left": False, "front_right": False, 
                        "rear_left": False, "rear_right": False}
        self.music = {"playing": False, "volume": 50, "track": "Aucune"}
        self.navigation = {"active": False, "destination": ""}
        
        self.engine = {"on": True, "rpm": 0, "fuel": 75}  
        self.lights = {"headlights": False, "hazard": False}  
        self.doors = {"driver": False, "passenger": False, "rear_left": False, "rear_right": False}  
        self.shortcuts = {
            "call": "shortcuts://run-shortcut?name=AppelerContact"
        }
        self.shortcuts = {
            "call": "shortcuts://run-shortcut?name=AppelerContact",
            "sms": "shortcuts://run-shortcut?name=EnvoyerSMS",
            "verif": "shortcuts://run-shortcut?name=VerifierContact"
        }
        #  Pas de liste fixe, validation via raccourci iOS
        self.contacts_autorises = {}  # Vide - validation dynamique
        self.music_shortcuts = {
        "play": "shortcuts://run-shortcut?name=LancerMusique",
        "pause": "shortcuts://run-shortcut?name=PauserMusique", 
        "next": "shortcuts://run-shortcut?name=PisteSuivante",
        "previous": "shortcuts://run-shortcut?name=PistePrecedente",
        "volume_up": "shortcuts://run-shortcut?name=AugmenterVolume",
        "volume_down": "shortcuts://run-shortcut?name=DiminuerVolume",
        "play_playlist": "shortcuts://run-shortcut?name=JouerPlaylist",
        "play_artist": "shortcuts://run-shortcut?name=JouerArtiste"
    }
        self.shortcuts = {
            "call": "shortcuts://run-shortcut?name=AppelerContact",
            "sms": "shortcuts://run-shortcut?name=EnvoyerSMS", 
            "verif": "shortcuts://run-shortcut?name=VerifierContact",
            "check": "shortcuts://run-shortcut?name=ContactExiste"  
        }

    def get_detailed_status(self):
        """Retourne l'état simplifié du véhicule - Version personnalisée"""
    
    # Calculer les vitres ouvertes
        open_windows = sum(1 for v in self.windows.values() if v)
        total_windows = len(self.windows)
    
        return f"""🚗 ÉTAT DU VÉHICULE

🧭 NAVIGATION
   {'🟢 Actif' if self.navigation['active'] else '🔴 Inactif'}
   {f"Destination: {self.navigation['destination']}" if self.navigation['destination'] else "Aucune destination"}

🌡️ CLIMATISATION  
   {'🟢 Activée' if self.climate['on'] else '🔴 Désactivée'} - {self.climate['temp']}°C

🪟 VITRES
   {open_windows}/{total_windows} ouvertes {'🟢' if open_windows == 0 else '🟡' if open_windows <= 2 else '🔴'}

🎵 MUSIQUE
   {'🟢 En cours' if self.music['playing'] else '🔴 Arrêtée'} - Volume: {self.music['volume']}%
   {f"♪ {self.music['track']}" if self.music['playing'] else "Aucune piste"}"""
    def calculate_consumption(self):
        """Calcule la consommation basée sur l'état du véhicule"""
        base_consumption = 7.5  # L/100km de base
        
        # Facteurs d'augmentation
        if self.climate["on"]:
            base_consumption += 1.2
        if self.music["playing"] and self.music["volume"] > 70:
            base_consumption += 0.3
        if sum(self.windows.values()) > 2:  # Plus de 2 vitres ouvertes
            base_consumption += 0.8
            
        return round(base_consumption, 1)

    def get_security_score(self):
        """Calcule un score de sécurité sur 100"""
        score = 100
        
        # Déductions
        open_doors = sum(1 for v in self.doors.values() if v)
        open_windows = sum(1 for v in self.windows.values() if v)
        
        score -= open_doors * 15  # -15 points par porte ouverte
        score -= open_windows * 5  # -5 points par vitre ouverte
        
        if not self.lights["headlights"] and self.engine["on"]:
            score -= 10  # Pas de phares si moteur en marche
            
        return max(0, score)

    def get_energy_efficiency(self):
        """Calcule l'efficacité énergétique sur 100"""
        score = 100
        
        if self.climate["on"]:
            score -= 20
        if self.music["playing"]:
            score -= 5 + (self.music["volume"] / 10)
        if sum(self.windows.values()) > 0:
            score -= sum(self.windows.values()) * 3
            
        return max(0, int(score))

    def update_engine_rpm(self, rpm):
        """Met à jour le RPM du moteur"""
        self.engine["rpm"] = max(0, min(6000, rpm))

    def toggle_lights(self, light_type):
        """Bascule l'état des phares"""
        if light_type in self.lights:
            self.lights[light_type] = not self.lights[light_type]
            return f"{'✅ Allumés' if self.lights[light_type] else '❌ Éteints'}"
        return "❌ Type d'éclairage non reconnu"

    def toggle_door(self, door):
        """Bascule l'état d'une porte"""
        if door in self.doors:
            self.doors[door] = not self.doors[door]
            return f"Porte {door}: {'🔓 Ouverte' if self.doors[door] else '🔒 Fermée'}"
        return "❌ Porte non reconnue"
    # AJOUTER CETTE NOUVELLE MÉTHODE
    def generer_qr_raccourci(self, contact_name, action_type="call"):
        """Génère un QR code pour appel/SMS - Version dynamique"""
        if not contact_name:
            return None, "❌ Aucun nom détecté."
    
        base_url = self.shortcuts.get(action_type)
        if not base_url:
           return None, f"❌ Action non supportée : {action_type}"
    
        try:
        # NOUVEAU: Pas de vérification de liste, direct au raccourci
           encoded_name = urllib.parse.quote(contact_name)
           full_url = f"{base_url}&input={encoded_name}"
        
        # Créer le QR code
           qr = qrcode.QRCode(version=1, box_size=10, border=5)
           qr.add_data(full_url)
           qr.make(fit=True)
        
           qr_image = qr.make_image(fill_color="black", back_color="white")
        
           action_fr = "appeler" if action_type == "call" else "envoyer SMS à"
           message = f"✅ QR code généré pour {action_fr} {contact_name}"
           message += f"\n📱 Le contact sera vérifié sur votre iPhone"
        
           return qr_image, message
        
        except Exception as e:
           return None, f"❌ Erreur génération QR : {e}"

    # AJOUTER CETTE MÉTHODE AUSSI
    def generer_qr_verification(self, contact_name):
        """Génère un QR code pour vérifier si le contact existe"""
        if not contact_name:
            return None, "❌ Aucun nom détecté."
        
        try:
            encoded_name = urllib.parse.quote(contact_name)
            verif_url = f"{self.shortcuts['verif']}&input={encoded_name}"
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(verif_url)
            qr.make(fit=True)
            
            qr_image = qr.make_image(fill_color="blue", back_color="white")
            message = f"📲 QR code de vérification pour {contact_name}"
            
            return qr_image, message
            
        except Exception as e:
            return None, f"❌ Erreur génération QR : {e}"

    def extract_contact_name(self, text):
        """Extrait le nom du contact - Version dynamique"""
        print(f"🔍 Debug - Texte reçu: '{text}'")
    
        ignore_words = [
            "appel", "appelle", "téléphone", "message", "sms", "envoie", "envoyer",
            "un", "une", "le", "la", "les", "à", "au", "aux", "de", "du", "des"
        ]
    
        words = text.lower().split()
        keywords = ["appelle", "appel", "message", "sms", "envoie"]
    
    # Rechercher le mot-clé et extraire ce qui suit
        for i, word in enumerate(words):
            if any(keyword in word for keyword in keywords):
            # Extraire tous les mots après le mot-clé
                 contact_words = []
                 for j in range(i + 1, len(words)):
                     if words[j] not in ignore_words:
                       contact_words.append(words[j])
            
                 if contact_words:
                # NOUVEAU: Retourner directement le nom sans vérification fixe
                   contact_name = " ".join(contact_words).strip()
                   print(f"✅ Debug - Contact extrait: {contact_name}")
                   return contact_name.title()  # Mettre en forme (première lettre majuscule)
    
        print(f"❌ Debug - Aucun contact trouvé")
        return None

    def make_call_or_sms(self, contact_name, action_type="call"):
        """Lance l'appel via raccourci iOS uniquement si le contact est autorisé"""
        if not contact_name:
            print("❌ Contact non reconnu ou non autorisé.")
            return False

        try:
            encoded_name = urllib.parse.quote(contact_name)
            base_url = self.shortcuts.get(action_type)
            if not base_url:
                print(f"❌ Action non supportée : {action_type}")
                return False

            # Crée l'URL du raccourci avec le nom du contact
            full_url = f"{base_url}&input={encoded_name}"
            webbrowser.open(full_url)
            print(f"📞 Appel lancé vers {contact_name} via raccourci iOS")
            return True
        except Exception as e:
            print(f"❌ Erreur lors du lancement : {e}")
            return False
    
    def execute_command(self, text):
        """Traite et exécute les commandes vocales"""
        text = text.lower().strip()
        # NOUVEAU: Commandes de gestion des chats
        if any(word in text for word in ["nouveau chat", "new chat", "nouvelle conversation"]):
           return "🔄 Commande détectée : Nouveau chat. Utilisez le bouton 'Nouveau Chat' dans l'interface."
    
        elif any(word in text for word in ["sauvegarde", "sauvegarder", "enregistrer"]):
           return "💾 Commande détectée : Sauvegarde. Utilisez le bouton 'Sauvegarder' dans l'interface."
    
        elif any(word in text for word in ["historique", "conversations", "anciens chats"]):
           return "📚 Commande détectée : Historique. Utilisez le bouton 'Historique' dans l'interface."
        
        # 🌡️ CLIMATISATION
        if any(word in text for word in ["clim", "climatisation", "température", "chauff", "degré", "degre"]):
            if "allum" in text or "activ" in text:
                 self.climate["on"] = True
                 return "✅ Climatisation activée"
            elif "éteind" in text or "désactiv" in text:
                self.climate["on"] = False
                return "✅ Climatisation désactivée"
            # NOUVEAU: Modification des degrés (augmenter/diminuer)
            elif any(word in text for word in ["augment", "monte", "plus", "hausse"]):
        # Rechercher si un nombre spécifique est mentionné
                temp_match = re.search(r'(\d+)', text)
                if temp_match:
                    increment = int(temp_match.group(1))
                else:
                    increment = 1  # Par défaut +1°C
        
                new_temp = min(30, self.climate["temp"] + increment)
                old_temp = self.climate["temp"]
                self.climate["temp"] = new_temp
        
                if new_temp == old_temp:
                    return f"⚠️ Température déjà au maximum (30°C)"
                else:
                    return f"✅ Température augmentée de {old_temp}°C à {new_temp}°C"
                
            elif any(word in text for word in ["diminue", "baisse", "moins", "réduis"]):
        # Rechercher si un nombre spécifique est mentionné
                 temp_match = re.search(r'(\d+)', text)
                 if temp_match:
                     decrement = int(temp_match.group(1))
                 else:
                     decrement = 1  # Par défaut -1°C
        
                 new_temp = max(16, self.climate["temp"] - decrement)
                 old_temp = self.climate["temp"]
                 self.climate["temp"] = new_temp
        
                 if new_temp == old_temp:
                     return f"⚠️ Température déjà au minimum (16°C)"
                 else:
                     return f"✅ Température réduite de {old_temp}°C à {new_temp}°C"
                 
            # Réglage direct de température
            elif "température" in text or any(word in text for word in ["met", "règle", "fixe"]):
                  temp_match = re.search(r'(\d+)', text)
                  if temp_match:
                     temp = int(temp_match.group(1))
                     if 16 <= temp <= 30:
                      old_temp = self.climate["temp"]
                      self.climate["temp"] = temp
                     return f"✅ Température réglée de {old_temp}°C à {temp}°C"
                  else:
                     return f"❌ Température invalide. Plage autorisée : 16°C à 30°C"
    
            return f"🌡️ Climat: {'ON' if self.climate['on'] else 'OFF'} - {self.climate['temp']}°C"
        # 🔍 RECHERCHE WEB
        elif any(word in text for word in ["recherche", "cherche", "trouve", "google", "internet", "web"]):
            # Extraire la requête de recherche
            search_terms = ["recherche", "cherche", "trouve", "google", "sur internet", "sur le web"]
            query = text
            
            # Nettoyer la requête
            for term in search_terms:
                if term in query:
                    query = query.replace(term, "").strip()
            
            # Mots à ignorer
            ignore_words = ["moi", "pour", "sur", "le", "la", "les", "un", "une", "des", "du", "de"]
            words = query.split()
            clean_words = [w for w in words if w.lower() not in ignore_words and len(w) > 1]
            final_query = " ".join(clean_words)
            
            if final_query:
                return self.web_search(final_query)
            else:
                return "❌ Veuillez préciser votre recherche"
        
        # 🪟 VITRES
        elif any(word in text for word in ["vitre", "fenêtre", "ouvr", "ferm"]):
            if "ouvr" in text or "baiss" in text:
                if "toute" in text:
                    for window in self.windows:
                        self.windows[window] = True
                    return "✅ Toutes les vitres ouvertes"
                else:
                    self.windows["front_left"] = True
                    return "✅ Vitre conducteur ouverte"
            elif "ferm" in text or "remont" in text:
                if "toute" in text:
                    for window in self.windows:
                        self.windows[window] = False
                    return "✅ Toutes les vitres fermées"
                else:
                    self.windows["front_left"] = False
                    return "✅ Vitre conducteur fermée"
        
        # 🎵 MUSIQUE
        elif any(word in text for word in ["musique", "son", "volume", "joue", "lance", "pause", "suivant", "précédent"]):
            # Contrôles basiques
            if "joue" in text or "lance" in text or "met" in text:
                if "playlist" in text:
            # Extraire nom de playlist
                    words = text.split()
                    playlist_name = None
                    for i, word in enumerate(words):
                        if word in ["playlist", "liste"]:
                            if i + 1 < len(words):
                                playlist_name = " ".join(words[i+1:])
                            break
                    if playlist_name:
                        qr_image, message = self.generate_music_qr("play_playlist", playlist_name)
                        if qr_image:
                            return message, qr_image
                        else:
                            return message
                    else:
                           return "❌ Nom de playlist non détecté. Dites 'Lance playlist [nom]'"
            
                elif "artiste" in text:
            # Extraire nom d'artiste
                   words = text.split()
                   artist_name = None
                   for i, word in enumerate(words):
                       if word == "artiste":
                           if i + 1 < len(words):
                              artist_name = " ".join(words[i+1:])
                              break
                           
                   if artist_name:
                        qr_image, message = self.generate_music_qr("play_artist", artist_name)
                        if qr_image:
                           return message, qr_image
                        else:
                           return message
                   else:
                        return "❌ Nom d'artiste non détecté. Dites 'Lance artiste [nom]'"
                   
                else:
            # Lecture générale
                   self.music["playing"] = True
                   qr_image, message = self.generate_music_qr("play")
                   if qr_image:
                      return message, qr_image
                   else:
                      return "▶️ Commande de lecture envoyée à l'iPhone"
                   
            elif "pause" in text or "arrêt" in text or "stop" in text:
                self.music["playing"] = False
                qr_image, message = self.generate_music_qr("pause")
                if qr_image:
                    return message, qr_image
                else:
                    return "⏸️ Musique mise en pause"
    
            elif "suivant" in text or "next" in text:
                  qr_image, message = self.generate_music_qr("next")
                  if qr_image:
                     return message, qr_image
                  else:
                     return "⏭️ Piste suivante"
    
            elif "précédent" in text or "previous" in text:
                   qr_image, message = self.generate_music_qr("previous") 
                   if qr_image:
                        return message, qr_image
                   else:
                        return "⏮️ Piste précédente"
    
            elif "volume" in text:
                  if "augment" in text or "plus fort" in text or "monte" in text:
                      qr_image, message = self.generate_music_qr("volume_up")
                      if qr_image:
                           return message, qr_image
                      else:
                           return "🔊 Volume augmenté"
        
            elif "diminue" in text or "moins fort" in text or "baisse" in text:
                   qr_image, message = self.generate_music_qr("volume_down")
                   if qr_image:
                       return message, qr_image
                   else:
                       return "🔉 Volume diminué"
        
        # Volume spécifique (si supporté)
            else:
                 vol_match = re.search(r'(\d+)', text)
                 if vol_match:
                     vol = min(100, max(0, int(vol_match.group(1))))
                     self.music["volume"] = vol
                     return f"✅ Volume théorique réglé à {vol}% (utiliser QR pour iPhone)"
    
            return f"🎵 Musique: {'ON' if self.music['playing'] else 'OFF'} - Volume: {self.music['volume']}%"

        # Commandes navigation
        if any(word in text for word in ["aller", "navigation", "route", "va", "direction"]):
            if not hasattr(self, 'navigation_system'):
              return "❌ Navigation non disponible"
    
            if any(word in text for word in ["arrêt", "stop", "annul"]):
               return self.navigation_system.stop_navigation()
            elif "état" in text or "status" in text:
               return self.navigation_system.get_status()
            else:
               return self.navigation_system.start_navigation(text)

# Test GPS et localisation
        elif any(word in text for word in ["position", "localisation", "où suis", "gps", "coordonnées"]):
            if hasattr(self, 'navigation_system'):
              return self.navigation_system.test_gps_location()
            else:
              return "❌ Système GPS non disponible"
        
        # 📞 APPELS AVEC QR CODE (REMPLACER LA SECTION APPELS EXISTANTE)
        elif any(word in text for word in ["appel", "appelle", "téléphone"]):
            contact_name = self.extract_contact_name(text)
            if contact_name:
                # Générer QR code pour appel
                qr_image, message = self.generer_qr_raccourci(contact_name, "call")
                if qr_image:
                    return message, qr_image
                else:
                    return message
            else:
                return "❌ Nom du contact non reconnu. Dites 'Appelle [nom]'"
        # 💬 MESSAGES AVEC QR CODE (REMPLACER LA SECTION MESSAGES EXISTANTE)
        elif any(word in text for word in ["message", "sms", "envoie", "envoyer"]):
            contact_name = self.extract_contact_name(text)
            if contact_name:
                # Générer QR code pour SMS
                qr_image, message = self.generer_qr_raccourci(contact_name, "sms")
                if qr_image:
                    return message, qr_image
                else:
                    return message
            else:
                return "❌ Nom du contact non reconnu. Dites 'Message à [nom]'"
        # 🔍 VÉRIFICATION CONTACT (NOUVELLE FONCTIONNALITÉ)
        elif any(word in text for word in ["vérifie", "vérifier", "existe", "contact"]):
            contact_name = self.extract_contact_name(text)
            if contact_name:
                qr_image, message = self.generer_qr_verification(contact_name)
                if qr_image:
                    return message, qr_image
                else:
                    return message
            else:
                return "❌ Nom du contact non reconnu pour vérification"
        
        # 💬 MESSAGES UNIVERSELS
        elif any(word in text for word in ["message", "sms", "envoie", "envoyer"]):
            contact_name = self.extract_contact_name(text)
            if contact_name:
                success = self.make_call_or_sms(contact_name, "sms")
                if success:
                    return f"✅ Ouverture des messages pour {contact_name}"
                else:
                    return f"❌ Impossible d'envoyer un message à {contact_name}"
            else:
                return "❌ Nom du contact non reconnu. Dites 'Message à [nom]'"
        
        # 🚗 ÉTAT DÉTAILLÉ
        elif any(word in text for word in ["état", "status", "diagnostic", "rapport"]):
            if "détaillé" in text or "complet" in text or "diagnostic" in text:
                return self.get_detailed_status()
            else:
               return self.get_status()
    
    
    # 💡 ÉCLAIRAGE
        elif any(word in text for word in ["phare", "phares", "éclairage", "lumière"]):
            if "allum" in text:
               result = self.toggle_lights("headlights")
               return f"💡 Phares {result}"
            elif "warning" in text or "détresse" in text:
               result = self.toggle_lights("hazard")
               return f"⚠️ Warnings {result}"
    
    # 🚪 PORTES
        elif any(word in text for word in ["porte", "portes", "ouvre", "ferme", "verrouille"]):
            if "conducteur" in text or "gauche" in text:
               result = self.toggle_door("driver")
               return f"🚪 {result}"
            elif "passager" in text or "droite" in text:
               result = self.toggle_door("passenger")
               return f"🚪 {result}"
            elif "toutes" in text:
                if "ouvre" in text:
                  for door in self.doors:
                    self.doors[door] = True
                    return "🚪 Toutes les portes ouvertes"
                elif "ferme" in text:
                   for door in self.doors:
                      self.doors[door] = False
                   return "🔒 Toutes les portes fermées"
    
        
        return None

    def extraire_requete_recherche(self, commande):
        commande = commande.lower()
    
        mots_a_supprimer = [
            "fais", "fait", "faites", "cherche", "cherche-moi",
            "recherche", "recherche-moi", "montre", "montre-moi",
            "sur", "de", "du", "la", "le", "les", "une", "un"
        ]
    
        mots = commande.split()
        mots_utiles = [mot for mot in mots if mot not in mots_a_supprimer]
    
        return " ".join(mots_utiles).strip(".?! ")
    
    def web_search(self, query):
        """Effectue une recherche web avec DuckDuckGo"""
        try:
            with DDGS() as ddgs:
                # Recherche avec limite de 3 résultats
                results = list(ddgs.text(query, max_results=3))
                
                if not results:
                    return f"❌ Aucun résultat trouvé pour '{query}'"
                
                # Formatage des résultats
                response = f"🔍 Résultats pour '{query}':\n\n"
                
                for i, result in enumerate(results, 1):
                    title = html.unescape(result.get('title', 'Sans titre'))
                    snippet = html.unescape(result.get('body', 'Pas de description'))
                    url = result.get('href', '')
                    
                    # Limiter la longueur du snippet
                    if len(snippet) > 120:
                        snippet = snippet[:120] + "..."
                    
                    response += f"{i}. {title}\n{snippet}\n{url}\n\n"
                
                return response.strip()
                
        except Exception as e:
            return f"❌ Erreur de recherche: {str(e)}"
        
    def control_iphone_music(self, action, parameter=None):
        """Contrôle la musique via raccourcis iPhone"""
        try:
            base_url = self.music_shortcuts.get(action)
            if not base_url:
                return f"❌ Action musicale non supportée : {action}"
        
        # URL avec paramètre si nécessaire
            if parameter:
                encoded_param = urllib.parse.quote(parameter)
                full_url = f"{base_url}&input={encoded_param}"
            else:
                full_url = base_url
        
        # Ouvrir le raccourci
            webbrowser.open(full_url)
        
        # Messages de confirmation
            messages = {
            "play": "▶️ Lecture lancée sur iPhone",
            "pause": "⏸️ Musique en pause", 
            "next": "⏭️ Piste suivante",
            "previous": "⏮️ Piste précédente",
            "volume_up": "🔊 Volume augmenté",
            "volume_down": "🔉 Volume diminué",
            "play_playlist": f"🎵 Playlist '{parameter}' lancée",
            "play_artist": f"🎤 Artiste '{parameter}' en lecture"
            }
        
            return messages.get(action, "✅ Commande musicale envoyée")
        
        except Exception as e:
            return f"❌ Erreur contrôle musique : {e}"

    
    def generate_music_qr(self, action, parameter=None):
        """Génère un QR code pour contrôle musical"""
        try:
            base_url = self.music_shortcuts.get(action)
            if not base_url:
                return None, f"❌ Action non supportée : {action}"
        
        # URL avec paramètre
            if parameter:
                encoded_param = urllib.parse.quote(parameter)
                full_url = f"{base_url}&input={encoded_param}"
            else:
                full_url = base_url
        
        # Créer QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(full_url)
            qr.make(fit=True)
        
        # Couleur selon l'action
            colors = {
                 "play": ("green", "white"),
                 "pause": ("orange", "white"), 
                 "next": ("blue", "white"),
                  "previous": ("purple", "white")
             }
            fill_color, back_color = colors.get(action, ("black", "white"))
        
            qr_image = qr.make_image(fill_color=fill_color, back_color=back_color)
        
            actions_fr = {
            "play": "lancer la musique",
            "pause": "mettre en pause",
            "next": "piste suivante", 
            "previous": "piste précédente",
            "play_playlist": f"jouer la playlist {parameter}",
            "play_artist": f"jouer l'artiste {parameter}"
            }
        
            action_text = actions_fr.get(action, action)
            message = f"🎵 QR code généré pour {action_text}"
        
            return qr_image, message
        
        except Exception as e:
            return None, f"❌ Erreur génération QR : {e}"

    def get_status(self):
        """Retourne l'état complet du véhicule"""
        open_windows = sum(1 for v in self.windows.values() if v)
        return f"""🚗 État du véhicule:
🌡️ Climat: {'ON' if self.climate['on'] else 'OFF'} ({self.climate['temp']}°C)
🪟 Vitres: {open_windows} ouverte(s)
🎵 Audio: {'ON' if self.music['playing'] else 'OFF'} ({self.music['volume']}%)
🗺️ Navigation: {'Actif' if self.navigation['active'] else 'Inactif'}"""

# ========== FONCTIONS IA ==========
def internet_ok():
    """Vérifie si Internet est disponible"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except:
        return False

def ask_gemini(prompt):
    """Interroge l'API Gemini"""
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {"parts": [{"text": f"Réponds de manière concise et claire en français : {prompt}"}]}
        ]
    }
    try:
        response = requests.post(GEMINI_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return "Service Gemini temporairement indisponible."


# REMPLACER COMPLÈTEMENT LA CLASSE NavigationSystem EXISTANTE PAR CELLE-CI :

class NavigationSystem:
    def __init__(self, langchain_manager=None):
        self.langchain_manager = langchain_manager
        self.geolocator = Nominatim(user_agent="CarOS_Navigation_v3")
        self.destination = None
        self.route_active = False
        self.current_location = None
        self.precision_mode = "auto"  # auto, ip, manual, web
        
        # Lieux favoris (Casablanca et alentours)
        self.favorites = {
            "maison": (33.5831, -7.5998),
            "travail": (33.5931, -7.5898), 
            "centre": (33.5731, -7.5898),
            "gare": (33.6031, -7.6198),
            "aéroport": (33.3675, -7.5897),
            "hôpital": (33.5631, -7.6298),
            "casablanca": (33.5731, -7.5898),
            "rabat": (34.0209, -6.8416),
            "marrakech": (31.6295, -7.9811),
            "fes": (34.0181, -5.0078),
            "tanger": (35.7595, -5.8340)
        }
        
        self.default_location = (33.5731, -7.5898)  # Casablanca centre
        
        # Obtenir la position actuelle au démarrage
        self.get_current_location()
    
    def create_html5_geolocation_page(self):
        """Crée une page HTML5 pour obtenir la géolocalisation précise"""
        html_content = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CarOS - Géolocalisation GPS</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 500px;
            width: 100%;
        }
        .logo {
            font-size: 3em;
            margin-bottom: 20px;
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
        }
        .status {
            margin: 20px 0;
            padding: 15px;
            border-radius: 8px;
            font-weight: bold;
        }
        .loading {
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }
        .success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .coordinates {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            font-family: 'Courier New', monospace;
        }
        button {
            background: #007bff;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px;
        }
        button:hover {
            background: #0056b3;
        }
        .copy-btn {
            background: #28a745;
        }
        .copy-btn:hover {
            background: #1e7e34;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">📍</div>
        <h1>CarOS - Géolocalisation GPS</h1>
        <p>Cliquez sur "Obtenir ma position" pour autoriser l'accès GPS</p>
        
        <button onclick="getLocation()">📡 Obtenir ma position</button>
        
        <div id="status" class="status" style="display:none;"></div>
        <div id="coordinates" class="coordinates" style="display:none;"></div>
        
        <script>
            let currentCoords = null;
            
            function getLocation() {
                const statusDiv = document.getElementById('status');
                const coordsDiv = document.getElementById('coordinates');
                
                statusDiv.style.display = 'block';
                statusDiv.className = 'status loading';
                statusDiv.innerHTML = '🔍 Recherche de votre position GPS...';
                
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(
                        showPosition, 
                        showError, 
                        {
                            enableHighAccuracy: true,
                            timeout: 15000,
                            maximumAge: 0
                        }
                    );
                } else {
                    statusDiv.className = 'status error';
                    statusDiv.innerHTML = '❌ Géolocalisation non supportée par ce navigateur.';
                }
            }
            
            function showPosition(position) {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                const accuracy = position.coords.accuracy;
                
                currentCoords = {lat: lat, lon: lon, accuracy: accuracy};
                
                const statusDiv = document.getElementById('status');
                const coordsDiv = document.getElementById('coordinates');
                
                statusDiv.className = 'status success';
                statusDiv.innerHTML = `✅ Position GPS obtenue avec précision de ${Math.round(accuracy)}m`;
                
                coordsDiv.style.display = 'block';
                coordsDiv.innerHTML = `
                    <h3>📍 Vos Coordonnées GPS</h3>
                    <strong>Latitude:</strong> ${lat.toFixed(6)}<br>
                    <strong>Longitude:</strong> ${lon.toFixed(6)}<br>
                    <strong>Précision:</strong> ±${Math.round(accuracy)} mètres<br>
                    <br>
                    <button class="copy-btn" onclick="copyCoordinates()">📋 Copier les coordonnées</button>
                    <button onclick="openInMaps()">🗺️ Ouvrir dans Google Maps</button>
                `;
                
                // Sauvegarder automatiquement dans le localStorage
                localStorage.setItem('carOsGpsCoords', JSON.stringify(currentCoords));
            }
            
            function showError(error) {
                const statusDiv = document.getElementById('status');
                statusDiv.className = 'status error';
                
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        statusDiv.innerHTML = '❌ Accès GPS refusé. Autorisez la géolocalisation dans votre navigateur.';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        statusDiv.innerHTML = '❌ Position GPS non disponible.';
                        break;
                    case error.TIMEOUT:
                        statusDiv.innerHTML = '❌ Délai d\'attente GPS dépassé.';
                        break;
                    default:
                        statusDiv.innerHTML = '❌ Erreur GPS inconnue.';
                        break;
                }
            }
            
            function copyCoordinates() {
                if (currentCoords) {
                    const coordText = `${currentCoords.lat}, ${currentCoords.lon}`;
                    navigator.clipboard.writeText(coordText).then(() => {
                        alert('✅ Coordonnées copiées dans le presse-papiers!');
                    });
                }
            }
            
            function openInMaps() {
                if (currentCoords) {
                    const url = `https://www.google.com/maps/@${currentCoords.lat},${currentCoords.lon},17z`;
                    window.open(url, '_blank');
                }
            }
            
            // Charger automatiquement les coordonnées sauvegardées
            window.onload = function() {
                const saved = localStorage.getItem('carOsGpsCoords');
                if (saved) {
                    const coords = JSON.parse(saved);
                    const age = Date.now() - (coords.timestamp || 0);
                    
                    // Si les coordonnées ont moins de 5 minutes, les afficher
                    if (age < 300000) {
                        currentCoords = coords;
                        showPosition({coords: coords});
                    }
                }
            };
        </script>
    </div>
</body>
</html>
        """
        
        # Créer le fichier HTML temporaire
        html_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
        html_file.write(html_content)
        html_file.close()
        
        return html_file.name
    
    def get_html5_location(self):
        """Obtient la position via HTML5 Geolocation"""
        try:
            print("🌐 Ouverture de l'interface GPS HTML5...")
            html_file = self.create_html5_geolocation_page()
            webbrowser.open(f'file://{html_file}')
            
            print("📱 Instructions:")
            print("1. Autorisez l'accès à votre position GPS")
            print("2. Copiez vos coordonnées GPS")
            print("3. Revenez dans CarOS")
            
            return None, "Interface GPS HTML5 ouverte"
            
        except Exception as e:
            print(f"❌ Erreur HTML5 GPS: {e}")
            return None, f"Erreur: {e}"
    
    def get_manual_location(self):
        """Interface pour saisie manuelle des coordonnées"""
        try:
            import tkinter.simpledialog as simpledialog
            
            coords_input = simpledialog.askstring(
                "Position GPS Manuelle",
                "Entrez vos coordonnées GPS:\n\nFormat: latitude, longitude\nExemple: 33.5731, -7.5898\n\n(Utilisez Google Maps pour les obtenir)",
                initialvalue="33.5731, -7.5898"
            )
            
            if coords_input:
                try:
                    parts = coords_input.replace(' ', '').split(',')
                    lat = float(parts[0])
                    lon = float(parts[1])
                    
                    # Vérification basique des coordonnées
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        return (lat, lon), f"Position manuelle définie: {lat:.4f}, {lon:.4f}"
                    else:
                        return None, "❌ Coordonnées GPS invalides"
                        
                except (ValueError, IndexError):
                    return None, "❌ Format de coordonnées incorrect"
            
            return None, "❌ Saisie annulée"
            
        except Exception as e:
            return None, f"❌ Erreur saisie manuelle: {e}"
    
    def get_improved_ip_location(self):
        """Géolocalisation IP améliorée avec plusieurs services"""
        services = [
            {
                'name': 'ipapi.co',
                'url': 'https://ipapi.co/json/',
                'lat_key': 'latitude',
                'lon_key': 'longitude',
                'city_key': 'city',
                'accuracy': 'Ville'
            },
            {
                'name': 'ip-api.com',
                'url': 'http://ip-api.com/json/',
                'lat_key': 'lat',
                'lon_key': 'lon',
                'city_key': 'city',
                'accuracy': 'Ville'
            },
            {
                'name': 'ipinfo.io',
                'url': 'https://ipinfo.io/json',
                'lat_key': None,  # Special handling for 'loc' field
                'lon_key': None,
                'city_key': 'city',
                'accuracy': 'Ville'
            }
        ]
        
        for service in services:
            try:
                print(f"🔍 Essai géolocalisation via {service['name']}...")
                response = requests.get(service['url'], timeout=8)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Gestion spéciale pour ipinfo.io
                    if service['name'] == 'ipinfo.io' and 'loc' in data:
                        lat, lon = map(float, data['loc'].split(','))
                        city = data.get('city', 'Inconnue')
                        return (lat, lon), f"{city} (via {service['name']}) - Précision: {service['accuracy']}"
                    
                    # Gestion standard
                    elif service['lat_key'] in data and service['lon_key'] in data:
                        lat = float(data[service['lat_key']])
                        lon = float(data[service['lon_key']])
                        city = data.get(service['city_key'], 'Inconnue')
                        
                        return (lat, lon), f"{city} (via {service['name']}) - Précision: {service['accuracy']}"
                        
            except Exception as e:
                print(f"❌ Échec {service['name']}: {e}")
                continue
        
        # Fallback vers position par défaut
        print("⚠️ Tous les services de géolocalisation ont échoué")
        return self.default_location, "Casablanca (position par défaut)"
    
    def get_current_location(self):
        """Obtient la position GPS avec plusieurs méthodes"""
        print(f"\n🗺️ Mode de géolocalisation: {self.precision_mode}")
        
        if self.precision_mode == "manual":
            coords, location_name = self.get_manual_location()
        elif self.precision_mode == "web":
            coords, location_name = self.get_html5_location()
        elif self.precision_mode == "ip":
            coords, location_name = self.get_improved_ip_location()
        else:  # mode "auto"
            # Essayer d'abord la géolocalisation IP améliorée
            coords, location_name = self.get_improved_ip_location()
        
        if coords:
            self.current_location = coords
            self.current_location_name = location_name
            print(f"✅ Position détectée: {location_name}")
            print(f"📍 Coordonnées: {coords[0]:.6f}, {coords[1]:.6f}")
        else:
            # Fallback vers position par défaut
            self.current_location = self.default_location
            self.current_location_name = "Casablanca (par défaut)"
            print("⚠️ Utilisation de la position par défaut")
        
        return self.current_location
    
    def switch_precision_mode(self, mode):
        """Change le mode de précision GPS"""
        valid_modes = ["auto", "ip", "manual", "web"]
        if mode in valid_modes:
            self.precision_mode = mode
            print(f"📡 Mode GPS changé vers: {mode}")
            return f"✅ Mode GPS: {mode}"
        else:
            return f"❌ Mode invalide. Modes disponibles: {', '.join(valid_modes)}"
    
    def test_all_location_methods(self):
        """teste toutes les méthodes de géolocalisation"""
        results = {}
        
        print("\n🧪 Test de toutes les méthodes de géolocalisation...\n")
        
        # Test 1: Géolocalisation IP améliorée
        print("1️⃣ Test géolocalisation IP améliorée...")
        coords, name = self.get_improved_ip_location()
        results["ip_advanced"] = {"coords": coords, "name": name}
        print(f"   Résultat: {name}")
        
        # Test 2: Interface HTML5 (ouverture seulement)
        print("\n2️⃣ Test interface HTML5 GPS...")
        html_file = self.create_html5_geolocation_page()
        results["html5"] = {"coords": None, "name": f"Interface créée: {html_file}"}
        print(f"   Interface HTML5 créée et prête")
        
        # Test 3: Position manuelle (simulation)
        print("\n3️⃣ Test position manuelle (simulation)...")
        results["manual"] = {"coords": (33.5831, -7.5998), "name": "Position manuelle simulée"}
        print(f"   Position manuelle configurée")
        
        # Résumé
        print("\n📊 RÉSUMÉ DES TESTS:")
        print("=" * 50)
        for method, result in results.items():
            print(f"{method.upper()}: {result['name']}")
        
        return results

    # CONSERVER LES MÉTHODES EXISTANTES POUR LA COMPATIBILITÉ
    def get_route_coordinates(self, start, end):
        """Génère des points intermédiaires pour simuler une route réaliste"""
        lat1, lon1 = start
        lat2, lon2 = end
        
        distance = geodesic(start, end).kilometers
        num_points = max(5, min(20, int(distance / 10)))
        
        route_points = [start]
        
        for i in range(1, num_points):
            progress = i / num_points
            lat = lat1 + (lat2 - lat1) * progress
            lon = lon1 + (lon2 - lon1) * progress
            
            import math
            variation = 0.005 * math.sin(progress * math.pi * 3)
            lat += variation
            lon += variation * 0.5
            
            route_points.append((lat, lon))
        
        route_points.append(end)
        return route_points
    
    def create_advanced_map(self, start, end, destination_name):
        """Génère une carte interactive colorée avec route stylée"""
        try:
           center = ((start[0] + end[0])/2, (start[1] + end[1])/2)
        
           distance = geodesic(start, end).kilometers
           if distance < 5:
            zoom = 13
           elif distance < 20:
            zoom = 11
           elif distance < 100:
            zoom = 9
           else:
            zoom = 7
        
        # Créer la carte avec un thème coloré
           m = folium.Map(
            location=center, 
            zoom_start=zoom,
            tiles=None  # On va ajouter nos propres tuiles
           )
        
        # Ajouter plusieurs couches de cartes colorées
           folium.TileLayer(
            'OpenStreetMap',
            name='OpenStreetMap',
            attr='OpenStreetMap'
           ).add_to(m)
        
           folium.TileLayer(
            'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
            name='Topographie Colorée',
            attr='OpenTopoMap',
            overlay=False,
            control=True
           ).add_to(m)
        
           folium.TileLayer(
            'CartoDB Voyager',
            name='Voyager (Coloré)',
            attr='CartoDB'
           ).add_to(m)
        
           folium.TileLayer(
            'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            name='Satellite',
            attr='Esri'
           ).add_to(m)
        
        # Marqueur de départ avec icône colorée personnalisée
           folium.Marker(
            start,
            popup=folium.Popup(f"""
            <div style="width:200px;">
                <h4 style="color:#2E7D32; margin:0;">🚗 Position Actuelle</h4>
                <p style="margin:5px 0;"><b>Coordonnées:</b><br>{start[0]:.4f}, {start[1]:.4f}</p>
                <p style="margin:5px 0; color:#1976D2;"><b>Heure:</b> {datetime.now().strftime('%H:%M')}</p>
            </div>
            """, max_width=250),
            tooltip="🚗 Votre position actuelle",
            icon=folium.Icon(
                color='green', 
                icon='play-circle', 
                prefix='fa',
                icon_color='white'
            )
           ).add_to(m)
        
        # Marqueur de destination avec style attractif
           folium.Marker(
            end,
            popup=folium.Popup(f"""
            <div style="width:200px;">
                <h4 style="color:#C62828; margin:0;">🎯 {destination_name}</h4>
                <p style="margin:5px 0;"><b>Coordonnées:</b><br>{end[0]:.4f}, {end[1]:.4f}</p>
                <p style="margin:5px 0; color:#FF6F00;"><b>Distance:</b> {distance:.1f} km</p>
            </div>
            """, max_width=250),
            tooltip=f"🎯 Destination: {destination_name}",
            icon=folium.Icon(
                color='red', 
                icon='flag-checkered', 
                prefix='fa',
                icon_color='white'
            )
           ).add_to(m)
        
        # Générer une route avec plusieurs points
           route_points = self.get_route_coordinates(start, end)
        
        # Route principale avec dégradé de couleurs
           folium.PolyLine(
            route_points,
            weight=8,
            color="#1B70C6",  # Bleu principal
            opacity=0.9,
            popup=f"📍 Route vers {destination_name}",
            tooltip="Cliquez pour plus d'infos"
           ).add_to(m)
        
        # Ombre de la route pour effet 3D
           folium.PolyLine(
            route_points,
            weight=12,
            color='#000000',
            opacity=0.3
           ).add_to(m)
        
        # Route de surbrillance colorée
           folium.PolyLine(
            route_points,
            weight=4,
            color="#C74FFF",  # Jaune doré
            opacity=0.8
           ).add_to(m)
        
        # Ajouter des marqueurs intermédiaires colorés
           if len(route_points) > 4:
            # Point milieu
            mid_point = route_points[len(route_points)//2]
            folium.CircleMarker(
                mid_point,
                radius=8,
                popup="🔄 Point intermédiaire",
                color="#0000FF",  # Orange
                fill=True,
                fillColor="#3007FF",  # Ambre
                fillOpacity=0.8,
                weight=3
            ).add_to(m)
            
            # Points de passage supplémentaires
            for i in range(1, len(route_points)-1, max(1, len(route_points)//5)):
                if i != len(route_points)//2:  # Éviter le point milieu
                    folium.CircleMarker(
                        route_points[i],
                        radius=4,
                        color="#4E4CAF",  # Vert
                        fill=True,
                        fillColor="#4A82C3",  # Vert clair
                        fillOpacity=0.6,
                        weight=2
                    ).add_to(m)
        
        # Informations de route dans un panneau coloré
            distance = geodesic(start, end).kilometers
            estimated_time = (distance / 50) * 60
        
           info_html = f"""
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 280px; 
                    background: linear-gradient(135deg, #1976D2 0%, #42A5F5 100%);
                    border: none; border-radius: 15px;
                    z-index: 9999; font-size: 14px; padding: 20px;
                    color: white; box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
            
            <h3 style="margin: 0 0 15px 0; color: #FFD54F; font-size: 18px;">
                🧭 Navigation CarOS
            </h3>
            
            <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 8px; margin-bottom: 10px;">
                <p style="margin: 5px 0; font-weight: bold;">
                    📏 <span style="color: #FFD54F;">Distance:</span> {distance:.1f} km
                </p>
                <p style="margin: 5px 0; font-weight: bold;">
                    ⏱️ <span style="color: #FFD54F;">Temps estimé:</span> {estimated_time:.0f} min
                </p>
            </div>
            
            <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 8px;">
                <p style="margin: 5px 0; font-weight: bold;">
                    🎯 <span style="color: #FFD54F;">Destination:</span>
                </p>
                <p style="margin: 5px 0; font-size: 16px; color: #E3F2FD;">
                    {destination_name}
                </p>
            </div>
            
            <div style="text-align: center; margin-top: 15px; font-size: 12px; opacity: 0.8;">
                🚗 CarOS Navigation Premium
            </div>
        </div>
        """
           m.get_root().html.add_child(folium.Element(info_html))
        
        # Zone de départ avec cercle coloré
           folium.Circle(
            start,
            radius=200,  # 200m autour du départ
            popup="Zone de départ",
            color="#5042CE",
            fill=True,
            fillColor="#4A70C3",
            fillOpacity=0.2,
            weight=2
           ).add_to(m)
        
        # Zone d'arrivée avec cercle coloré
           folium.Circle(
            end,
            radius=300,  # 300m autour de l'arrivée
            popup=f"Zone d'arrivée - {destination_name}",
            color="#B836F4",
            fill=True,
            fillColor='#FFCDD2',
            fillOpacity=0.2,
            weight=2
           ).add_to(m)
        
        # Ajouter des plugins pour une meilleure interactivité
           plugins.Fullscreen(
            position='topleft',
            title='Plein écran',
            title_cancel='Quitter plein écran',
            force_separate_button=True
           ).add_to(m)
        
        # Mesurer les distances
           plugins.MeasureControl(
            position='bottomleft',
            primary_length_unit='kilometers',
            secondary_length_unit='miles'
           ).add_to(m)
        
        # Contrôleur de couches avec style
           folium.LayerControl(
            position='topright',
            collapsed=False
           ).add_to(m)
        
        # Plugin de localisation
           plugins.LocateControl(
            auto_start=False,
            position='topleft'
           ).add_to(m)
        
        # Sauvegarde avec CSS personnalisé
           map_file = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
           m.save(map_file.name)
        
        # Ajouter du CSS personnalisé au fichier
           with open(map_file.name, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # CSS pour améliorer l'apparence
            custom_css = """
        <style>
        .leaflet-container {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .leaflet-popup-content-wrapper {
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .leaflet-popup-content {
            font-family: 'Segoe UI', sans-serif;
        }
        .leaflet-control-layers {
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        </style>
        """
        
        # Insérer le CSS avant </head>
           html_content = html_content.replace('</head>', f'{custom_css}</head>')
        
           with open(map_file.name, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
           return map_file.name
        
        except Exception as e:
           print(f"❌ Erreur création carte colorée: {e}")
        return None
    def extract_destination(self, command):
        """Extrait la destination de la commande - Version améliorée"""
        if not self.langchain_manager or not self.langchain_manager.is_available():
            return self._smart_extract(command)
            
        try:
            prompt = f'''Extrait UNIQUEMENT le nom du lieu de destination de: "{command}"
Réponds en JSON: {{"destination": "nom_lieu"}}'''
            
            response = self.langchain_manager.get_response(prompt)
            json_match = re.search(r'\{.*\}', response)
            if json_match:
                result = json.loads(json_match.group())
                return result.get("destination")
        except:
            pass
            
        return self._smart_extract(command)
    
    def _smart_extract(self, text):
        """Extraction intelligente de destination"""
        text = text.lower().strip()
        
        triggers = ["aller", "va", "navigation", "route", "vers", "à", "direction"]
        
        for trigger in triggers:
            if trigger in text:
                parts = text.split(trigger, 1)
                if len(parts) > 1:
                    destination = parts[1].strip()
                    destination = destination.replace("à", "").replace("vers", "").strip()
                    if destination:
                        return destination
        
        for fav in self.favorites.keys():
            if fav in text:
                return fav
                
        return None
    
    def start_navigation(self, command):
        """Lance la navigation avec GPS et route colorée"""
        destination = self.extract_destination(command)
        if not destination:
            return "❌ Destination non comprise. Essayez: 'Navigation vers Casablanca'"
        
        start_coords = self.get_current_location()
        end_coords = self.get_coordinates(destination)
        
        if not end_coords:
            return f"❌ Lieu '{destination}' introuvable"
        
        distance_to_destination = geodesic(start_coords, end_coords).kilometers
        if distance_to_destination < 0.5:
            return f"✅ Vous êtes déjà à {destination} !"
        
        route_info = self.calculate_route(start_coords, end_coords)
        if not route_info["valid"]:
            return "❌ Calcul de route impossible"
        
        map_file = self.create_advanced_map(start_coords, end_coords, destination)
        
        self.route_active = True
        self.destination = destination
        
        result = f"✅ Navigation GPS active vers {destination.title()}\n"
        result += f"📍 Position actuelle: {getattr(self, 'current_location_name', 'Position détectée')}\n"
        result += f"📏 Distance: {route_info['distance']} km\n"
        result += f"⏱️ Temps estimé: {route_info['time']} min\n"
        result += f"🧭 Direction: {self._get_direction(start_coords, end_coords)}"
        
        if map_file:
            webbrowser.open(f'file://{map_file}')
            result += "\n🗺️ Carte interactive ouverte avec route colorée"
        
        return result
    
    def _get_location_name(self, coords):
        """Obtient le nom du lieu à partir des coordonnées"""
        try:
            location = self.geolocator.reverse(coords, timeout=5)
            if location:
                return location.address.split(',')[0]
        except:
            pass
        return f"{coords[0]:.3f}, {coords[1]:.3f}"
    
    def _get_direction(self, start, end):
        """Calcule la direction générale"""
        lat_diff = end[0] - start[0]
        lon_diff = end[1] - start[1]
        
        if abs(lat_diff) > abs(lon_diff):
            return "Nord" if lat_diff > 0 else "Sud"
        else:
            return "Est" if lon_diff > 0 else "Ouest"
    
    def get_coordinates(self, location_name):
        """Obtient les coordonnées avec géocodage amélioré"""
        if not location_name:
            return None
            
        location_name = location_name.lower().strip()
        
        if location_name in self.favorites:
            return self.favorites[location_name]
        
        for fav_key, coords in self.favorites.items():
            if location_name in fav_key or fav_key in location_name:
                return coords
        
        try:
            search_query = f"{location_name}, Maroc"
            location = self.geolocator.geocode(search_query, timeout=10)
            
            if location:
                return (location.latitude, location.longitude)
            
            location = self.geolocator.geocode(location_name, timeout=10)
            if location:
                return (location.latitude, location.longitude)
                
        except Exception as e:
            print(f"❌ Erreur géocodage: {e}")
            
        return None
    
    def calculate_route(self, start, end):
        """Calcule distance et temps avec plus de précision"""
        try:
            distance = geodesic(start, end).kilometers
            
            if distance < 5:
                avg_speed = 30
            elif distance < 50:
                avg_speed = 60
            else:
                avg_speed = 100
            
            time_hours = distance / avg_speed
            time_minutes = time_hours * 60
            
            return {
                "distance": round(distance, 1), 
                "time": round(time_minutes), 
                "valid": True,
                "avg_speed": avg_speed
            }
        except:
            return {"distance": 0, "time": 0, "valid": False}
    
    def stop_navigation(self):
        """Arrête la navigation"""
        if self.route_active:
            dest = self.destination
            self.route_active = False
            self.destination = None
            return f"✅ Navigation vers {dest} arrêtée"
        return "❌ Aucune navigation active"
    
    def get_status(self):
        """Statut navigation"""
        if self.route_active:
            return f"🧭 Navigation active → {self.destination}"
        return "🧭 Navigation inactive"
    
    def test_gps_location(self):
        """Teste et affiche la géolocalisation actuelle"""
        print("\n🔍 Test de géolocalisation...")
        coords, location_name = self.get_improved_ip_location()
    
        result = f"🌍 Position GPS détectée :\n"
        result += f"📍 Lieu: {location_name}\n"
        result += f"🗺️ Latitude: {coords[0]:.6f}\n"
        result += f"🗺️ Longitude: {coords[1]:.6f}"
    
        return result
    
# 3. CLASSE LANGCHAIN MANAGER (à ajouter après CarSystem)
class LangChainManager:
    def __init__(self):
        """Initialise le gestionnaire LangChain"""
        self.llm = None
        self.conversation_chain = None
        self.memory = None
        self.output_parser = CarAssistantOutputParser()
        
        # Initialiser LangChain
        self.setup_langchain()
    
    def setup_langchain(self):
        """Configure LangChain avec Ollama"""
        try:
            # Configuration du LLM Ollama (ou LM Studio)
            self.llm = Ollama(
                model="llama3.2:1b",  # Modèle Ollama
                base_url="http://localhost:11434",  # URL Ollama par défaut
                temperature=0.3,
                num_predict=100,  # Limiter les tokens pour des réponses courtes
            )
            
            # Mémoire conversationnelle (garde les 6 derniers échanges)
            self.memory = ConversationBufferWindowMemory(
                k=6,
                return_messages=True,
                memory_key="chat_history"
            )
            
            # Template de prompt personnalisé pour l'assistant auto
            prompt_template = PromptTemplate(
                input_variables=["chat_history", "input"],
                template="""Tu es un assistant vocal intelligent pour automobile nommé CarOS.

RÈGLES IMPORTANTES:
- Réponds TOUJOURS en français
- Sois concis (maximum 2 phrases courtes)
- Adapte-toi au contexte automobile
- Sois professionnel mais convivial
- Si on te demande des actions sur la voiture, explique que les commandes système sont gérées séparément

Historique de conversation:
{chat_history}

Utilisateur: {input}

Assistant CarOS:"""
            )
            
            # Chaîne de conversation
            self.conversation_chain = ConversationChain(
                llm=self.llm,
                memory=self.memory,
                prompt=prompt_template,
                output_parser=self.output_parser,
                verbose=False  # Mettre True pour debug
            )
            
            print("✅ LangChain initialisé avec succès")
            return True
            
        except Exception as e:
            print(f"❌ Erreur initialisation LangChain: {e}")
            # Fallback vers l'ancien système
            self.llm = None
            return False
    
    def get_response(self, user_input: str) -> str:
        """Obtient une réponse via LangChain"""
        try:
            if not self.conversation_chain:
                return "Service IA non disponible"
            
            # Générer la réponse
            response = self.conversation_chain.predict(input=user_input)
            return response.strip()
            
        except Exception as e:
            print(f"❌ Erreur LangChain: {e}")
            return "Désolé, je rencontre un problème technique."
    
    def clear_memory(self):
        """Efface la mémoire conversationnelle"""
        if self.memory:
            self.memory.clear()
    
    def is_available(self) -> bool:
        """Vérifie si LangChain est disponible"""
        return self.llm is not None

# ========== GESTIONNAIRE AUDIO ==========
class AudioManager:
    def __init__(self):
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 0.9)
        self.whisper_model = WhisperModel(WHISPER_MODEL, device="cpu")
        
        self.is_recording = False
        self.audio_data = []
        self.is_speaking = False  # AJOUTER CETTE LIGNE
        
    def speak(self, text):
        """Synthèse vocale"""
        try:
            self.is_speaking = True  # AJOUTER
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            self.is_speaking = False  # AJOUTER
        except:
            self.is_speaking = False  # AJOUTER
            pass
    def stop_speaking(self):  # AJOUTER CETTE MÉTHODE
        """Arrête la synthèse vocale"""
        try:
           self.tts_engine.stop()
           self.is_speaking = False
        except:
          pass
    def start_recording(self):
        """Démarre l'enregistrement"""
        self.is_recording = True
        self.audio_data = []
        
        def callback(indata, frames, time, status):
            if self.is_recording:
                self.audio_data.append(indata.copy())
        
        self.stream = sd.InputStream(callback=callback, channels=1, 
                                   samplerate=RATE, dtype='int16')
        self.stream.start()
    
    def stop_recording(self):
        """Arrête l'enregistrement et retourne le fichier audio"""
        if not self.is_recording:
            return None
            
        self.is_recording = False
        self.stream.stop()
        self.stream.close()
        
        if not self.audio_data:
            return None
        
        # Sauvegarde audio
        audio_array = np.concatenate(self.audio_data, axis=0)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            with wave.open(tmp.name, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(RATE)
                wf.writeframes(audio_array.tobytes())
            return tmp.name
    
    def transcribe(self, audio_file):
        """Transcrit l'audio en texte"""
        try:
            segments, _ = self.whisper_model.transcribe(audio_file, language="fr")
            return "".join([s.text for s in segments]).strip()
        except:
            return ""
class VoiceAssistantGUI:
    def __init__(self):
        self.car_system = CarSystem()
        self.audio_manager = AudioManager()
        self.tts_enabled = True
        self.conversation_manager = ConversationManager()
        self.qr_window = None  # AJOUTER cette ligne
        
        # NOUVEAU: Initialiser LangChain
        self.langchain_manager = LangChainManager()
        self.car_system.navigation_system = NavigationSystem(self.langchain_manager)
        self.setup_ui()
    
    def create_new_chat(self):
        """Crée un nouveau chat avec options de sauvegarde"""
        current_chat_info = self.conversation_manager.get_current_chat_info()
    
    # Si le chat actuel contient des messages
        if current_chat_info["has_messages"]:
        # Proposer de sauvegarder
           response = messagebox.askyesnocancel(
            "💬 Nouveau Chat",
            f"Chat actuel: '{current_chat_info['title']}'\n"
            f"Messages: {current_chat_info['message_count']}\n\n"
            f"Voulez-vous sauvegarder avant de créer un nouveau chat ?\n\n"
            f"• Oui = Sauvegarder et nouveau chat\n"
            f"• Non = Nouveau chat sans sauvegarder\n"
            f"• Annuler = Rester sur le chat actuel"
          )
        
        if response is None:  # Annuler
            return
        elif response:  # Oui - Sauvegarder
            if not self.save_conversation_with_custom_title():
                return  # Si sauvegarde échoue, annuler
        # Si Non, continuer sans sauvegarder
    
    # Créer le nouveau chat
        new_chat_title = self.conversation_manager.create_new_chat(auto_save_current=False)
    
    # Vider l'interface et réinitialiser
        self.clear_chat_ui_only()
    
    # Effacer la mémoire LangChain pour un nouveau contexte
        if hasattr(self, 'langchain_manager'):
           self.langchain_manager.clear_memory()
    
    # Message de bienvenue du nouveau chat
        self.add_welcome_message_new_chat(new_chat_title)
    
    # Mettre à jour le titre de la fenêtre
        self.update_window_title()
    
    # Notification
        self.add_message(f"✨ Nouveau chat créé : '{new_chat_title}'", "system")

    def save_conversation_with_custom_title(self):
        """Sauvegarde avec titre personnalisé"""
        current_info = self.conversation_manager.get_current_chat_info()
    
        title = tk.simpledialog.askstring(
          "💾 Sauvegarder la conversation",
          f"Titre pour cette conversation :\n({current_info['message_count']} messages)",
          initialvalue=current_info["title"],
          parent=self.window
        )
    
        if title:
           if self.conversation_manager.save_current_conversation(title):
             messagebox.showinfo("✅ Succès", f"Conversation '{title}' sauvegardée !")
             return True
           else:
             messagebox.showerror("❌ Erreur", "Impossible de sauvegarder la conversation")
             return False
        return False
    
    def clear_chat_ui_only(self):
        """Vide seulement l'interface sans toucher à la gestion des conversations"""
        self.chat_box.delete(1.0, tk.END)

    def add_welcome_message_new_chat(self, chat_title):
        """Message de bienvenue pour nouveau chat"""
        nav_ok = hasattr(self.car_system, 'navigation_system')
        llm_ok = hasattr(self, 'langchain_manager') and self.langchain_manager.is_available()
    
        welcome = f"""✨ {chat_title}

    🔄 Nouveau contexte de conversation démarré
    🧠 Mémoire IA réinitialisée pour une expérience fraîche

    🔗 LangChain: {"✅ Actif" if llm_ok else "⚠️ Limité"}
    🧭 Navigation: {"✅ GPS Smart avec Routes" if nav_ok else "⚠️ Indisponible"}

    COMMANDES VOCALES DISPONIBLES:
🌡️ "Allume la climatisation" • "Température à 24 degrés"
🪟 "Ouvre les vitres" • "Ferme toutes les vitres"  
🎵 "Lance la musique" • "Volume plus fort" • "Piste suivante"
🗺️ "Navigation vers Paris" • "Aller à la maison"
📞 "Appelle [NOM]" • "Message à [NOM]"
🔍 "Recherche [SUJET]" • "Trouve des infos sur..."
📍 "Ma position" • "Où suis-je ?"

Cliquez "Démarrer" pour commencer !
"""
        self.add_message(welcome, "welcome")

    def update_window_title(self):
        """Met à jour le titre de la fenêtre avec le chat actuel"""
        chat_info = self.conversation_manager.get_current_chat_info()
        window_title = f"🚘 CarOS - {chat_info['title']} ({chat_info['message_count']} messages)"
        self.window.title(window_title)
    def get_ai_response_with_langchain(self, text):
        """Obtient une réponse IA via LangChain avec fallback"""
        try:
            # Priorité 1: LangChain si disponible
            if self.langchain_manager.is_available():
               return self.langchain_manager.get_response(text)
        
        # Priorité 2: Gemini si internet disponible
            elif internet_ok():
               return ask_gemini(text)
        
        # Priorité 3: LM Studio local
            else:
               payload = {
                  "model": MODEL_NAME,
                  "messages": [
                    {"role": "system", "content": "Tu es CarOS, assistant vocal automobile. Réponds en français, maximum 2 phrases."},
                    {"role": "user", "content": text}
                   ],
                   "temperature": 0.3,
                   "max_tokens": 100
               }
            
               response = requests.post(LM_URL, headers=HEADERS, json=payload, timeout=10)
               if response.status_code == 200:
                   return response.json()["choices"][0]["message"]["content"]
               else:
                return "Service IA temporairement indisponible."
                
        except Exception as e:
            print(f"❌ Erreur IA: {e}")
        return "Désolé, problème technique temporaire."

    # AJOUTER CETTE NOUVELLE MÉTHODE
    def show_qr_code(self, qr_image, title="QR Code"):
        """Affiche le QR code dans une fenêtre popup"""
        # Fermer l'ancienne fenêtre QR si elle existe
        if self.qr_window and self.qr_window.winfo_exists():
            self.qr_window.destroy()
        
        # Créer une nouvelle fenêtre
        self.qr_window = ttk.Toplevel(self.window)
        self.qr_window.title(f"📱 {title}")
        self.qr_window.geometry("400x500")
        self.qr_window.resizable(False, False)
        
        # Convertir l'image PIL en format Tkinter
        # Redimensionner le QR code pour un meilleur affichage
        qr_resized = qr_image.resize((300, 300), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(qr_resized)
        
        # Frame principal
        main_frame = ttk.Frame(self.qr_window)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Titre
        title_label = ttk.Label(main_frame, text=title, 
                               font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # QR Code
        qr_label = ttk.Label(main_frame, image=photo)
        qr_label.image = photo  # Garder une référence
        qr_label.pack(pady=10)
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                                text="📱 Scannez avec votre iPhone\npour exécuter l'action",
                                font=("Segoe UI", 12),
                                justify="center")
        instructions.pack(pady=10)
        
        # Bouton fermer
        close_btn = ttk.Button(main_frame, text="✅ Fermer", 
                              command=self.qr_window.destroy,
                              bootstyle="primary")
        close_btn.pack(pady=20)
        
        # Centrer la fenêtre
        self.qr_window.transient(self.window)
        self.qr_window.grab_set()
    def setup_ui(self):
        """Configuration de l'interface - Design Professionnel"""
        # Fenêtre principale avec style moderne
        self.window = ttk.Window(themename="cosmo")  # Au lieu de "darkly"  # Thème sombre professionnel
        self.window.title("🚘 CarOS - Assistant Vocal Professionnel")
        self.window.geometry("1200x800")
        self.window.minsize(1000, 700)
        
        # Container principal
        main_container = ttk.Frame(self.window)
        main_container.pack(fill=BOTH, expand=True)
        
        # En-tête avec design premium
        self.create_premium_header(main_container)
        
        # Layout principal en grid
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=BOTH, expand=True, padx=30, pady=20)
        
        # Sidebar gauche - Contrôles
        self.create_sidebar(content_frame)
        
        # Zone centrale - Chat
        self.create_premium_chat_area(content_frame)
        
        # Panel droit - Status
        self.create_status_panel(content_frame)
        
        # Footer moderne
        self.create_footer(main_container)
        
        # Message de bienvenue
        self.add_welcome_message()
        

    def create_premium_header(self, parent):
        """En-tête premium avec design moderne"""
        header_frame = ttk.Frame(parent, height=100)
        header_frame.pack(fill=X, padx=30, pady=(20, 0))
        header_frame.pack_propagate(False)
        
        # Logo et titre
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=LEFT, fill=Y)
        
        # Icône et titre principal
        main_title = ttk.Label(title_frame, text="🚘 CarOS", 
                              font=("Segoe UI", 32, "bold"),
                      foreground="#1976d2")
        main_title.pack(anchor="w")
        
        subtitle = ttk.Label(title_frame, text="Assistant Vocal Intelligent • Version Pro", 
                            font=("Segoe UI", 14))
        subtitle.pack(anchor="w", pady=(5, 0))
        
        # Indicateurs de statut en temps réel
        status_frame = ttk.Frame(header_frame)
        status_frame.pack(side=RIGHT, fill=Y)
        
        # Indicateurs LED
        self.connection_led = ttk.Label(status_frame, text="●", foreground="#704caf", 
                                       font=("Segoe UI", 16))
        self.connection_led.pack(side=RIGHT, padx=(10, 0))
        
        ttk.Label(status_frame, text="Système", 
                 font=("Segoe UI", 10)).pack(side=RIGHT)

# ========== CORRECTION 1: create_sidebar SIMPLIFIÉ ==========
    def create_sidebar(self, parent):
        """Sidebar gauche avec contrôles - Version sans erreurs"""
        sidebar = ttk.LabelFrame(parent, text="⚡ Contrôles", 
                            padding=20, width=250)
        sidebar.pack(side=LEFT, fill=Y, padx=(0, 20))
        sidebar.pack_propagate(False)
    
    # Bouton principal
        self.record_btn = ttk.Button(
            sidebar, text="🎙️ Démarrer", bootstyle="primary",
            command=self.toggle_recording, width=20
        )
        self.record_btn.pack(pady=(0, 10), ipady=8)
       
        # NOUVEAU: Bouton Nouveau Chat
        new_chat_btn = ttk.Button(
        sidebar, text="➕ Nouveau Chat", bootstyle="success",
        command=self.create_new_chat, width=20
        )
        new_chat_btn.pack(pady=5, ipady=6)
    # Boutons de gestion
        history_btn = ttk.Button(
           sidebar, text="📚 Historique", bootstyle="info",
           command=self.open_history, width=20
        )
        history_btn.pack(pady=5, ipady=6)
    
        save_btn = ttk.Button(
            sidebar, text="💾 Sauvegarder", bootstyle="success-outline",
            command=self.save_conversation, width=20
         )
        save_btn.pack(pady=5, ipady=6)
    
    # Séparateur
        ttk.Separator(sidebar, orient="horizontal").pack(fill=X, pady=15)
    
    # Contrôles secondaires
        controls_grid = ttk.Frame(sidebar)
        controls_grid.pack(fill=X, pady=10)
    
        self.audio_btn = ttk.Button(
           controls_grid, text="🔊", bootstyle="success-outline",
           command=self.toggle_tts, width=8
        )
        self.audio_btn.grid(row=0, column=0, padx=(0, 5), ipady=5)
    
        # REMPLACER le bouton status existant par :
        detail_status_btn = ttk.Button(
            controls_grid, text="📊", bootstyle="info-outline",
            command=self.show_detailed_status, width=8  # Utilise la nouvelle méthode
        )
        detail_status_btn.grid(row=0, column=1, padx=5, ipady=5)
    
        clear_btn = ttk.Button(
           controls_grid, text="🗑️", bootstyle="warning-outline",
           command=self.clear_chat, width=8
        )
        clear_btn.grid(row=0, column=2, padx=(5, 0), ipady=5)
    
    # Stop Audio
        self.stop_audio_btn = ttk.Button(
           controls_grid, text="⏹️ Stop Audio", bootstyle="danger-outline",
           command=self.stop_ai_speech, width=20
        )
        self.stop_audio_btn.grid(row=1, column=0, columnspan=3, pady=(5, 0), ipady=5)
    
    # Séparateur
        ttk.Separator(sidebar, orient="horizontal").pack(fill=X, pady=15)
    
    # Actions rapides SIMPLIFIÉES (sans erreur)
        shortcuts_frame = ttk.LabelFrame(sidebar, text="⚡ Actions Rapides", padding=10)
        shortcuts_frame.pack(fill=X, pady=10)
    
    # Boutons simples avec lambda (évite les erreurs de méthodes manquantes)
        climate_btn = ttk.Button(shortcuts_frame, text="🌡️ Climat", 
                           bootstyle="primary-outline", width=18,
                           command=lambda: self.quick_action("allume la climatisation"))
        climate_btn.pack(pady=2, ipady=3)
    
        music_btn = ttk.Button(shortcuts_frame, text="🎵 Musique", 
                         bootstyle="success-outline", width=18,
                         command=lambda: self.quick_action("lance la musique"))
        music_btn.pack(pady=2, ipady=3)
    
        nav_btn = ttk.Button(shortcuts_frame, text="🧭 Navigation", 
                        bootstyle="info-outline", width=18,
                        command=self.open_navigation_safe)
        nav_btn.pack(pady=2, ipady=3)
    
        qr_btn = ttk.Button(shortcuts_frame, text="📱 QR Contact", 
                       bootstyle="warning-outline", width=18,
                       command=lambda: self.add_message("📱 Fonction QR en développement", "info"))
        qr_btn.pack(pady=2, ipady=3)
        
        web_btn = ttk.Button(shortcuts_frame, text="🌐 Interface Web", 
                    bootstyle="info-outline", width=18,
                    command=self.create_web_interface)
        web_btn.pack(pady=2, ipady=3)
    # Label de statut (pour éviter l'erreur status_label)
        self.status_label = ttk.Label(sidebar, text="🟢 Prêt", font=("Segoe UI", 10))
        self.status_label.pack(pady=10)

    # AJOUTER CETTE NOUVELLE MÉTHODE
    def quick_qr_contact(self):
        """Action rapide pour générer un QR contact"""
        import tkinter.simpledialog as simpledialog
        
        contact_name = simpledialog.askstring(
            "QR Contact", 
            "Nom du contact pour QR code :",
            parent=self.window
        )
        
        if contact_name:
            # Demander le type d'action
            action = messagebox.askyesnocancel(
                "Type d'action", 
                f"Que faire avec {contact_name} ?\n\nOui = Appel\nNon = SMS\nAnnuler = Vérification"
            )
            
            if action is True:  # Appel
                qr_image, message = self.car_system.generer_qr_raccourci(contact_name, "call")
                if qr_image:
                    self.show_qr_code(qr_image, f"Appeler {contact_name}")
                self.add_message(f"📱 {message}", "system")
                
            elif action is False:  # SMS
                qr_image, message = self.car_system.generer_qr_raccourci(contact_name, "sms")
                if qr_image:
                    self.show_qr_code(qr_image, f"SMS à {contact_name}")
                self.add_message(f"📱 {message}", "system")
                
            else:  # Vérification
                qr_image, message = self.car_system.generer_qr_verification(contact_name)
                if qr_image:
                    self.show_qr_code(qr_image, f"Vérifier {contact_name}")
                self.add_message(f"📱 {message}", "system")

    def create_default_css(self):
        """Crée le fichier CSS par défaut s'il n'existe pas"""
        try:
            css_default = """/* CarOS - Style par défaut */
:root {
    --primary-blue: #1976d2;
    --success-green: #4caf50;
    --warning-orange: #ff9800;
    --background-white: #ffffff;
}

.main-window {
    font-family: 'Segoe UI', sans-serif;
    background: #fafafa;
}"""
        
            with open('style.css', 'w', encoding='utf-8') as f:
              f.write(css_default)
            
              print("✅ Fichier style.css créé avec succès")
        
        except Exception as e:
           print(f"❌ Erreur création CSS: {e}")
    def create_premium_chat_area(self, parent):
        """Zone de chat premium"""
        chat_container = ttk.LabelFrame(parent, text="💬 Conversation Intelligence", padding=20)
        chat_container.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 20))
        
        # Chat avec design moderne
        self.chat_box = scrolledtext.ScrolledText(
            chat_container, wrap=tk.WORD, font=("Segoe UI", 12),
            relief="flat", borderwidth=0, height=25
        )
        self.chat_box.pack(fill=BOTH, expand=True)
        
        # Styles de texte premium
        # Styles de texte premium avec couleurs CSS
        self.chat_box.tag_config("user", 
                        foreground="#193bd2",  # primary-blue du CSS
                        font=("Segoe UI", 12, "bold"))
        self.chat_box.tag_config("assistant", 
                        foreground="#7b1fa2",  # primary-violet du CSS  
                        font=("Segoe UI", 12, "bold"))
        self.chat_box.tag_config("system", 
                        foreground="#614caf",  # success du CSS
                        font=("Segoe UI", 12, "bold"))
        self.chat_box.tag_config("search", 
                        foreground="#aa00ff",  # warning du CSS
                        font=("Segoe UI", 11))
        self.chat_box.tag_config("timestamp", foreground="#616161", font=("Consolas", 9))           # Gris moyen
        self.chat_box.tag_config("welcome", foreground="#7b1fa2", font=("Segoe UI", 11))            # Violet foncé

    def create_status_panel(self, parent):
        """Panel de statut en temps réel"""
        status_panel = ttk.LabelFrame(parent, text="📊 État Système", 
                                     padding=15, width=280)
        status_panel.pack(side=RIGHT, fill=Y)
        status_panel.pack_propagate(False) 
        # Séparateur
        ttk.Separator(status_panel, orient="horizontal").pack(fill=X, pady=10)
        
        # Métriques en temps réel
        metrics_frame = ttk.Frame(status_panel)
        metrics_frame.pack(fill=X, pady=(0, 15))
        
        # Indicateur de charge CPU simulé
        cpu_frame = ttk.Frame(metrics_frame)
        cpu_frame.pack(fill=X, pady=5)
        
        ttk.Label(cpu_frame, text="🔋 Système", font=("Segoe UI", 10)).pack(anchor="w")
        
        self.cpu_progress = ttk.Progressbar(cpu_frame, length=200, mode="determinate", 
                                           bootstyle="success", value=75)
        self.cpu_progress.pack(fill=X, pady=2)
        
        # Indicateur réseau
        network_frame = ttk.Frame(metrics_frame)
        network_frame.pack(fill=X, pady=5)
        
        ttk.Label(network_frame, text="🌐 Réseau", font=("Segoe UI", 10)).pack(anchor="w")
        
        self.network_progress = ttk.Progressbar(network_frame, length=200, mode="determinate",
                                              bootstyle="info", value=90)
        self.network_progress.pack(fill=X, pady=2)
        # Ajouter après self.network_progress.pack(fill=X, pady=2)

# Indicateur IA
        ai_frame = ttk.Frame(metrics_frame)
        ai_frame.pack(fill=X, pady=5)

        ttk.Label(ai_frame, text="🤖 IA", font=("Segoe UI", 10)).pack(anchor="w")

        self.ai_status = ttk.Label(ai_frame, text="Gemini ✅" if internet_ok() else "Local ⚠️", 
                          font=("Segoe UI", 9))
        self.ai_status.pack(anchor="w", pady=2)

        # Indicateur LangChain
        langchain_frame = ttk.Frame(metrics_frame)
        langchain_frame.pack(fill=X, pady=5)

        ttk.Label(langchain_frame, text="🔗 LangChain", font=("Segoe UI", 10)).pack(anchor="w")

        self.langchain_status = ttk.Label(langchain_frame, 
                                 text="Actif ✅" if hasattr(self, 'langchain_manager') and self.langchain_manager.is_available() else "Indisponible ⚠️", 
                                 font=("Segoe UI", 9))
        self.langchain_status.pack(anchor="w", pady=2)

        # Statut Navigation
        nav_frame = ttk.Frame(metrics_frame)
        nav_frame.pack(fill=X, pady=5)
        
        ttk.Label(nav_frame, text="🧭 Navigation", font=("Segoe UI", 10)).pack(anchor="w")
        nav_status = "Prêt ✅" if hasattr(self.car_system, 'navigation_system') else "⚠️ Indisponible"
        self.nav_indicator = ttk.Label(nav_frame, text=nav_status, font=("Segoe UI", 9))
        self.nav_indicator.pack(anchor="w", pady=2)
        # Séparateur
        ttk.Separator(status_panel, orient="horizontal").pack(fill=X, pady=15)
        
        # État des composants
        components_frame = ttk.LabelFrame(status_panel, text="🚗 Véhicule", padding=10)
        components_frame.pack(fill=X, pady=10)
        
        # Grille d'état
        self.create_component_indicators(components_frame)
        
        # Horloge temps réel
        clock_frame = ttk.Frame(status_panel)
        clock_frame.pack(fill=X, pady=15)
        
        self.clock_label = ttk.Label(clock_frame, text="", foreground="#1976d2",  # Bleu foncé
                            font=("Consolas", 14, "bold"))
        self.clock_label.pack()
        
        # Démarrer l'horloge
        self.update_clock()
    

    def create_web_interface(self):
        """Crée une interface web simple pour le CarOS"""
        try:
           import tempfile
           import webbrowser
        
           html_content = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CarOS - Interface Web Premium</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --primary-blue: #1976d2;
            --secondary-blue: #42a5f5;
            --primary-purple: #7b1fa2;
            --secondary-purple: #ba68c8;
            --accent-violet: #9c27b0;
            --gradient-main: linear-gradient(135deg, #1976d2 0%, #7b1fa2 50%, #9c27b0 100%);
            --gradient-card: linear-gradient(145deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.9) 100%);
            --glass-bg: rgba(255, 255, 255, 0.1);
            --glass-border: rgba(255, 255, 255, 0.2);
            --shadow-soft: 0 8px 32px rgba(0, 0, 0, 0.1);
            --shadow-strong: 0 20px 60px rgba(0, 0, 0, 0.3);
            --text-primary: #1a1a1a;
            --text-secondary: #6b7280;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--gradient-main);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow-x: hidden;
        }
        
        /* Animated background elements */
        .bg-decoration {
            position: absolute;
            width: 100%;
            height: 100%;
            top: 0;
            left: 0;
            pointer-events: none;
            overflow: hidden;
        }
        
        .bg-circle {
            position: absolute;
            border-radius: 50%;
            background: var(--glass-bg);
            backdrop-filter: blur(10px);
            animation: float 8s ease-in-out infinite;
        }
        
        .bg-circle:nth-child(1) {
            width: 300px;
            height: 300px;
            top: -150px;
            right: -150px;
            animation-delay: 0s;
        }
        
        .bg-circle:nth-child(2) {
            width: 200px;
            height: 200px;
            bottom: -100px;
            left: -100px;
            animation-delay: 2s;
        }
        
        .bg-circle:nth-child(3) {
            width: 150px;
            height: 150px;
            top: 50%;
            left: -75px;
            animation-delay: 4s;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            33% { transform: translateY(-20px) rotate(120deg); }
            66% { transform: translateY(10px) rotate(240deg); }
        }
        
        .container {
            max-width: 1000px;
            width: 100%;
            position: relative;
            z-index: 1;
        }
        
        .glass-card {
            background: var(--gradient-card);
            backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            border-radius: 24px;
            padding: 40px;
            box-shadow: var(--shadow-strong);
            position: relative;
            overflow: hidden;
        }
        
        .glass-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.4) 50%, transparent 100%);
        }
        
        .header {
            text-align: center;
            margin-bottom: 50px;
            position: relative;
        }
        
        .logo {
            font-size: 4rem;
            margin-bottom: 20px;
            filter: drop-shadow(0 4px 12px rgba(0,0,0,0.3));
            animation: pulse 3s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        .title {
            font-size: 3rem;
            font-weight: 700;
            background: var(--gradient-main);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
            line-height: 1.2;
        }
        
        .subtitle {
            font-size: 1.2rem;
            color: var(--text-secondary);
            font-weight: 400;
        }
        
        .status-card {
            background: var(--glass-bg);
            backdrop-filter: blur(15px);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 24px;
            margin: 20px 0;
            position: relative;
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .status-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.15);
        }
        
        .status-success {
            border-left: 4px solid #4caf50;
            background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(139, 195, 74, 0.05) 100%);
        }
        
        .status-info {
            border-left: 4px solid var(--primary-blue);
            background: linear-gradient(135deg, rgba(25, 118, 210, 0.1) 0%, rgba(66, 165, 245, 0.05) 100%);
        }
        
        .status-card h3 {
            font-size: 1.4rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-card p {
            color: var(--text-secondary);
            line-height: 1.6;
            font-size: 1rem;
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin: 30px 0;
        }
        
        .feature-card {
            background: var(--glass-bg);
            backdrop-filter: blur(15px);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 30px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .feature-card::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            transform: scale(0);
            transition: transform 0.6s ease;
        }
        
        .feature-card:hover::before {
            transform: scale(1);
        }
        
        .feature-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
            border-color: rgba(255,255,255,0.3);
        }
        
        .feature-card h4 {
            font-size: 1.3rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .feature-card ul {
            list-style: none;
            margin: 0;
            padding: 0;
        }
        
        .feature-card li {
            padding: 8px 0;
            color: var(--text-secondary);
            position: relative;
            padding-left: 25px;
            font-weight: 400;
            transition: color 0.3s ease;
        }
        
        .feature-card li::before {
            content: '▶';
            position: absolute;
            left: 0;
            color: var(--primary-blue);
            font-size: 0.8rem;
            transform: translateY(1px);
        }
        
        .feature-card:hover li {
            color: var(--text-primary);
        }
        
        .cta-section {
            text-align: center;
            margin-top: 50px;
            padding: 40px;
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            position: relative;
        }
        
        .cta-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 20%;
            right: 20%;
            height: 1px;
            background: var(--gradient-main);
        }
        
        .cta-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 25px;
        }
        
        .step {
            display: inline-block;
            background: var(--gradient-main);
            color: white;
            padding: 15px 25px;
            margin: 8px;
            border-radius: 50px;
            font-weight: 500;
            box-shadow: var(--shadow-soft);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .step::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.6s ease;
        }
        
        .step:hover::before {
            left: 100%;
        }
        
        .step:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: var(--text-secondary);
            font-size: 0.9rem;
        }
        
        .footer-gradient {
            background: var(--gradient-main);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 600;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
            
            .glass-card {
                padding: 25px;
            }
            
            .title {
                font-size: 2.2rem;
            }
            
            .subtitle {
                font-size: 1rem;
            }
            
            .features-grid {
                grid-template-columns: 1fr;
                gap: 20px;
            }
            
            .feature-card {
                padding: 20px;
            }
            
            .step {
                display: block;
                margin: 10px 0;
            }
        }
        
        /* Loading animation */
        .loading-spinner {
            width: 20px;
            height: 20px;
            border: 2px solid var(--glass-border);
            border-top: 2px solid var(--primary-blue);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            display: inline-block;
            margin-left: 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="bg-decoration">
        <div class="bg-circle"></div>
        <div class="bg-circle"></div>
        <div class="bg-circle"></div>
    </div>
    
    <div class="container">
        <div class="glass-card">
            <div class="header">
                <div class="logo">🚘</div>
                <h1 class="title">CarOS Premium</h1>
                <p class="subtitle">Assistant Vocal Intelligent • Nouvelle Génération</p>
            </div>
            
            <div class="status-card status-success">
                <h3>✅ Système Opérationnel <span class="loading-spinner"></span></h3>
                <p>L'assistant vocal CarOS est en ligne et optimisé pour votre expérience automobile. Tous les systèmes sont fonctionnels et prêts à recevoir vos commandes.</p>
            </div>
            
            <div class="status-card status-info">
                <h3>🚀 Fonctionnalités Premium Disponibles</h3>
                <div class="features-grid">
                    <div class="feature-card">
                        <h4>🎙️ Intelligence Vocale</h4>
                        <ul>
                            <li>Reconnaissance vocale avancée</li>
                            <li>Contrôle climatisation intelligente</li>
                            <li>Gestion automatique des vitres</li>
                            <li>Interface musicale intuitive</li>
                            <li>Navigation GPS temps réel</li>
                        </ul>
                    </div>
                    <div class="feature-card">
                        <h4>📱 Connectivité iPhone</h4>
                        <ul>
                            <li>Appels via codes QR sécurisés</li>
                            <li>Messages automatiques iOS</li>
                            <li>Synchronisation contacts iPhone</li>
                            <li>Contrôle musique iPhone</li>
                        </ul>
                    </div>
                    <div class="feature-card">
                        <h4>🤖 IA & Recherche</h4>
                        <ul>
                            <li>Assistant IA conversationnel</li>
                            <li>Recherche web en temps réel</li>
                            <li>Réponses contextuelles</li>
                        </ul>
                    </div>
                    <div class="feature-card">
                        <h4>🗺️ Navigation Avancée</h4>
                        <ul>
                            <li>GPS haute précision</li>
                            <li>Cartes interactives colorées</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="cta-section">
                <h2 class="cta-title">🎯 Guide de Démarrage Rapide</h2>
                <div class="step">1️⃣ Retournez à l'application desktop</div>
                <div class="step">2️⃣ Cliquez sur "🎙️ Démarrer" pour activer</div>
                <div class="step">3️⃣ Utilisez les QR codes pour iPhone</div>
            </div>
            
            <div class="footer">
                <p>Développé avec ❤️ pour une expérience automobile premium</p>
                <p class="footer-gradient">CarOS v2.0 Pro • Intelligence Artificielle & Recherche Web Intégrée</p>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        # Créer le fichier HTML temporaire
           html_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
           html_file.write(html_content)
           html_file.close()
        
        # Ouvrir dans le navigateur
           webbrowser.open(f'file://{html_file.name}')
        
           self.add_message("🌐 Interface web ouverte dans votre navigateur", "system")
        
        except Exception as e:
           self.add_message(f"❌ Erreur ouverture interface web: {e}", "system")


    # NOUVEAU: Méthode pour afficher l'état complet
    def show_detailed_status(self):
        """Affiche l'état complet du véhicule"""
        detailed_status = self.car_system.get_detailed_status()
        self.add_message(detailed_status, "system")
        
        if self.tts_enabled:
            # Version courte pour TTS
            summary = f"Véhicule sécurisé à {self.car_system.get_security_score()}%. "
            summary += f"Carburant à {self.car_system.engine['fuel']}%. "
            summary += f"Efficacité {self.car_system.get_energy_efficiency()}%."
            threading.Thread(target=lambda: self.audio_manager.speak(summary), daemon=True).start()

    def create_component_indicators(self, parent):
        """Indicateurs d'état des composants"""
        components = [
            ("🌡️", "Climat"),
            ("🪟", "Vitres"), 
            ("🎵", "Audio"),
            ("🗺️", "GPS")
        ]
        
        for i, (icon, name) in enumerate(components):
            row = i // 2
            col = i % 2
            
            comp_frame = ttk.Frame(parent)
            comp_frame.grid(row=row, column=col, padx=5, pady=3, sticky="w")
            
            ttk.Label(comp_frame, text=icon, font=("Segoe UI", 14)).pack(side=LEFT)
            ttk.Label(comp_frame, text=name, font=("Segoe UI", 10)).pack(side=LEFT, padx=(5, 0))

    def create_footer(self, parent):
        """Footer moderne"""
        footer = ttk.Frame(parent, height=50)
        footer.pack(fill=X, padx=30, pady=(10, 20))
        footer.pack_propagate(False)

        status_frame = ttk.Frame(footer)
        status_frame.pack(side=LEFT, fill=Y)
        
        # Status principal
        self.status_label = ttk.Label(
    footer, text="✅ Système Opérationnel", 
    font=("Segoe UI", 11, "bold"), foreground="#342fcd"  # Vert très foncé
)

        self.status_label.pack(side=LEFT, pady=10)
        
        # NOUVEAU: Affichage du chat actuel
        self.chat_status_label = ttk.Label(
           status_frame, text="💬 Chat: Nouveau Chat", 
           font=("Segoe UI", 9), foreground="#1976d2"
        )
        self.chat_status_label.pack(anchor="w")
        # Info version
        version_label = ttk.Label(
            footer, text="CarOS v2.0 Pro • IA & Recherche Web Intégrée",
            font=("Segoe UI", 9)
        )
        version_label.pack(side=RIGHT, pady=10)

    def update_chat_status(self):
        """Met à jour l'affichage du statut du chat"""
        chat_info = self.conversation_manager.get_current_chat_info()
        status_text = f"💬 Chat: {chat_info['title']} ({chat_info['message_count']} messages)"
    
        if hasattr(self, 'chat_status_label'):
           self.chat_status_label.config(text=status_text)
    
    # Mettre à jour le titre de la fenêtre
        self.update_window_title()
    def update_clock(self):
        """Met à jour l'horloge en temps réel"""
        try:
            current_time = datetime.now().strftime("%H:%M:%S")
            self.clock_label.config(text=current_time)
            
            self.window.after(1000, self.update_clock)
        except:
            pass
    def save_conversation(self):
        '''Sauvegarde la conversation actuelle'''
        if not self.conversation_manager.current_conversation:
            messagebox.showwarning("Attention", "Aucune conversation à sauvegarder !")
            return
        
        # Demander un titre personnalisé
        title = tk.simpledialog.askstring(
            "Sauvegarder", 
            "Nom de la conversation :",
            initialvalue=f"Conversation {datetime.now().strftime('%d/%m/%Y')}"
        )
        
        if title:
            if self.conversation_manager.save_current_conversation(title):
                messagebox.showinfo("Succès", f"Conversation '{title}' sauvegardée !")
            else:
                messagebox.showerror("Erreur", "Impossible de sauvegarder la conversation")
    
    def open_history(self):
        '''Ouvre la fenêtre d'historique'''
        HistoryWindow(self.window, self.conversation_manager, self)
    
    def clear_chat(self):
        """Efface la conversation avec option nouveau chat"""
        current_info = self.conversation_manager.get_current_chat_info()
        if current_info["has_messages"]:
           response = messagebox.askyesnocancel(
            "🗑️ Effacer la conversation",
            f"Chat: '{current_info['title']}'\n"
            f"Messages: {current_info['message_count']}\n\n"
            f"• Oui = Sauvegarder puis effacer\n"
            f"• Non = Effacer sans sauvegarder\n"
            f"• Annuler = Ne pas effacer"
        )
        if response is None:  # Annuler
            return
        elif response:  # Sauvegarder avant effacement
            if not self.save_conversation_with_custom_title():
                return
         # Effacer et créer un nouveau chat
        self.create_new_chat()
    
    def stop_ai_speech(self):
       """Arrête la synthèse vocale de l'IA"""
       if self.audio_manager.is_speaking:
        self.audio_manager.stop_speaking()
        self.add_message("🔇 Synthèse vocale interrompue", "system")

    def open_navigation(self):
        """Interface navigation rapide"""
        destination = simpledialog.askstring(
            "🧭 Navigation CarOS", 
            "Destination ?\n\n• maison, travail, centre, gare\n• aéroport, hôpital\n• Adresse complète",
            parent=self.window
        )
        
        if destination:
            command = f"aller à {destination}"
            result = self.car_system.execute_command(command)
            self.add_message(f"🧭 {result}", "system")
            
            if self.tts_enabled:
                clean_text = result.replace("✅", "").replace("❌", "").replace("🗺️", "")
                threading.Thread(target=lambda: self.audio_manager.speak(clean_text), daemon=True).start()
    
    def clear_chat(self):
        """Efface la conversation et la mémoire LangChain"""
    # Proposer de sauvegarder si la conversation n'est pas vide
        if self.conversation_manager.current_conversation:
            if messagebox.askyesno("Sauvegarder ?", 
                             "Voulez-vous sauvegarder cette conversation avant de l'effacer ?"):
              self.save_conversation()
    
              self.chat_box.delete(1.0, tk.END)
              self.conversation_manager.clear_current_conversation()
    
    # NOUVEAU: Effacer la mémoire LangChain
              if hasattr(self, 'langchain_manager'):
               self.langchain_manager.clear_memory()
    
               self.add_welcome_message()

    def add_welcome_message(self):
        """Message de bienvenue avec navigation GPS"""
        nav_ok = hasattr(self.car_system, 'navigation_system')
        llm_ok = hasattr(self, 'langchain_manager') and self.langchain_manager.is_available()
    
        welcome = f"""🎉 CarOS - Assistant Vocal Intelligent

🔗 LangChain: {"✅ Actif" if llm_ok else "⚠️ Limité"}
🧭 Navigation: {"✅ GPS Smart avec Routes" if nav_ok else "⚠️ Indisponible"}

  

COMMANDES DISPONIBLES:
🌡️ "Allume la climatisation" 
🪟 "Ouvre les vitres" • "Ferme toutes les vitres"  
🎵 "Lance la musique" • "Arrête la musique"
🗺️ "Navigation vers Paris"(comme exemple) • "Aller à la maison"
📞 "Appelle [NOM]" 
💬 "Message à [NOM]" • "Envoie un SMS à [NOM]"
🔍 "Recherche [SUJET]" • "Cherche actualités" • "Trouve [INFOS]"
🚗 "État de la voiture"
📍 "Ma position" • "Où suis-je ?" • "Coordonnées GPS"

Cliquez sur "Démarrer" pour une expérience vocale premium !
"""
        self.add_message(welcome, "welcome")
    
    def add_message(self, text, tag=""):
        '''Ajoute un message dans la conversation'''
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_box.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.chat_box.insert(tk.END, f"{text}\n\n", tag)
        self.chat_box.see(tk.END)
        self.window.update()
        
        # Ajouter à l'historique
        self.conversation_manager.add_message(text, tag)
        self.update_chat_status()
    
    def toggle_recording(self):
        """Démarre/arrête l'enregistrement"""
        if not self.audio_manager.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Démarre l'enregistrement"""
        self.record_btn.config(text="⏹️ Stop", bootstyle="danger")
        self.status_label.config(text="🔴 Écoute...", foreground="#9128c6")  # Rouge foncé
        self.audio_manager.start_recording()
    
    def stop_recording(self):
        """Arrête l'enregistrement et traite"""
        self.record_btn.config(text="⏳ Traitement...", state="disabled")
        self.status_label.config(text="⏳ Analyse...", foreground="#5000ef")  # Orange foncé
        
        # Traitement en arrière-plan
        threading.Thread(target=self.process_audio, daemon=True).start()
    
    def process_audio(self):
        """Traite l'audio enregistré"""
        try:
            # Arrêt de l'enregistrement
            audio_file = self.audio_manager.stop_recording()
            if not audio_file:
                raise Exception("Aucun audio enregistré")
            
            # Transcription
            transcription = self.audio_manager.transcribe(audio_file)
            if not transcription:
                raise Exception("Aucune parole détectée")
            
            # Affichage de la commande utilisateur
            self.add_message(f"👤 Vous: {transcription}", "user")
            
            # Traitement de la commande
            car_response = self.car_system.execute_command(transcription)
            
            if car_response:
                # Vérifier si c'est un tuple (message, qr_image)
                if isinstance(car_response, tuple) and len(car_response) == 2:
                    message, qr_image = car_response
                    self.add_message(f"🚗 Système: {message}", "system")
                    
                    # Afficher le QR code
                    if qr_image:
                        action = "Appel" if "appeler" in message else "SMS" if "SMS" in message else "Vérification"
                        self.show_qr_code(qr_image, f"{action} - QR Code")
                    
                    response_text = message
                else:
                    # Réponse simple sans QR
                    self.add_message(f"🚗 Système: {car_response}", "system")
                    response_text = car_response
            else:
                # Requête conversationnelle via LM Studio
                response_text = self.get_ai_response_with_langchain(transcription)
                self.add_message(f"🤖 Assistant: {response_text}", "assistant")
            
            # Synthèse vocale
            if self.tts_enabled:
                threading.Thread(target=lambda: self.audio_manager.speak(
                    response_text.replace("✅", "").replace("❌", "").replace("🚗", "")
                ), daemon=True).start()
        
        except Exception as e:
            error_msg = f"❌ Erreur: {str(e)}"
            self.add_message(error_msg, "system")
            if self.tts_enabled:
                self.audio_manager.speak("Erreur technique")
        
        finally:
            # Réinitialisation des contrôles
            self.record_btn.config(text="🎙️ Démarrer", bootstyle="primary", state="normal")
            self.status_label.config(text="✅ Système Opérationnel", foreground="#2a0ff5")  # Vert foncé
    
    def get_ai_response(self, text):
        """Obtient une réponse de l'IA"""
        try:
            payload = {
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": "Tu es un assistant vocal de voiture. Réponds en français, de manière concise (max 15 mots)."},
                    {"role": "user", "content": text}
                ],
                "temperature": 0.3,
                "max_tokens": 50
            }
            
            response = requests.post(LM_URL, headers=HEADERS, json=payload, timeout=10)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return "Service IA temporairement indisponible."
        except:
            return "Problème de connexion au service IA."
    
    def toggle_tts(self):
        """Active/désactive la synthèse vocale"""
        self.tts_enabled = not self.tts_enabled
        style = "success-outline" if self.tts_enabled else "secondary-outline"
        text = "🔊" if self.tts_enabled else "🔇"
        self.audio_btn.config(text=text, bootstyle=style)
    
    def show_status(self):
        """Affiche l'état du véhicule"""
        status = self.car_system.get_status()
        self.add_message(status, "system")
    
    def clear_chat(self):
        """Efface la conversation"""
        self.chat_box.delete(1.0, tk.END)
        self.add_welcome_message()
    
    # ========== MÉTHODES MANQUANTES À AJOUTER ==========
    
    def open_navigation_safe(self):
        """Version sécurisée de l'ouverture de navigation"""
        try:
            if hasattr(self.car_system, 'navigation_system'):
                self.open_navigation()
            else:
                self.add_message("❌ Navigation non disponible", "system")
        except Exception as e:
            self.add_message(f"❌ Erreur navigation: {e}", "system")
    
    def quick_action(self, command):
        """Exécute une action rapide depuis les boutons"""
        try:
            # Traiter la commande
            result = self.car_system.execute_command(command)
            
            if result:
                # Vérifier si c'est un tuple (message, qr_image)
                if isinstance(result, tuple) and len(result) == 2:
                    message, qr_image = result
                    self.add_message(f"⚡ Action: {message}", "system")
                    
                    # Afficher le QR code si présent
                    if qr_image:
                        action = "Appel" if "appeler" in message else "SMS" if "SMS" in message else "Action"
                        self.show_qr_code(qr_image, f"{action} - QR Code")
                    
                    response_text = message
                else:
                    # Réponse simple
                    self.add_message(f"⚡ Action: {result}", "system")
                    response_text = result
                
                # Synthèse vocale
                if self.tts_enabled:
                    clean_text = response_text.replace("✅", "").replace("❌", "").replace("🚗", "")
                    threading.Thread(target=lambda: self.audio_manager.speak(clean_text), daemon=True).start()
            else:
                self.add_message("❌ Action non reconnue", "system")
                
        except Exception as e:
            error_msg = f"❌ Erreur action rapide: {str(e)}"
            self.add_message(error_msg, "system")
    
    def open_navigation(self):
        """Interface navigation rapide - Version corrigée"""
        try:
            destination = simpledialog.askstring(
                "🧭 Navigation CarOS", 
                "Destination ?\n\n• maison, travail, centre, gare\n• aéroport, hôpital\n• Adresse complète",
                parent=self.window
            )
            
            if destination:
                command = f"aller à {destination}"
                result = self.car_system.execute_command(command)
                
                if result:
                    self.add_message(f"🧭 {result}", "system")
                    
                    if self.tts_enabled:
                        clean_text = result.replace("✅", "").replace("❌", "").replace("🗺️", "")
                        threading.Thread(target=lambda: self.audio_manager.speak(clean_text), daemon=True).start()
                else:
                    self.add_message("❌ Navigation impossible", "system")
                    
        except Exception as e:
            self.add_message(f"❌ Erreur navigation: {e}", "system")
    def run(self):
        """Lance l'application"""
        try:
            self.window.mainloop()
        except KeyboardInterrupt:
            self.window.quit()

# ========== NOUVELLE CLASSE POUR LA GESTION DES CONVERSATIONS ==========
class ConversationManager:
    def __init__(self, history_dir="conversations_history"):
        self.history_dir = history_dir
        self.current_conversation = []
        self.conversations_list = []
        
        self.chat_counter = 0  # NOUVEAU: Compteur de chats
        self.current_chat_title = "Nouveau Chat"  # NOUVEAU: Titre du chat actuel
        # Créer le dossier d'historique s'il n'existe pas
        if not os.path.exists(self.history_dir):
            os.makedirs(self.history_dir)
        
        # Charger l'historique existant
        self.load_conversations_list()
    
    def create_new_chat(self, auto_save_current=True):
        """Crée un nouveau chat et optionnellement sauvegarde l'actuel"""
        # Sauvegarder automatiquement le chat actuel s'il n'est pas vide
        if auto_save_current and self.current_conversation:
            timestamp = datetime.now().strftime("%d/%m/%Y à %H:%M")
            auto_title = f"Chat automatique - {timestamp}"
            self.save_current_conversation(auto_title)
        
        # Réinitialiser pour nouveau chat
        self.current_conversation = []
        self.chat_counter += 1
        self.current_chat_title = f"Nouveau Chat {self.chat_counter}"
        
        return self.current_chat_title
    def set_current_chat_title(self, title):
        """Définit le titre du chat actuel"""
        self.current_chat_title = title if title.strip() else f"Chat {self.chat_counter}"

    def get_current_chat_info(self):
        """Retourne les infos du chat actuel"""
        return {
            "title": self.current_chat_title,
            "message_count": len(self.current_conversation),
            "has_messages": len(self.current_conversation) > 0
        }
    def add_message(self, message, tag=""):
        """Ajoute un message à la conversation courante"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.current_conversation.append({
            "timestamp": timestamp,
            "message": message,
            "tag": tag
        })
    
    def save_current_conversation(self, title=None):
        """Sauvegarde la conversation courante"""
        if not self.current_conversation:
            return False
        
        # Générer un titre automatique si non fourni
        if not title:
            title = f"Conversation {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
        
        conversation_data = {
            "title": title,
            "date": datetime.now().isoformat(),
            "messages": self.current_conversation.copy()
        }
        
        # Nom de fichier sécurisé
        safe_filename = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_filename}.pkl"
        filepath = os.path.join(self.history_dir, filename)
        
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(conversation_data, f)
            
            # Ajouter à la liste des conversations
            self.conversations_list.append({
                "title": title,
                "date": conversation_data["date"],
                "filepath": filepath,
                "message_count": len(self.current_conversation)
            })
            
            # Sauvegarder la liste mise à jour
            self.save_conversations_list()
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def load_conversation(self, filepath):
        """Charge une conversation depuis un fichier"""
        try:
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement: {e}")
            return None
    
    def delete_conversation(self, filepath):
        """Supprime une conversation"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
            
            # Retirer de la liste
            self.conversations_list = [conv for conv in self.conversations_list 
                                     if conv["filepath"] != filepath]
            self.save_conversations_list()
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression: {e}")
            return False
    
    def clear_current_conversation(self):
        """Vide la conversation courante"""
        self.current_conversation = []
    
    def get_conversations_list(self):
        """Retourne la liste des conversations sauvegardées"""
        # Trier par date (plus récent en premier)
        return sorted(self.conversations_list, 
                     key=lambda x: x["date"], reverse=True)
    
    def save_conversations_list(self):
        """Sauvegarde la liste des conversations"""
        list_file = os.path.join(self.history_dir, "conversations_list.pkl")
        try:
            with open(list_file, 'wb') as f:
                pickle.dump(self.conversations_list, f)
        except Exception as e:
            print(f"Erreur sauvegarde liste: {e}")
    
    def load_conversations_list(self):
        """Charge la liste des conversations"""
        list_file = os.path.join(self.history_dir, "conversations_list.pkl")
        try:
            if os.path.exists(list_file):
                with open(list_file, 'rb') as f:
                    self.conversations_list = pickle.load(f)
            else:
                self.conversations_list = []
        except Exception as e:
            print(f"Erreur chargement liste: {e}")
            self.conversations_list = []

# ========== CLASSE POUR L'INTERFACE D'HISTORIQUE ==========
class HistoryWindow:
    def __init__(self, parent, conversation_manager, main_app):
        self.parent = parent
        self.conversation_manager = conversation_manager
        self.main_app = main_app
        
        # Créer la fenêtre d'historique
        self.window = ttk.Toplevel(parent)
        self.window.title("📚 Historique des Conversations")
        self.window.geometry("900x600")
        self.window.resizable(True, True)
        
        self.setup_ui()
        self.refresh_list()
    
    def setup_ui(self):
        """Configure l'interface de l'historique"""
        # En-tête
        header = ttk.Frame(self.window)
        header.pack(fill=X, padx=20, pady=20)
        
        ttk.Label(header, text="📚 Historique des Conversations", 
                 font=("Segoe UI", 18, "bold")).pack(side=LEFT)
        
        # Boutons d'action
        btn_frame = ttk.Frame(header)
        btn_frame.pack(side=RIGHT)
        
        ttk.Button(btn_frame, text="🔄 Actualiser", 
                  command=self.refresh_list, bootstyle="info-outline").pack(side=LEFT, padx=5)
        
        ttk.Button(btn_frame, text="🗑️ Tout Supprimer", 
                  command=self.delete_all_conversations, 
                  bootstyle="danger-outline").pack(side=LEFT, padx=5)
        
        # Zone de liste
        list_frame = ttk.LabelFrame(self.window, text="Conversations Sauvegardées", padding=15)
        list_frame.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Treeview pour afficher les conversations
        columns = ("Titre", "Date", "Messages", "Actions")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Configuration des colonnes
        self.tree.heading("Titre", text="📝 Titre")
        self.tree.heading("Date", text="📅 Date & Heure")
        self.tree.heading("Messages", text="💬 Messages")
        self.tree.heading("Actions", text="⚡ Actions")
        
        self.tree.column("Titre", width=300)
        self.tree.column("Date", width=180)
        self.tree.column("Messages", width=100, anchor="center")
        self.tree.column("Actions", width=150, anchor="center")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Bind double-click pour charger une conversation
        self.tree.bind("<Double-1>", self.load_selected_conversation)
        self.tree.bind("<Button-3>", self.show_context_menu)  # Clic droit
        
        # Menu contextuel
        self.context_menu = tk.Menu(self.window, tearoff=0)
        self.context_menu.add_command(label="📖 Ouvrir", command=self.load_selected_conversation)
        self.context_menu.add_command(label="🗑️ Supprimer", command=self.delete_selected_conversation)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📋 Copier le titre", command=self.copy_title)
    
    def refresh_list(self):
        """Actualise la liste des conversations"""
        # Vider la liste actuelle
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Recharger les conversations
        conversations = self.conversation_manager.get_conversations_list()
        
        for conv in conversations:
            date_obj = datetime.fromisoformat(conv["date"])
            date_str = date_obj.strftime("%d/%m/%Y %H:%M")
            
            self.tree.insert("", "end", values=(
                conv["title"],
                date_str,
                conv["message_count"],
                "Cliquer pour ouvrir"
            ), tags=(conv["filepath"],))
    
    def load_selected_conversation(self, event=None):
        """Charge la conversation sélectionnée"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        filepath = item["tags"][0]
        
        # Charger la conversation
        conversation_data = self.conversation_manager.load_conversation(filepath)
        if conversation_data:
            # Effacer le chat actuel
            self.main_app.clear_chat()
            
            # Charger les messages
            for msg_data in conversation_data["messages"]:
                self.main_app.chat_box.insert(tk.END, f"[{msg_data['timestamp']}] ", "timestamp")
                self.main_app.chat_box.insert(tk.END, f"{msg_data['message']}\n\n", msg_data['tag'])
            
            self.main_app.chat_box.see(tk.END)
            
            # Message de confirmation
            messagebox.showinfo("Succès", f"Conversation '{conversation_data['title']}' chargée !")
            self.window.destroy()
    
    def delete_selected_conversation(self, event=None):
        """Supprime la conversation sélectionnée"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        title = item["values"][0]
        filepath = item["tags"][0]
        
        # Confirmation
        if messagebox.askyesno("Confirmation", f"Supprimer la conversation '{title}' ?"):
            if self.conversation_manager.delete_conversation(filepath):
                messagebox.showinfo("Succès", "Conversation supprimée !")
                self.refresh_list()
            else:
                messagebox.showerror("Erreur", "Impossible de supprimer la conversation")
    
    def delete_all_conversations(self):
        """Supprime toutes les conversations"""
        if not messagebox.askyesno("Confirmation", 
                                  "⚠️ Supprimer TOUTES les conversations ?\nCette action est irréversible !"):
            return
        
        conversations = self.conversation_manager.get_conversations_list()
        deleted_count = 0
        
        for conv in conversations:
            if self.conversation_manager.delete_conversation(conv["filepath"]):
                deleted_count += 1
        
        messagebox.showinfo("Terminé", f"{deleted_count} conversation(s) supprimée(s)")
        self.refresh_list()
    
    def show_context_menu(self, event):
        """Affiche le menu contextuel"""
        selection = self.tree.selection()
        if selection:
            self.context_menu.post(event.x_root, event.y_root)
    
    def copy_title(self):
        """Copie le titre de la conversation sélectionnée"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            title = item["values"][0]
            self.window.clipboard_clear()
            self.window.clipboard_append(title)


# ========== LANCEMENT ==========
if __name__ == "__main__":
    print("🚘 Démarrage de l'Assistant Vocal Automobile...")
    
    try:
        app = VoiceAssistantGUI()
        app.run()
    except Exception as e:
        print(f"❌ Erreur de démarrage: {e}")
        input("Appuyez sur Entrée pour quitter...")