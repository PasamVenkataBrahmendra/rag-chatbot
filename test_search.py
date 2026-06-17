import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("SERPER_API_KEY")
print(f"API Key found: {api_key[:10]}..." if api_key else "NO API KEY FOUND!")

url = "https://google.serper.dev/search"
headers = {
    "X-API-KEY": api_key,
    "Content-Type": "application/json"
}
payload = {"q": "Who won IPL 2025?", "num": 5}

response = requests.post(url, headers=headers, json=payload, timeout=10)
print(f"Status code: {response.status_code}")
data = response.json()
print(f"Response: {data}")