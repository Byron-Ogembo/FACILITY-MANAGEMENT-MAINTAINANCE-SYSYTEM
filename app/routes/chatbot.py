from flask import Blueprint, request, jsonify
from app.services.chatbot_service import get_chatbot_response

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/message', methods=['POST'])
def message():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400
        
    user_message = data['message']
    history = data.get('history', [])
    
    reply = get_chatbot_response(user_message, history)
    
    return jsonify({"reply": reply})
