```python
import json
import os
from datetime import datetime, timedelta, timezone

# --------------------------------------------------
# Your existing Costco price-fetching code goes here
# --------------------------------------------------

# Example:
# Replace these values with the values returned by
# your existing Costco price checker.

warehouse = "Windsor"
warehouse_id = 534
regular = 1.699
premium = 1.869

# --------------------------------------------------
# Save price history
# --------------------------------------------------

FILE = "prices.json"

now = datetime.now(timezone.utc)

new_price = {
    "warehouse": warehouse,
    "warehouse_id": warehouse_id,
    "regular": regular,
    "premium": premium,
    "checked_at": now.isoformat()
}

# Load existing history
if os.path.exists(FILE):
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            prices = json.load(f)

        # Make sure the file contains a list
        if not isinstance(prices, list):
            prices = []

    except (json.JSONDecodeError, OSError):
        prices = []
else:
    prices = []

# Add the new price
prices.append(new_price)

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
        # Ignore malformed old records
        continue

prices = filtered_prices

# Save the updated history
with open(FILE, "w", encoding="utf-8") as f:
    json.dump(prices, f, indent=2)

print(f"Saved price. Total records: {len(prices)}")
print(f"Regular: ${regular:.3f}")
print(f"Premium: ${premium:.3f}")
```
