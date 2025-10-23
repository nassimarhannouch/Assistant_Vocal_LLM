import requests
import json

# Configuration Mistral via Ollama
MISTRAL_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral:7b"  # ou "mistral:latest"

def test_mistral(prompt):
    """Test simple de Mistral via Ollama"""
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 100
        }
    }
    
    try:
        print(f"🤖 Envoi à Mistral: {prompt}")
        response = requests.post(MISTRAL_URL, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get("response", "Pas de réponse")
            print(f"✅ Réponse Mistral: {answer}")
            return answer
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def test_mistral_chat():
    """Test avec API chat (alternative)"""
    chat_url = "http://localhost:11434/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "Tu es un assistant IA utile. Réponds en français."},
            {"role": "user", "content": "Bonjour, peux-tu te présenter ?"}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    try:
        response = requests.post(chat_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            print(f"✅ Chat Mistral: {answer}")
            return answer
        else:
            print(f"❌ Erreur Chat: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur Chat: {e}")
        return None

# Tests
if __name__ == "__main__":
    print("🧪 Test de Mistral via Ollama")
    print("=" * 50)
    
    # Test 1: API generate
    print("\n📝 Test 1: API Generate")
    test_mistral("Bonjour ! Peux-tu te présenter brièvement ?")
    
    # Test 2: API chat
    print("\n💬 Test 2: API Chat")
    test_mistral_chat()
    
    # Test 3: Question technique
    print("\n🔧 Test 3: Question technique")
    test_mistral("Explique-moi en 2 phrases ce qu'est l'intelligence artificielle.")
    
    print("\n✅ Tests terminés !")