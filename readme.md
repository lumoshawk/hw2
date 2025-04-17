# Homework #2 of Deep Learning



## Installation

1. Create and activate a virtual environment:

 ```bash
python -m venv venv

venv\Scripts\activate  # On Windows

source venv/bin/activate  # On Unix/MacOS
 ```



2. Install the required dependencies:

 ```bash
pip install -r constraints.txt
 ```



3. run GUI

```powershell
py ./toolset_gui.py
```



## Functions

1. a chatbot 

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
    api_endpoint = ""  # Replace with your API endpoint
    api_key = ""  # Replace with your API key
    model_name = "gpt-4o"  # Replace with your desired model name

    chatbot = ChatBot(api_endpoint, api_key, model_name)

    # Use the chat_with_bot API
    user_message = str(input('you: '))
    response = chatbot.chat_with_bot(user_message)
    ```





2. a scientist paper search bot

- usage:

    - from the GUI

    - run `py ./sci_search/app.py` and open http://127.0.0.1:5001

    - CLI call:

    ```python
    python sci_search/main.py "Ya-qin Zhang"
    ```

    
