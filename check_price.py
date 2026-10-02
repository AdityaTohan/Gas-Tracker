import requests
import json
from datetime import datetime, timezone

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

timestamp = datetime.now(timezone.utc).isoformat()

price_data = {
    "warehouse": "Windsor",
    "warehouse_id": 534,
    "regular": regular,
    "premium": premium,
    "checked_at": timestamp
}

with open("prices.json", "w") as file:
    json.dump(price_data, file, indent=2)

print(f"Regular: ${regular:.3f}/L")
print(f"Premium: ${premium:.3f}/L")
print(f"Checked at: {timestamp}")
