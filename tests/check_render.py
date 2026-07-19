import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests

base = 'https://stadiumiq-7ski.onrender.com'

print(f"Testing {base} ...")
try:
    r = requests.get(base + '/', timeout=30, stream=True)
    print(f"Homepage status: {r.status_code}")
    print(f"Server: {r.headers.get('Server', '?')}")
    chunk = next(r.iter_content(300), b'').decode('utf-8', 'ignore')
    print(f"First bytes: {chunk[:150]}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)[:120]}")

print("---")
try:
    r2 = requests.get(base + '/api/health', timeout=30)
    print(f"Health: {r2.status_code} -> {r2.text[:100]}")
except Exception as e:
    print(f"Health error: {type(e).__name__}: {str(e)[:120]}")
