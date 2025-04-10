
# Chatbot Application

This is a simple web-based chatbot application that allows to connect to ChatGPT's API with your own custom endpoint.

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

## Usage

1. Start the Flask application:

   ```bash
   python app.py
   ```

2. Open a web browser and go to `http://127.0.0.1:5000/`

## Files

- `app.py`: Flask web application
- `chatbot.py`: ChatBot class implementation
- `templates/index.html`: HTML template for web interface with Markdown rendering
- `constraints.txt`: List of Python package dependencies

## Command-line Usage

You can also use the chatbot directly from the command line:

```bash
python chatbot.py
```

This will prompt you to enter the API endpoint, API key, and model name, and then you can start chatting in the terminal.
