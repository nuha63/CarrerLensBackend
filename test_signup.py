import urllib.request
import urllib.error
import json

url = 'https://carrerlensbackend.onrender.com/auth/signup'
data = json.dumps({'email': 'testxyz999@test.com', 'password': 'Test123', 'name': 'Test'}).encode()
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as response:
        print("Status:", response.status)
        print("Response:", response.read().decode())
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("Response body:", e.read().decode())
except Exception as e:
    print("Other error:", e)
