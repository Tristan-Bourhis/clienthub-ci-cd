"""Lance une vraie API HTTP contre MySQL puis les tests E2E, sans build Docker."""
import os
import subprocess
import sys
import time
from urllib.request import urlopen

process = subprocess.Popen([sys.executable, '-m', 'gunicorn', '--bind', '127.0.0.1:5000', 'app:app'])
try:
    for attempt in range(60):
        if process.poll() is not None:
            raise RuntimeError('Le serveur API a quitté')
        try:
            with urlopen('http://127.0.0.1:5000/health', timeout=2):
                break
        except OSError:
            time.sleep(1)
    else:
        raise RuntimeError('API indisponible')
    subprocess.run([sys.executable, 'tests/check_http.py'], check=True,
                   env={**os.environ, 'WEB_URL': 'http://127.0.0.1:5000'})
finally:
    process.terminate()
    process.wait(timeout=15)
