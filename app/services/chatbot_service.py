import os
import requests

def get_chatbot_response(user_message, conversation_history):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "Chatbot is temporarily unavailable (Missing API Key)."

    system_prompt = {
        "role": "system",
        "content": "You are Philron Assistant, a helpful AI assistant for TINDI CMMS, a professional maintenance and facilities management platform. You help users understand our services, how to submit work orders, check on equipment status, and learn about our technician team. Be concise, professional, and friendly. Operating hours: Monday–Friday 8am–6pm."
    }

    messages = [system_prompt] + conversation_history
    messages.append({"role": "user", "content": user_message})

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Groq API Error: {e}")
        return "I'm having trouble connecting to my brain right now. Please try again later."
