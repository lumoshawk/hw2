#!/usr/bin/env python3
"""
A command-line interface for the toolset.
This provides similar functionality to the GUI version but in a terminal.
"""

import subprocess
import webbrowser
import os
import sys
import threading
import time
import platform
import signal
import psutil  # Need to add this dependency for cross-platform process management
from typing import Callable, Dict, List, Any


class ToolsetCLI:
    def __init__(self):
        """Initialize the CLI toolset."""
        self.os_name = platform.system()  # 'Windows', 'Linux', 'Darwin' (macOS)
        self.tools = {}
        self.register_tools()
        # Track all processes started by this application
        self.processes = []
        # Set up signal handlers for cleanup on abnormal termination
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def register_tools(self):
        """Register available tools with their descriptions and handlers."""
        self.tools = {
            "1": {
                "name": "Chat Application",
                "description": "Open the web-based chat interface",
                "handler": self.open_chat_app
            },
            "2": {
                "name": "SciSearch Tool",
                "description": "Search for computer scientists and their publications on DBLP",
                "handler": self.open_sci_search
            },
            "3": {
                "name": "ChemSearch Tool",
                "description": "Search for chemical elements and their properties",
                "handler": self.open_chem_search
            },
            "4": {
                "name": "Future Tool 3",
                "description": "Coming soon: Description of future tool 3",
                "handler": lambda: self.show_message("Future Tool 3 coming soon!")
            },
            "q": {
                "name": "Quit",
                "description": "Exit the toolset",
                "handler": self.quit
            }
        }

    def display_header(self):
        """Display the toolset header."""
        print("\n" + "=" * 60)
        print(" " * 20 + "A LITTLE TOOLSET (CLI)")
        print("=" * 60 + "\n")

    def display_menu(self):
        """Display the main menu of available tools."""
        print("Available Tools:")
        print("-" * 60)
        for key, tool in self.tools.items():
            print(f"{key}. {tool['name']} - {tool['description']}")
        print("-" * 60)

    def run_flask_app(self, app_path: str, port: int = 5000, app_name: str = "App"):
        """
        Run a Flask application in the background.
        
        Args:
            app_path: Path to the Flask application
            port: Port number for the Flask server
            app_name: Name of the application
        """
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
            
            print(f"{app_name} is starting...")
            
        except Exception as e:
            print(f"Error starting {app_name}: {str(e)}")

    def cleanup_processes(self):
        """Terminate all started processes."""
        if not self.processes:
            return
            
        print("\nCleaning up running processes...")
        
        for proc_info in self.processes:
            process = proc_info['process']
            name = proc_info['name']
            port = proc_info.get('port')
            
            try:
                print(f"Terminating {name} process...")
                
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
                print(f"Error terminating {name}: {str(e)}")
                
        # Wait a moment for processes to terminate
        time.sleep(0.5)
        
        # Make sure all processes are really dead
        still_alive = []
        for proc_info in self.processes:
            if proc_info['process'].poll() is None:  # None means still running
                still_alive.append(proc_info)
                
        # Force kill any remaining processes
        for proc_info in still_alive:
            try:
                print(f"Force killing {proc_info['name']}...")
                proc_info['process'].kill()
            except:
                pass
                
        self.processes = []  # Clear the process list
    
    def kill_process_by_port(self, port):
        """Kill process using a specific port."""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    for conn in proc.connections():
                        if conn.laddr.port == port:
                            print(f"Killing process {proc.info['name']} (PID: {proc.info['pid']}) using port {port}")
                            psutil.Process(proc.info['pid']).terminate()
                            return True
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    continue
        except:
            pass
        return False
        
    def signal_handler(self, sig, frame):
        """Handle signals for clean shutdown."""
        print("\nReceived termination signal.")
        self.cleanup_processes()
        sys.exit(0)
        
    def open_browser(self, port: int = 5000, app_type: str = "app"):
        """
        Open the default web browser to access the application.
        
        Args:
            port: Port number for the web application
            app_type: Type of application being opened
        """
        try:
            url = f'http://127.0.0.1:{port}'
            webbrowser.open(url)
            print(f"{app_type.capitalize()} opened in browser at {url}")
        except Exception as e:
            print(f"Error opening browser: {str(e)}")

    def open_chat_app(self):
        """Start the chat application and open it in a browser."""
        print("Starting chat application...")
        
        # Determine the path to the chat application
        current_dir = os.path.dirname(os.path.abspath(__file__))
        chat_dir = os.path.join(current_dir, 'chat')
        app_path = os.path.join(chat_dir, 'app.py')
        
        # Run Flask app in a separate thread
        threading.Thread(target=self.run_flask_app, args=(app_path, 5000, 'Chat')).start()
        
        # Give Flask a moment to start
        print("Waiting for server to start...")
        time.sleep(1.5)
        self.open_browser(5000, "chat")
        
        # Return to the main menu after a brief pause
        input("\nPress Enter to return to the main menu...")

    def open_sci_search(self):
        """Start the SciSearch application and open it in a browser."""
        print("Starting SciSearch application...")
        
        # Determine the path to the sci_search application
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sci_search_dir = os.path.join(current_dir, 'sci_search')
        app_path = os.path.join(sci_search_dir, 'app.py')
        
        # Run Flask app in a separate thread
        threading.Thread(target=self.run_flask_app, args=(app_path, 5001, 'SciSearch')).start()
        
        # Give Flask a moment to start
        print("Waiting for server to start...")
        time.sleep(1.5)
        self.open_browser(5001, "SciSearch")
        
        # Return to the main menu after a brief pause
        input("\nPress Enter to return to the main menu...")

    def open_chem_search(self):
        """Start the ChemSearch application and open it in a browser."""
        print("Starting ChemSearch application...")
        
        # Determine the path to the chem_search application
        current_dir = os.path.dirname(os.path.abspath(__file__))
        chem_search_dir = os.path.join(current_dir, 'chem_search')
        app_path = os.path.join(chem_search_dir, 'app.py')
        
        # Run Flask app in a separate thread
        threading.Thread(target=self.run_flask_app, args=(app_path, 5004, 'ChemSearch')).start()
        
        # Give Flask a moment to start
        print("Waiting for server to start...")
        time.sleep(1.5)
        self.open_browser(5004, "ChemSearch")
        
        # Return to the main menu after a brief pause
        input("\nPress Enter to return to the main menu...")

    def show_message(self, message: str):
        """Display a message to the user and wait for acknowledgment."""
        print(f"\n{message}")
        input("\nPress Enter to return to the main menu...")

    def quit(self):
        """Exit the application."""
        print("\nExiting A Little Toolset. Goodbye!")
        self.cleanup_processes()
        sys.exit(0)

    def run(self):
        """Run the main CLI loop."""
        try:
            while True:
                self.display_header()
                self.display_menu()
                
                choice = input("\nEnter your choice (or 'q' to quit): ").strip().lower()
                
                if choice in self.tools:
                    self.tools[choice]["handler"]()
                else:
                    print(f"\nInvalid choice: '{choice}'. Please select a valid option.")
                    input("\nPress Enter to continue...")
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            self.signal_handler(signal.SIGINT, None)


if __name__ == "__main__":
    app = ToolsetCLI()
    app.run()