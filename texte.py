import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1)

texte = input("Entrez le texte à prononcer : ")
engine.say(texte)
engine.runAndWait()

