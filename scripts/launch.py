import subprocess
import requests
import time

def check_url(url):
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.ConnectionError:
        return False

print('\033[32m========================= spinning up codegen backend =========================\033[0m')
backend_process = subprocess.Popen(['python', 'codegen/serve.py'])

# wait until the backend process is up and running
backend_url = 'http://localhost:5000/active'
timeout = 60 
start_time = time.time()

while True:
    if check_url(backend_url):
        break
    elif time.time() - start_time > timeout:
        print("Timeout reached while waiting for the backend process to start.")
        backend_process.terminate()
        exit(1)
    else:
        time.sleep(1)

print('\033[32m========================= spinning up geode frontend =========================\033[0m')
frontend_process = subprocess.Popen(['streamlit', 'run', 'app/app.py'])

# Wait for the frontend process to finish
frontend_process.wait()