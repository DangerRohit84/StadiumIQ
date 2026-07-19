import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests

base = 'https://stadiumiq-7ski.onrender.com'

# Test with very short timeout to see if server responds at all
for path in ['/', '/api/health', '/api/csrf-token']:
    try:
        r = requests.get(base + path, timeout=8)
        print(f"{path}: {r.status_code}")
    except requests.exceptions.ConnectTimeout:
        print(f"{path}: CONNECT TIMEOUT (server not reachable)")
    except requests.exceptions.ReadTimeout:
        print(f"{path}: READ TIMEOUT (server slow/cold)")
    except requests.exceptions.ConnectionError as e:
        print(f"{path}: CONNECTION ERROR ({str(e)[:60]})")
    except Exception as e:
        print(f"{path}: {type(e).__name__}: {str(e)[:60]}")
