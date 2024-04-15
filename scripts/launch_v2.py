import subprocess

print('\033[32m========================= spinning up geode frontend =========================\033[0m')
frontend_process = subprocess.Popen(['streamlit', 'run', 'app/app.py'])

# Wait for the frontend process to finish
frontend_process.wait()