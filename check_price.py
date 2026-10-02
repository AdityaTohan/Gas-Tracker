from playwright.sync_api import sync_playwright

URL = "https://www.costco.ca/w/-/on/windsor/534"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140 Safari/537.36"
    )

    print("Opening Costco...")
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)

    # Wait for Costco's warehouse details to appear
    gas_section = page.locator(
        '[data-testid="Text_warehousetile-seewarehousedetails-gasprices"]'
    )

    gas_section.wait_for(state="visible", timeout=60000)

    print("✅ Gas Prices section found!")

    # The price elements are inside the same warehouse details area.
    # Get the text around the gas-price section's parent.
    parent = gas_section.locator("xpath=..")

    print("Gas section text:")
    print(parent.inner_text())

    browser.close()
