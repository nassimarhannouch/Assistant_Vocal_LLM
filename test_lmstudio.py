import requests

API_URL = "http://localhost:1234/v1/chat/completions"

headers = {"Content-Type": "application/json"}
data = {
    "model": "your-model-name",  # Mets le nom du modèle chargé dans LM Studio
    "messages": [{"role": "user", "content": "Bonjour, qui es-tu ?"}]
}

response = requests.post(API_URL, headers=headers, json=data)
print(response.json())
