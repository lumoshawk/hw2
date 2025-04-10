import requests
import json
import os
from typing import Dict, List, Optional

# Update macros for API endpoint, API key, and model name
API_ENDPOINT = os.environ.get("OPENAI_API_ENDPOINT", "https://www.jcapikey.com/v1/chat/completions")
API_KEY = os.environ.get("OPENAI_API_KEY", "sk-zhvgVgajM5AqJPmX63C02f93C37c44BeBc61457d49B638E6")
DEFAULT_MODEL_NAME = "gpt-4o-mini"

class ChatBot:
    def __init__(self, api_endpoint: str = API_ENDPOINT, api_key: str = API_KEY, model_name: str = DEFAULT_MODEL_NAME):
        """
        Initialize the chatbot with API endpoint and credentials.
        
        Args:
            api_endpoint: The API endpoint URL (can be OpenAI's or a custom endpoint)
            api_key: The API key for authentication
            model_name: The model to use (default: gpt-4o-mini)
        """
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.model_name = model_name
        self.conversation_history: List[Dict[str, str]] = []
        print(f"ChatBot initialized with model: {self.model_name}")  # Debug print
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        self.conversation_history.append({"role": role, "content": content})
    
    def reset_conversation(self) -> None:
        """Reset the conversation history."""
        self.conversation_history = []
    
    def send_message(self, message: str) -> str:
        """
        Send a message to the API and get a response.
        
        Args:
            message: The user message text
            
        Returns:
            The assistant's response text
        """
        # Add user message to history
        self.add_message("user", message)
        
        # Prepare headers and payload
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Ensure we're using the model name that was passed to the constructor
        payload = {
            "model": self.model_name,
            "messages": self.conversation_history,
            "temperature": 0.7
        }
        
        print(f"Using model: {self.model_name}")  # Debug print
        
        try:
            # Make the API request
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                data=json.dumps(payload)
            )
            response.raise_for_status()
            
            # Parse the response
            response_data = response.json()
            assistant_message = response_data["choices"][0]["message"]["content"]
            
            # Add assistant response to history
            self.add_message("assistant", assistant_message)
            
            return assistant_message
            
        except requests.exceptions.RequestException as e:
            return f"Error communicating with API: {str(e)}"
        except (KeyError, IndexError) as e:
            return f"Error parsing API response: {str(e)}"
    
    def chat_with_bot(self, message: str) -> str:
        """
        A wrapper function to send a message to the chatbot and get a response.

        Args:
            message: The user message text

        Returns:
            The assistant's response text
        """
        return self.send_message(message)


def main():
    """Main function to run the chatbot."""
    # Initialize the chatbot
    chatbot = ChatBot()
    
    print("\n=== Simple ChatGPT Chatbot ===")
    print("Type 'exit' to quit, 'reset' to start a new conversation")
    
    # Main conversation loop
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        elif user_input.lower() == "reset":
            chatbot.reset_conversation()
            print("Conversation has been reset.")
            continue
        
        # Get response from the chatbot
        response = chatbot.send_message(user_input)
        print(f"\nAssistant: {response}")


if __name__ == "__main__":
    main()