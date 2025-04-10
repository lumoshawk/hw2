import tkinter as tk
from tkinter import ttk
import webbrowser
import subprocess
import os
import sys
import threading
from PIL import Image, ImageTk
import io
import base64

class ToolsetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("A little Toolset")
        self.root.geometry("900x600")
        self.root.configure(bg="#f8f9fa")
        
        # Google-like styling
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#f8f9fa')
        self.style.configure('TButton', 
                            font=('Segoe UI', 10),
                            background='#1a73e8',
                            foreground='white',
                            borderwidth=0,
                            focusthickness=3,
                            focuscolor='#1a73e8')
        self.style.map('TButton', 
                      background=[('active', '#185abc'), ('pressed', '#174ea6')])
        
        # Main container
        self.main_container = ttk.Frame(root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        self.header = ttk.Frame(self.main_container)
        self.header.pack(fill=tk.X, pady=(0, 20))
        
        self.title_label = tk.Label(self.header, 
                                   text="A little Toolset", 
                                   font=('Segoe UI', 24, 'bold'),
                                   bg="#f8f9fa",
                                   fg="#202124")
        self.title_label.pack(side=tk.LEFT)
        
        # Tools container with grid layout
        self.tools_container = ttk.Frame(self.main_container)
        self.tools_container.pack(fill=tk.BOTH, expand=True)
        
        # Define tool cards
        self.create_tool_card(0, 0, "Chat Application", 
                             "Open the web-based chat interface", 
                             self.open_chat_app)
        
        self.create_tool_card(0, 1, "SciSearch Tool", 
                             "Search for computer scientists and their publications on DBLP", 
                             self.open_sci_search)
        
        self.create_tool_card(1, 0, "Future Tool 2", 
                             "Coming soon: Description of future tool 2", 
                             lambda: self.show_message("Future Tool 2 coming soon!"))
        
        self.create_tool_card(1, 1, "Future Tool 3", 
                             "Coming soon: Description of future tool 3", 
                             lambda: self.show_message("Future Tool 3 coming soon!"))
        
        # Status bar
        self.status_bar = tk.Label(root, 
                                  text="Ready", 
                                  bd=1, 
                                  relief=tk.SUNKEN, 
                                  anchor=tk.W,
                                  bg="#f8f9fa",
                                  fg="#5f6368")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_tool_card(self, row, col, title, description, command):
        card = ttk.Frame(self.tools_container, style='Card.TFrame')
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Configure card style
        self.style.configure('Card.TFrame', 
                            background='white',
                            relief='raised',
                            borderwidth=1)
        
        # Card content
        title_label = tk.Label(card, 
                              text=title, 
                              font=('Segoe UI', 14, 'bold'),
                              bg="white",
                              fg="#202124")
        title_label.pack(padx=15, pady=(15, 5), anchor='w')
        
        desc_label = tk.Label(card, 
                             text=description, 
                             font=('Segoe UI', 10),
                             wraplength=300,
                             bg="white",
                             fg="#5f6368")
        desc_label.pack(padx=15, pady=(0, 15), anchor='w', fill='x')
        
        button = ttk.Button(card, text="Open", command=command)
        button.pack(padx=15, pady=(0, 15), anchor='e')
        
        # Make grid cells expandable
        self.tools_container.grid_columnconfigure(0, weight=1)
        self.tools_container.grid_columnconfigure(1, weight=1)
        self.tools_container.grid_rowconfigure(0, weight=1)
        self.tools_container.grid_rowconfigure(1, weight=1)
    
    def open_chat_app(self):
        self.status_bar.config(text="Starting chat application...")
        
        # Determine the path to the chat application
        current_dir = os.path.dirname(os.path.abspath(__file__))
        chat_dir = os.path.join(current_dir, 'chat')
        app_path = os.path.join(chat_dir, 'app.py')
        
        # Run Flask app in a separate thread
        threading.Thread(target=self.run_flask_app, args=(app_path, 5000, 'Chat')).start()
        
        # Give Flask a moment to start
        self.root.after(1500, lambda: self.open_browser(5000, "chat"))
    
    def open_sci_search(self):
        self.status_bar.config(text="Starting SciSearch application...")
        
        # Determine the path to the sci_search application
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sci_search_dir = os.path.join(current_dir, 'sci_search')
        app_path = os.path.join(sci_search_dir, 'app.py')
        
        # Run Flask app in a separate thread
        threading.Thread(target=self.run_flask_app, args=(app_path, 5001, 'SciSearch')).start()
        
        # Give Flask a moment to start
        self.root.after(1500, lambda: self.open_browser(5001, "SciSearch"))
    
    def run_flask_app(self, app_path, port=5000, app_name="App"):
        try:
            subprocess.Popen([sys.executable, app_path])
            self.status_bar.config(text=f"{app_name} is starting...")
        except Exception as e:
            self.status_bar.config(text=f"Error starting {app_name}: {str(e)}")
    
    def open_browser(self, port=5000, app_type="app"):
        try:
            url = f'http://127.0.0.1:{port}'
            webbrowser.open(url)
            self.status_bar.config(text=f"{app_type.capitalize()} opened in browser at {url}")
        except Exception as e:
            self.status_bar.config(text=f"Error opening browser: {str(e)}")
    
    def show_message(self, message):
        self.status_bar.config(text=message)

if __name__ == "__main__":
    root = tk.Tk()
    app = ToolsetApp(root)
    root.mainloop()