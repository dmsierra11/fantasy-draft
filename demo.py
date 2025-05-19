import webbrowser
import time
import os
import subprocess
import sys

def start_server():
    """Start the FastAPI server in a separate process"""
    if sys.platform == 'win32':
        subprocess.Popen(['uvicorn', 'main:app', '--reload'], 
                        creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        subprocess.Popen(['uvicorn', 'main:app', '--reload'])

def open_browser_windows():
    """Open multiple browser windows for each team"""
    # Wait for server to start
    time.sleep(2)
    
    # Open browser windows
    webbrowser.open('http://localhost:8000')
    time.sleep(1)
    webbrowser.open('http://localhost:8000')
    time.sleep(1)
    webbrowser.open('http://localhost:8000')
    time.sleep(1)
    webbrowser.open('http://localhost:8000')

def main():
    print("Starting Fantasy Draft Demo...")
    print("\nInstructions:")
    print("1. The server will start automatically")
    print("2. Four browser windows will open")
    print("3. In each window:")
    print("   - Click 'Start Draft' (only in one window)")
    print("   - Select a different team from the dropdown")
    print("   - Make picks when it's your team's turn")
    print("\nPress Enter to start...")
    input()
    
    start_server()
    open_browser_windows()
    
    print("\nDemo is running!")
    print("Keep this terminal window open while using the demo.")
    print("Press Ctrl+C to stop the server when done.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping server...")
        sys.exit(0)

if __name__ == "__main__":
    main() 