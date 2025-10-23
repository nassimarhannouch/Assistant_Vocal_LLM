import webbrowser

def appeler_contact(nom):
    url = f"shortcuts://run-shortcut?name=AppelerContact&input={nom}"
    webbrowser.open(url)

# Exemple : lancer appel à Yasmine
appeler_contact("Yasmine")
