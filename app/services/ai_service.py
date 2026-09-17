import requests
import urllib3
from flask import current_app

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def ai_yanit_uret(kullanici_mesaji, sohbet_gecmisi=None):
    """
    Groq API kullanarak kullanıcı mesajına yanıt üretir.
    GÜVENLİK & MİMARİ: Tüm AI çağrıları ve sistem talimatı (BUSINESS_CONTEXT)
    yalnızca bu katmanda işlenir.
    """
    api_key = current_app.config.get('GROQ_API_KEY')
    business_context = current_app.config.get('BUSINESS_CONTEXT', '')

    if not api_key:
        return "Hata: Groq API anahtarı (.env) tanımlanmamış."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    messages = [
        {"role": "system", "content": business_context}
    ]

    if sohbet_gecmisi:
        for msg in sohbet_gecmisi:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

    messages.append({"role": "user", "content": kullanici_mesaji})

    payload = {
        "model": "qwen/qwen3.8-27b",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 800
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15, verify=False)
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return f"AI Servis Hatası ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Bağlantı Hatası: {str(e)}"