import requests

URL = "https://www.costco.ca/AjaxGetGasPricesService?warehouseid=534"

response = requests.get(
    URL,
    headers={
        "User-Agent": "Mozilla/5.0"
    },
    timeout=30
)

response.raise_for_status()

data = response.json()

regular = float(data["534"]["regular"])
premium = float(data["534"]["premium"])

print(f"Regular: ${regular:.3f}/L")
print(f"Premium: ${premium:.3f}/L")
