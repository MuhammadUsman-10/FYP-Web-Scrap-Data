from selenium import webdriver
from selenium.webdriver.common.by import By
from openpyxl.workbook import Workbook
from bs4 import BeautifulSoup
import pandas as pd
import time
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Set up Selenium WebDriver (use Chrome or any other driver you prefer)
driver = webdriver.Edge()  # Ensure ChromeDriver is correctly installed

# Define the URL
url = "https://www.pakstyle.pk/cat/party-wear-dresses"
driver.get(url)

# MongoDB connect
# Get MongoDB URI from environment variable, fallback to localhost if not set
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)  # Use environment variable for MongoDB connection
# Database and Collection select
db = client["ShopSmart-Fyp"]
collection = db["products"]

# Scroll down in small increments to load all products and images
scroll_pause_time = 7  # Increased delay to allow slow-loading images
total_scrolls = 35     # Increased total scrolls to capture all content

for _ in range(total_scrolls):
    # Scroll down a little bit
    driver.execute_script("window.scrollBy(0, 500);")
    
    # Wait for content to load
    time.sleep(scroll_pause_time)

# Get the fully loaded page source and parse it with BeautifulSoup
soup = BeautifulSoup(driver.page_source, "html.parser")

# Close the browser
driver.quit()

# Find the outer div with the specified class
outer_div = soup.find("div", class_="on_list_view_false products nt_products_holder row fl_center row_pr_1 cdt_des_1 round_cd_false nt_cover ratio_nt position_8 space_30 nt_default")

# Initialize an empty list to store product data
product_data = []

# Loop through each individual product div inside the outer div
for prod_div in outer_div.find_all("div", class_="col-md-3 col-6 pr_animated done mt__30 pr_grid_item product nt_pr desgin__1"):
    # Find the product URL
    prod_link = prod_div.find("a", class_="d-block")
    product_url = "https://www.pakstyle.pk" + prod_link["href"] if prod_link else None
    
    # Find the image URL
    img_div = prod_div.find("div", class_="pr_lazy_img main-img nt_img_ratio nt_bg_lz padding-top__127_571 lazyloaded")
    img_url = "https://www.pakstyle.pk" + img_div["data-bgset"] if img_div and img_div.has_attr("data-bgset") else None
    
    # Find the product title
    title_h3 = prod_div.find("h3", class_="product-title pr fs__14 mg__0 fwm")
    product_title = title_h3.text.strip() if title_h3 else None
    
    # Find the product price
    price_span = prod_div.find("span", class_="price dib mb__5")
    # price = price_span.text.strip() if price_span else None

    if price_span:
        # Find the actual price inside the <del><b> tag
        actual_price_tag = price_span.find("del")
        actual_price = actual_price_tag.text.strip() if actual_price_tag else None

        # Find the discounted price inside the <b><ins> tag
        discounted_price_tag = price_span.find("ins")
        discounted_price = discounted_price_tag.text.strip() if discounted_price_tag else None
    else:
        actual_price = None
        discounted_price = None
    # Append the data to the list
    product_data.append({
        "Product URL": product_url,
        "Image URL": img_url,
        "Title": product_title,
        "Actual Price": actual_price,
        "Discounted Price": discounted_price
    })

# Convert product data to MongoDB format
if product_data:
    collection.insert_many(product_data)
    print("Data successfully stored in MongoDB!")
else:
    print("No data to store.")

# Convert the data to a DataFrame
df = pd.DataFrame(product_data)

# Save the DataFrame to an Excel file
df.to_excel("scraped_data.xlsx", index=False)
print("Data saved to scraped_data.xlsx")
