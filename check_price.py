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

gas_section = soup.select_one(
    '[data-testid="Text_warehouseetile-seewarehousedetails-gasprices"]'
)

if not gas_section:
    print("❌ Gas price section not found")
    exit(1)

print("✅ Gas price section found!")

# Find the two price values following the "Gas Prices" element
prices = []

for element in gas_section.find_all_next("span"):
    text = element.get_text(strip=True)

    if text.startswith("$"):
        prices.append(text)

    if len(prices) == 2:
        break

if len(prices) < 2:
    print("❌ Could not find both prices")
    exit(1)

regular = prices[0]
premium = prices[1]

print(f"Regular: {regular}/L")
print(f"Premium: {premium}/L")
