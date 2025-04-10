# Homework #2 of Deep Learning

1. added a chatbot 

- usage:
    - from the GUI

    - run `py ./chat/app.py` and open http://127.0.0.1:5000

    - CLI call:

    ```python
    py ./chat/chatbot.py
    ```

    - use with function call:

    ```python
    from chatbot import ChatBot
    # Initialize the chatbot
    api_endpoint = "https://www.jcapikey.com/v1/chat/completions"  # Replace with your API endpoint
    api_key = "sk-zhvgVgajM5AqJPmX63C02f93C37c44BeBc61457d49B638E6"  # Replace with your API key
    model_name = "gpt-4o"  # Replace with your desired model name

    chatbot = ChatBot(api_endpoint, api_key, model_name)

    # Use the chat_with_bot API
    user_message = str(input('you: '))
    response = chatbot.chat_with_bot(user_message)
    ```





2. added a scientist paper search bot

- usage:

    - from the GUI

    - run `py ./sci_search/app.py` and open http://127.0.0.1:5001

    - CLI call:

    ```python
    python sci_search/main.py "Ya-qin Zhang"
    ```

    
