from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
from pymongo import MongoClient
import json

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["Web-Scraping"]
collection = db["daraz_products"]

def setup_driver():
    """Initialize and return a configured WebDriver"""
    driver = webdriver.Edge()
    driver.maximize_window()
    return driver

def get_product_details(driver, product_url):
    """Extract detailed information from a product page"""
    driver.get(product_url)
    time.sleep(3)  # Wait for page to load
    
    try:
        # Wait for product details to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "pdp-product-title"))
        )
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Extract product details
        title = soup.find("h1", class_="pdp-product-title").text.strip()
        description = soup.find("div", class_="pdp-product-description").text.strip()
        
        # Price extraction
        price_div = soup.find("div", class_="pdp-price")
        current_price = price_div.find("span", class_="pdp-price_type_normal").text.strip()
        original_price = price_div.find("span", class_="pdp-price_type_deleted").text.strip() if price_div.find("span", class_="pdp-price_type_deleted") else None
        
        # Image URLs
        image_divs = soup.find_all("div", class_="gallery-preview-panel__image")
        image_urls = [img.find("img")["src"] for img in image_divs if img.find("img")]
        
        # Reviews
        reviews = []
        review_elements = soup.find_all("div", class_="review-item")
        for review in review_elements:
            review_text = review.find("div", class_="review-content").text.strip()
            rating = review.find("div", class_="rating").text.strip()
            reviews.append({"text": review_text, "rating": rating})
        
        return {
            "title": title,
            "description": description,
            "current_price": current_price,
            "original_price": original_price,
            "image_urls": image_urls,
            "reviews": reviews,
            "product_url": product_url
        }
    except Exception as e:
        print(f"Error scraping product {product_url}: {str(e)}")
        return None

def scrape_daraz_products(category_url, max_pages=5):
    """Main function to scrape products from Daraz"""
    driver = setup_driver()
    all_products = []
    
    try:
        for page in range(1, max_pages + 1):
            page_url = f"{category_url}?page={page}"
            driver.get(page_url)
            time.sleep(3)  # Wait for page to load
            
            # Scroll to load all products
            for _ in range(5):
                driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(1)
            
            soup = BeautifulSoup(driver.page_source, "html.parser")
            product_links = soup.find_all("a", class_="product-card")
            
            for link in product_links:
                product_url = "https:" + link["href"] if not link["href"].startswith("http") else link["href"]
                product_data = get_product_details(driver, product_url)
                if product_data:
                    all_products.append(product_data)
                    print(f"Scraped product: {product_data['title']}")
            
            print(f"Completed page {page}")
    
    finally:
        driver.quit()
    
    # Save to MongoDB
    if all_products:
        collection.insert_many(all_products)
        print("Data successfully stored in MongoDB!")
    
    # Save to Excel
    df = pd.DataFrame(all_products)
    df.to_excel("daraz_products.xlsx", index=False)
    print("Data saved to daraz_products.xlsx")

if __name__ == "__main__":
    # Example category URL for clothing
    category_url = "https://www.daraz.pk/womens-clothing/"
    scrape_daraz_products(category_url) 