'''
run_project.py
This script automates the building and running of the various containers. 
It also opens a browser with the dashboard.

Author: Amil Shrivastava
'''

import subprocess
import time
import webbrowser

# Build and run the containers
subprocess.run(["docker-compose", "build", "--no-cache"])
subprocess.run(["docker-compose", "up", "-d"])

# Wait for Streamlit to be ready
print("Waiting for Streamlit to be ready...")

# Wait for streamlit to be setup
time.sleep(5)

while True:
    try:
        # Checking if Streamlit is up by accessing the localhost URL (8501)
        subprocess.run(["curl", "-s", "http://localhost:8501"], check=True)
        break
    except subprocess.CalledProcessError:
        # If Streamlit is not yet available, retry after 1 second
        time.sleep(1)

# Open the browser
webbrowser.open("http://localhost:8501")
