# Web Scraper for https://global.essentialmeds.org/dashboard/countries/
# Created by James Hu with ChatGPT; Rethink Priorities, 2023

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import pandas as pd

# Set up headless Firefox options
options = Options()
options.add_argument('-headless')
options.add_argument('--disable-notifications')
options.add_argument('--no-sandbox')
options.add_argument('--verbose')

# Initialize constants and dictionaries
NUM_COUNTRIES = 137
SCROLL_HEIGHT = 38
country_to_consistencies = {}
country_to_differences = {}

# Generate list of URLs to be scraped
urls = []

for n in range(1,NUM_COUNTRIES+1):
    url = 'https://global.essentialmeds.org/dashboard/countries/' + str(n)
    urls.append(url)

# Start the browser
driver = webdriver.Firefox(options=options)
wait = WebDriverWait(driver, 10)  # Initialize wait object

for url in urls:
    # ITEMS CONSISTENT WITH WORLD HEALTH ORGANIZATION LIST
    # Open the webpage
    driver.get(url)
    
    # Locate the scrollable element
    scrollable_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.css-o6nvc9 > div:nth-child(2)')))

    # Scroll through the internal scrollable element to load all products
    scroll_step = SCROLL_HEIGHT * 10  # Set the scroll_step equal to the height of 10 product elements
    scroll_position = 0
    consistencies = set()

    while True:
        # Scroll down
        driver.execute_script(f"arguments[0].scrollTop = {scroll_position};", scrollable_element)
        scroll_position += scroll_step
        time.sleep(0.2)

        # Get the page source after scrolling
        html = driver.page_source

        # Use BeautifulSoup to parse and extract the data
        soup = BeautifulSoup(html, 'html.parser')
        product_list = soup.select('.css-t9ct1g')

        # Add visible products to the consistencies set
        current_product_count = len(consistencies)
        for product in product_list:
            consistencies.add(product.text.strip())

        # Break the loop if the product count doesn't change after scrolling
        if len(consistencies) == current_product_count:
            break

    country = soup.select('.css-147a4oj > h4:nth-child(1)')[0].text.strip()
    country_to_consistencies[country] = consistencies
        
    # ITEMS DIFFERENT FROM WORLD HEALTH ORGANIZATION LIST
    # Click the "Differences with the WHO list" button
    element_to_click = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/div[1]/div[2]/div[3]/div[1]/div[2]')))
    element_to_click.click()
    time.sleep(0.2)

    # Locate the scrollable element
    scrollable_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.css-o6nvc9 > div:nth-child(2)')))

    # Scroll through the internal scrollable element to load all products
    scroll_step = SCROLL_HEIGHT * 10  # Set the scroll_step equal to the height of 10 product elements
    scroll_position = 0
    differences = set()
    
    while True:
        # Scroll down
        
        driver.execute_script(f"arguments[0].scrollTop = {scroll_position};", scrollable_element)
        
        scroll_position += scroll_step
        time.sleep(0.2)

        # Get the page source after scrolling
        html = driver.page_source

        # Use BeautifulSoup to parse and extract the data
        soup = BeautifulSoup(html, 'html.parser')
        product_list = soup.select('.css-t9ct1g')

        # Add visible products to the differences set
        current_product_count = len(differences)
        for product in product_list:
            differences.add(product.text.strip())

        # Break the loop if the product count doesn't change after scrolling
        if len(differences) == current_product_count:
            break

    country_to_differences[country] = differences

# Close the browser
driver.quit()

# Create a set for the WHO EML
who_eml = set.union(*country_to_consistencies.values())

# Combine the dictionaries
all_products = {}
for country, products in country_to_consistencies.items():
    all_products[country] = products | country_to_differences[country]

# Add the WHO EML column
all_products["WHO EML"] = who_eml

# Create a list of all unique products and sort it alphabetically
unique_products = sorted(set.union(who_eml, *country_to_differences.values()))

# Create an empty DataFrame with the desired column order
sorted_countries = sorted(col for col in all_products.keys() if col != "WHO EML")
columns = ["Product", "WHO EML"] + sorted_countries
df = pd.DataFrame(columns=columns)

# Fill the DataFrame
for product in unique_products:
    row_data = {col: int(product in product_set) for col, product_set in all_products.items()}
    row_data["Product"] = product
    row = pd.Series(row_data, name=product)
    df = df.append(row)

# Reset the index
df.reset_index(drop=True, inplace=True)

# Export DataFrame to an Excel file
df.to_excel("products_eml.xlsx", index=False)