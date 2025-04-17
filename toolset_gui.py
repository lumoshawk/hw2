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
import platform  # Import platform module for OS detection
import signal
import psutil  # Need to add this dependency for cross-platform process management
import atexit  # For registering cleanup on exit

class ToolsetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("A little Toolset")
        self.root.geometry("900x600")
        self.root.configure(bg="#f8f9fa")
        
        # Detect operating system
        self.os_name = platform.system()  # 'Windows', 'Linux', 'Darwin' (macOS)
        
        # Track all processes started by this application
        self.processes = []
        
        # Register cleanup handlers
        atexit.register(self.cleanup_processes)
        
        # Override window close event to ensure cleanup
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Select appropriate font based on platform
        if self.os_name == 'Windows':
            self.default_font = 'Segoe UI'
        elif self.os_name == 'Darwin':  # macOS
            self.default_font = 'Helvetica Neue'
        else:  # Linux and others
            self.default_font = 'DejaVu Sans'
        
        # Google-like styling with platform-specific adjustments
        self.style = ttk.Style()
        
        # Use a theme that works well on all platforms
        try:
            self.style.theme_use('clam')
        except tk.TclError:
            # Fallback to a default theme if 'clam' is unavailable
            self.style.theme_use('default')
            
        self.style.configure('TFrame', background='#f8f9fa')
        self.style.configure('TButton', 
                            font=(self.default_font, 10),
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
                                   font=(self.default_font, 24, 'bold'),
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
        
        self.create_tool_card(1, 0, "ChemSearch Tool", 
                             "Search for chemical elements and their properties", 
                             self.open_chem_search)
        
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
                              font=(self.default_font, 14, 'bold'),
                              bg="white",
                              fg="#202124")
        title_label.pack(padx=15, pady=(15, 5), anchor='w')
        
        desc_label = tk.Label(card, 
                             text=description, 
                             font=(self.default_font, 10),
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
    
    def open_chem_search(self):
        self.status_bar.config(text="Starting ChemSearch application...")
        
        # Determine the path to the chem_search application
        current_dir = os.path.dirname(os.path.abspath(__file__))
        chem_search_dir = os.path.join(current_dir, 'chem_search')
        app_path = os.path.join(chem_search_dir, 'app.py')
        
        # Run Flask app in a separate thread
        threading.Thread(target=self.run_flask_app, args=(app_path, 5004, 'ChemSearch')).start()
        
        # Give Flask a moment to start
        self.root.after(1500, lambda: self.open_browser(5004, "ChemSearch"))
    
    def run_flask_app(self, app_path, port=5000, app_name="App"):
        try:
            # Create platform-specific subprocess config
            if self.os_name == 'Windows':
                # On Windows, use shell=True for better process handling
                # and create a detached process that doesn't show a console window
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                process = subprocess.Popen(
                    [sys.executable, app_path],
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE
                )
            else:
                # On Unix-like systems, we can use standard approach
                # Redirect output to /dev/null to avoid blocking
                with open(os.devnull, 'w') as devnull:
                    process = subprocess.Popen(
                        [sys.executable, app_path],
                        stdout=devnull,
                        stderr=devnull,
                        preexec_fn=os.setpgrp  # Prevent the process from receiving parent's signals
                    )
            
            # Store the process for cleanup
            self.processes.append({
                'process': process,
                'name': app_name,
                'port': port
            })
            
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
    
    def cleanup_processes(self):
        """Terminate all started processes."""
        if not self.processes:
            return
            
        self.status_bar.config(text="Cleaning up running processes...")
        
        for proc_info in self.processes:
            process = proc_info['process']
            name = proc_info['name']
            port = proc_info.get('port')
            
            try:
                self.status_bar.config(text=f"Terminating {name} process...")
                
                if self.os_name == 'Windows':
                    # On Windows, terminate the process
                    process.terminate()
                else:
                    # On Unix systems, kill the process group if possible
                    try:
                        # Try to kill the process group (if we used preexec_fn=os.setpgrp)
                        pgid = os.getpgid(process.pid)
                        os.killpg(pgid, signal.SIGTERM)
                    except (ProcessLookupError, OSError):
                        # Fall back to killing just the process
                        process.terminate()
                        
                # Kill by port if process termination fails
                if port:
                    self.kill_process_by_port(port)
                    
            except Exception as e:
                self.status_bar.config(text=f"Error terminating {name}: {str(e)}")
                
        # Wait a moment for processes to terminate
            self.root.after(500, self.ensure_processes_terminated)
        
        def ensure_processes_terminated(self):
            """Ensure all processes are terminated after a delay."""
            # Make sure all processes are really dead
            still_alive = []
        for proc_info in self.processes:
            if proc_info['process'].poll() is None:  # None means still running
                still_alive.append(proc_info)
                
        # Force kill any remaining processes
        for proc_info in still_alive:
            try:
                self.status_bar.config(text=f"Force killing {proc_info['name']}...")
                proc_info['process'].kill()
            except:
                pass
                
        self.processes = []  # Clear the process list
        self.status_bar.config(text="All processes terminated")
    
    def kill_process_by_port(self, port):
        """Kill process using a specific port."""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    for conn in proc.connections():
                        if conn.laddr.port == port:
                            proc_obj = psutil.Process(proc.info['pid'])
                            proc_obj.terminate()
                            return True
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    continue
        except:
            pass
        return False
        
    def on_closing(self):
        """Handle window close event."""
        self.cleanup_processes()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ToolsetApp(root)
    root.mainloop()