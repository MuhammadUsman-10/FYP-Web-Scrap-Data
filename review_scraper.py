import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from pymongo import MongoClient
from bson.objectid import ObjectId


client = MongoClient("mongodb://localhost:27017/")  # Local Environment MongoDB connection
db = client["ShopSMart-Fyp"]
collection = db["products"]


driver = webdriver.Edge()
# Fetch all products with empty reviews
products = collection.find({
    "category": "mens-shoes",
    "reviews": {"$size": 0}
})

for product in products:
    url = product['productUrl']
    product_id = product['_id']
    print(f"Scraping reviews for: {url}")

    driver.get(url)
    time.sleep(3)

    reviews = []

    ## Scrape reviews using the same logic as review_scraper.py
    try:
        # Scroll to load reviews
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(500, 800);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(800, 1000);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(1000, 1300);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(1300, 1600);")
        time.sleep(1)

        page = 1
        while True:  # Continue until we explicitly break
            try:
                # Finding the container for reviews
                reviews_container = driver.find_element(By.XPATH, '//*[@id="module_product_review"]/div/div/div[3]/div[1]')
                
                # Finding all individual reviews on the current page
                review_elements = reviews_container.find_elements(By.CLASS_NAME, 'item')
                
                if not review_elements:  # If no reviews found on this page
                    print(f'No reviews found on page {page}')
                    break

                # Looping through each review on the current page
                for i in range(len(review_elements)):
                    try:
                        review_text = review_elements[i].find_element(By.CSS_SELECTOR, f"#module_product_review > div > div > div:nth-child(3) > div.mod-reviews > div:nth-child({i+1}) > div.item-content > div.content").text
                        if review_text:
                            reviews.append(review_text)
                    except Exception as e:
                        print(f"Error extracting review text: {str(e)}")
                        continue

                # Try to go to next page
                try:
                    next_button = driver.find_element(By.XPATH, '//*[@id="module_product_review"]/div/div/div[3]/div[2]/div/button[2]')
                    if not next_button.is_enabled():  # Check if next button is disabled
                        print(f'Reached last page ({page})')
                        break
                    driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(5)
                    page += 1
                except NoSuchElementException:
                    print(f'No more pages after page {page}')
                    break
            except NoSuchElementException:
                print('No review section found')
                break
    except Exception as e:
        print(f"Error while scraping reviews: {str(e)}")
        print("Continuing with available reviews...")

    # Update product with reviews
    collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"reviews": reviews}}
    )
    print(f"Saved {len(reviews)} reviews for product ID {product_id}\n")
# Close the driver
driver.quit()