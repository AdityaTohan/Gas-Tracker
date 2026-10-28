
import requests
import json
import os
from datetime import datetime, timedelta, timezone

# --------------------------------------------------
# Fetch Costco Windsor gas prices
# --------------------------------------------------
URL = "https://www.costco.ca/AjaxGetGasPricesService?warehouseid=534"

response = requests.get(
    URL,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30
)
response.raise_for_status()
data = response.json()

warehouse = "Windsor"
warehouse_id = 534

regular = float(data["534"]["regular"])
premium = float(data["534"]["premium"])

FILE = "prices.json"
now = datetime.now(timezone.utc)

new_price = {
    "warehouse": warehouse,
    "warehouse_id": warehouse_id,
    "regular": regular,
    "premium": premium,
    "checked_at": now.isoformat()
}

# --------------------------------------------------
# Load existing price history
# --------------------------------------------------
if os.path.exists(FILE):
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            prices = json.load(f)

        if not isinstance(prices, list):
            prices = []

    except (json.JSONDecodeError, OSError):
        prices = []
else:
    prices = []

# Keep only the last 365 days
one_year_ago = now - timedelta(days=365)
filtered_prices = []

for price in prices:
    try:
        checked_at = datetime.fromisoformat(
            price["checked_at"].replace("Z", "+00:00")
        )

        if checked_at >= one_year_ago:
            filtered_prices.append(price)

    except (KeyError, ValueError, TypeError):
        continue

prices = filtered_prices

# Compare against the previous recorded price
previous_price = prices[-1] if prices else None

regular_changed = (
    previous_price is not None
    and float(previous_price["regular"]) != regular
)

premium_changed = (
    previous_price is not None
    and float(previous_price["premium"]) != premium
)

# --------------------------------------------------
# Send OneSignal notification only when prices change
# --------------------------------------------------
if regular_changed or premium_changed:
    app_id = os.environ.get("ONESIGNAL_APP_ID")
    api_key = os.environ.get("ONESIGNAL_REST_API_KEY")

    if not app_id or not api_key:
        raise RuntimeError(
            "Missing ONESIGNAL_APP_ID or ONESIGNAL_REST_API_KEY."
        )

    changed_items = []

    if regular_changed:
        changed_items.append(
            f"Regular: ${previous_price['regular']:.3f} -> ${regular:.3f}/L"
        )

    if premium_changed:
        changed_items.append(
            f"Premium: ${previous_price['premium']:.3f} -> ${premium:.3f}/L"
        )

    message = "\n".join(changed_items)
    payload = {
        "app_id": app_id,
        "target_channel": "push",
        "included_segments": ["Subscribed Users"],
        "headings": {"en": "Costco Windsor gas price changed"},
        "contents": {"en": message},
        "url": "https://adityatohan.github.io/Gas-Tracker/"
    }

    notification_response = requests.post(
        "https://api.onesignal.com/notifications",
        headers={
            "Authorization": f"Key {api_key}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=30
    )
    notification_response.raise_for_status()

    print("Price-change notification sent.")
    print(message)
else:
    print("No price change. No notification sent.")

# --------------------------------------------------
# Save updated history
# --------------------------------------------------
prices.append(new_price)

with open(FILE, "w", encoding="utf-8") as f:
    json.dump(prices, f, indent=2)

print(f"Saved price. Total records: {len(prices)}")
print(f"Regular: ${regular:.3f}/L")
print(f"Premium: ${premium:.3f}/L")
