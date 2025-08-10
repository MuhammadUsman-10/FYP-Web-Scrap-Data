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
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

client = MongoClient(MONGO_URI)  # Use environment variable for MongoDB connection
db = client["ShopSmart-Fyp"]
collection = db["products"]

# Set up Selenium WebDriver
driver = webdriver.Edge()

# url = "https://pk.khaadi.com/fabrics/2-piece/?prefn1=filter_categories&prefv1=2+Piece&start=0&sz=58"
url = "https://pk.khaadi.com/fabrics/3-piece/?prefn1=filter_categories&prefv1=3+Piece&start=0&sz=100"

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
outer_div = soup.find("div", class_="row refinement-bar-acitve")

# Initialize list to store product data
product_data = []

# Loop through each product card
for card in outer_div.find_all("div", class_="product"):
    # Get basic product info from the card
    product_div = card.find("div", class_="product-tile")
    if not product_div:
        continue

    product_tile_body = product_div.find("div", class_="tile-body")
    product_link = product_tile_body.find("a", class_="link plpRedirectPdp")
    if not product_link:
        continue

    product_url = "https://pk.khaadi.com" + product_link["href"] if not product_link["href"].startswith("http") else product_link["href"]
    product_title = product_tile_body.find("h2", class_="pdp-link-heading").text.strip() if product_div.find("h2", class_="pdp-link-heading") else None
    
    # Get image URL
    img_outer_div = card.find("div", class_="image-container")
    img_div = img_outer_div.find("a", class_="plp-tap-mobile plpRedirectPdp") if img_outer_div else None
    img_url = img_div.find("img")["src"] if img_div and img_div.find("img") else None
    print(f"Product URL: {product_url}, Title: {product_title}, Image URL: {img_url}")
    
    # Now visit the product page to get more details
    driver.get(product_url)
    time.sleep(3)  # Wait for page to load
    
    # Get the product page source
    product_soup = BeautifulSoup(driver.page_source, "html.parser")

    product_outer_div1 = product_soup.find("div", class_="row product-detail-wrapper")
    if product_outer_div1:
        product_outer_div2 = product_outer_div1.find("div", class_="product-info-wrapper col-12 col-md-5")
        if product_outer_div2:
            product_outer_div3 = product_outer_div2.find("div", class_="details-pdp")
            if product_outer_div3:
                # Get product category & price
                category = product_outer_div3.find("div", class_="product-brand").text.strip() if product_outer_div3.find("div", class_="product-brand") else None
                print(f"Category: {category}")

                # Get product prices
                prices_outer_div = product_outer_div3.find("div", class_="name-and-price")
                if prices_outer_div:
                    # Get current price
                    # prices_inner_div1 = prices_outer_div.find("div", class_="")
                    prices_inner_div = prices_outer_div.find("div", class_="price")
                    current_price = prices_outer_div.find("span", class_="value cc-price").text.strip() if prices_inner_div and prices_inner_div.find("span", class_="value cc-price") else None
                    print(f"Current Price: {current_price}")

    
    # Append all product data
    product_data.append({
        "productUrl": product_url,
        "title": product_title,
        "brand": "Khaadi",
        "description": "N/A",
        "category": category,
        "colors": "N/A",
        "location": "N/A",
        "currentPrice": current_price,
        "discountRate": "N/A",
        "originalPrice": "N/A",
        "imageUrl": img_url,
        "sizes": "3PC",
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