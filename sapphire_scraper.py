from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get MongoDB URI from environment variable, fallback to localhost if not set
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)  # Use environment variable for MongoDB connection
db = client["ShopSmart-Fyp"]
collection = db["products"]

# Set up Selenium WebDriver
driver = webdriver.Edge()

# url = "https://pk.khaadi.com/fabrics/2-piece/?prefn1=filter_categories&prefv1=2+Piece&start=0&sz=58"
url = "https://pk.sapphireonline.pk/collections/woman?page=9"

driver.get(url)

# Scroll down to load all products
scroll_pause_time = 5
total_scrolls = 20

for _ in range(total_scrolls):

    driver.execute_script("window.scrollBy(0, 1000);")


    time.sleep(scroll_pause_time)

# Get the page source and parse it
soup = BeautifulSoup(driver.page_source, "html.parser")



# Find the outer div with the specified class
outer_div = soup.find("div", class_="row product-grid justify-content-center")

# Initialize list to store product data
product_data = []

# Loop through each product card
for card in outer_div.find_all("div", class_="plp-tile"):
    # Get basic product info from the card
    product_outer_div = card.find("div", class_="product")
    product_inner_div = product_outer_div.find("div", class_="product-tile") if product_outer_div else None
    product_tile_outer_body = product_inner_div.find("div", class_="d-flex justify-content-between product-tile-element  ") if product_inner_div else None
    product_tile_body = product_tile_outer_body.find("div", class_="tile-body") if product_tile_outer_body else None
    product_link_div = product_tile_body.find("div", class_="pdp-link")
    product_link = product_link_div.find("a", class_="link")

    product_url = "https://pk.khaadi.com" + product_link["href"] if not product_link["href"].startswith("http") else product_link["href"]
    print(f"Product URL: {product_url}")

    # Get product title
    product_title = product_link.text.strip() if product_link else None
    print(f"Product Title: {product_title}")

    # Get product category and price
    category = product_tile_body.find("div", class_="subtitle").text.strip() if product_tile_body.find("div", class_="subtitle") else None
    price_div = product_tile_body.find("div", class_="price")
    outer_span = price_div.find("span", class_="sales  d-inline-block") if price_div else None
    current_price = outer_span.find("span", class_="value cc-price").text.strip() if price_div and price_div.find("span", class_="value cc-price") else None
        
    # Get image URL
    img_outer_div = product_inner_div.find("div", class_="image-container plp-product-image-container link")
    img_inner_div = img_outer_div.find("div", class_="plp-dual-image link") if img_outer_div else None
    img_div = img_inner_div.find("a", class_="link") if img_inner_div else None
    img_url = img_div.find("img")["src"] if img_div and img_div.find("img") else None
    print(f"Image URL: {img_url}")

    
    # Append all product data
    product_data.append({
        "productUrl": product_url,
        "title": product_title,
        "brand": "Sapphire",
        "description": "N/A",
        "category": category,
        "colors": "N/A",
        "location": "N/A",
        "currentPrice": current_price,
        "discountRate": "N/A",
        "originalPrice": "N/A",
        "imageUrl": img_url,
        "sizes": ["2PC", "3PC"],
        "ratingScore": "N/A",
        "ratingCount": "N/A",
        "reviews": "No Reviews"
    })
    
    print(f"Scraped product: {product_title}")

# Close the browser
driver.quit()

# Save to MongoDB
if product_data:
    collection.insert_many(product_data)
    print("Data successfully stored in MongoDB!")
else:
    print("No data to store.")