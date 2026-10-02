import requests

url = "https://www.costco.ca/w/-/on/windsor/534"

response = requests.get(
    url,
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-CA,en;q=0.9",
    },
    timeout=30,
)

print("Status:", response.status_code)
print("Length:", len(response.text))

# Look for possible price information
keywords = [
    "1.729",
    "regular",
    "premium",
    "gasPrice",
    "gasoline",
    "warehouse",
]

for keyword in keywords:
    print(f"{keyword}: {keyword.lower() in response.text.lower()}")
