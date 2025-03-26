from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import re


# Setup Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# URL of the website
url = "http://boot24.ch/chde/occasionsboote/?cat=2"
driver.get(url)

# Wait for JavaScript to load
time.sleep(5)

# Find all boat listings
boat_listings = driver.find_elements(By.CLASS_NAME, "blurb")

print(f"✅ Found {len(boat_listings)} boat listings")

boats_data = []

for boat in boat_listings:
    try:
        # Extract Boat Name
        title_element = boat.find_element(By.TAG_NAME, "h3")
        title = title_element.text.strip() if title_element else "Unknown"

        # Extract Price (allow empty values)
        try:
            price_tag = boat.find_element(By.CLASS_NAME, "blurb__price")
            price = int(re.sub(r"[^\d]", "", price_tag.text.strip())) if price_tag.text.strip() else None
        except:
            price = None

        # Extract Baujahr (from the <ul> with class "blurb__description l-mb-12")
        try:
            description_list = boat.find_element(By.CLASS_NAME, "blurb__description")
            descriptions = [li.text for li in description_list.find_elements(By.TAG_NAME, "li")]
            year = next((int(re.search(r"\d{4}", item).group()) for item in descriptions if "Baujahr" in item), None)
        except:
            year = None

        # Extract Size (Abmessung)
        try:
            size_tag = boat.find_element(By.XPATH, ".//span[text()='Abmessungen']/preceding-sibling::span")
            size = size_tag.text.strip() if size_tag.text.strip() else None
        except:
            size = None

        # Extract Engine Power (Motorleistung)
        try:
            motor_tag = boat.find_element(By.XPATH, ".//span[text()='Motorleistung']/preceding-sibling::span")
            motor_power = motor_tag.text.strip() if motor_tag.text.strip() else None
        except:
            motor_power = None

        # Determine if the boat is "New" based on "Occasionsboot"
        is_new = "Occasionsboot" not in descriptions

        # Debugging Output (Print extracted values)
        print(f"🚤 {title} | Year: {year} | Size: {size} | Power: {motor_power} | Price: {price} | New: {is_new}")

        # Append extracted data
        boats_data.append({
            "Boat Name": title,
            "Baujahr": year,
            "Abmessung": size,
            "Motorleistung": motor_power,
            "Preis": price,
            "New": is_new
        })

    except Exception as e:
        print(f"⚠️ Skipping a listing due to error: {e}")
        continue

# Convert list to DataFrame
df = pd.DataFrame(boats_data)

# Explicitly convert "Baujahr" to Int64 to remove decimals
df["Baujahr"] = pd.to_numeric(df["Baujahr"], errors="coerce").astype("Int64")

# Save DataFrame to CSV file
df.to_csv("boats_data_1.csv", index=False, encoding="utf-8")
print("✅ Data saved to boats_data.csv")

# Close Selenium driver
driver.quit()

# Print first 5 rows to verify
print(df.head())
