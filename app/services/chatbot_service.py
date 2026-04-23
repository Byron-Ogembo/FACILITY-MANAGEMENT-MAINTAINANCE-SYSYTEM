import os
import json
import urllib.request
import urllib.error


def get_chatbot_response(user_message, conversation_history):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "Chatbot is temporarily unavailable (Missing API Key)."

    system_prompt = {
        "role": "system",
        "content": (
            "You are Philron Assistant, a helpful AI assistant for TINDI CMMS, "
            "a professional maintenance and facilities management platform for the "
            "Coca-Cola plant. You help users understand our services, how to submit "
            "work orders, check on equipment status, and learn about our technician team. "
            "Be concise, professional, and friendly. "
            "Operating hours: Monday–Friday 8am–6pm."
        )
    }

    messages = [system_prompt] + list(conversation_history)
    messages.append({"role": "user", "content": user_message})

    payload = json.dumps({
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "temperature": 0.7
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"Groq API HTTP Error {e.code}: {body}")
        return "I'm having trouble connecting to my brain right now. Please try again later."
    except Exception as e:
        print(f"Groq API Error: {e}")
        return "I'm having trouble connecting to my brain right now. Please try again later."
