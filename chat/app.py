from flask import Flask, render_template, request, jsonify, session
import os
from chatbot import ChatBot
from flask import Blueprint

# Update macros for API endpoint, API key, and model name
API_ENDPOINT = os.environ.get("OPENAI_API_ENDPOINT", "https://www.jcapikey.com/v1/chat/completions")
API_KEY = os.environ.get("OPENAI_API_KEY", "sk-zhvgVgajM5AqJPmX63C02f93C37c44BeBc61457d49B638E6")
DEFAULT_MODEL_NAME = "gpt-4o-mini"

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    # Initialize session variables if they don't exist
    if 'api_endpoint' not in session:
        session['api_endpoint'] = API_ENDPOINT
    if 'model_name' not in session:
        session['model_name'] = DEFAULT_MODEL_NAME
    
    return render_template('index.html', 
                           api_endpoint=session['api_endpoint'],
                           model_name=session['model_name'])

@app.route('/setup', methods=['POST'])
def setup():
    # Save API settings in session
    session['api_endpoint'] = request.form.get('apiEndpoint', API_ENDPOINT)
    session['api_key'] = request.form.get('apiKey', API_KEY)
    session['model_name'] = request.form.get('modelName', DEFAULT_MODEL_NAME)
    
    print(f"Model name set to: {session['model_name']}")  # Debug print
    
    # Reset conversation history
    if 'conversation' in session:
        session.pop('conversation')
    
    return jsonify({'success': True})

@app.route('/chat', methods=['POST'])
def chat():
    # Get message from request
    user_message = request.form.get('message', '')
    
    # Get API settings from session
    api_endpoint = session.get('api_endpoint', API_ENDPOINT)
    api_key = session.get('api_key', API_KEY)
    model_name = session.get('model_name', DEFAULT_MODEL_NAME)
    
    # Initialize or get conversation history
    if 'conversation' not in session:
        session['conversation'] = []
    
    conversation = session['conversation']
    
    # Add user message to conversation
    conversation.append({'role': 'user', 'content': user_message})
    
    try:
        # Initialize chatbot with custom endpoint and send message
        chatbot = ChatBot(api_endpoint, api_key, model_name)
        
        # Set conversation history in chatbot
        chatbot.conversation_history = conversation
        
        # Send message and get response
        response = chatbot.send_message(user_message)
        
        # Update conversation in session
        session['conversation'] = chatbot.conversation_history
        
        return jsonify({
            'success': True,
            'response': response
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/reset', methods=['POST'])
def reset():
    # Reset conversation in session
    if 'conversation' in session:
        session.pop('conversation')
    
    return jsonify({'success': True})

# Create a blueprint for API access
api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/api/send_message', methods=['POST'])
def api_send_message():
    user_message = request.json.get('message', '')
    api_endpoint = session.get('api_endpoint', API_ENDPOINT)
    api_key = session.get('api_key', API_KEY)
    model_name = session.get('model_name', DEFAULT_MODEL_NAME)

    if 'conversation' not in session:
        session['conversation'] = []

    conversation = session['conversation']
    conversation.append({'role': 'user', 'content': user_message})

    try:
        chatbot = ChatBot(api_endpoint, api_key, model_name)
        chatbot.conversation_history = conversation
        response = chatbot.send_message(user_message)
        session['conversation'] = chatbot.conversation_history
        return jsonify({'success': True, 'response': response})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@api_blueprint.route('/api/reset', methods=['POST'])
def api_reset():
    if 'conversation' in session:
        session.pop('conversation')
    return jsonify({'success': True})

# Register the blueprint
app.register_blueprint(api_blueprint)

if __name__ == '__main__':
    app.run(debug=True)