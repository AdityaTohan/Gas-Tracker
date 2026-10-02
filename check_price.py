import requests
from bs4 import BeautifulSoup

URL = "https://www.costco.ca/w/-/on/windsor/534"

response = requests.get(
    URL,
    headers={
        "User-Agent": "Mozilla/5.0"
    },
    timeout=30
)

response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

text = soup.get_text(" ", strip=True)

print(text)
