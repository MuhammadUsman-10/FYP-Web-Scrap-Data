from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from openpyxl.workbook import Workbook
from bs4 import BeautifulSoup
import pandas as pd
import time
from pymongo import MongoClient
import os
# from dotenv import load_dotenv

# load_dotenv()
# # Load environment variables from .env file
# MONGO_URI = os.getenv("MONGO_URI")


# # Check if the environment variable is loaded
# if not os.getenv("MONGO_URI"):
#     print("MONGO_URI not found in environment variables.")
# else:
#     print("MONGO_URI loaded successfully.")


# MongoDB setup
# client = MongoClient(MONGO_URI)  # Use the environment variable for MongoDB connection for Production

# Uncomment the line below for local testing
client = MongoClient("mongodb://localhost:27017/")  # Local Environment MongoDB connection
db = client["ShopSMart-Fyp"]
collection = db["products"]

# Set up Selenium WebDriver
driver = webdriver.Edge()

# Clothing Urls to scrape
# url = "https://www.daraz.pk/mens-clothing/"
# url = "https://www.daraz.pk/mens-clothing/?page=2"
# url = "https://www.daraz.pk/mens-clothing/?page=3"

# T-shirts/Trousers Urls to scrape
# url = "https://www.daraz.pk/mens-t-shirts/"
# url = "https://www.daraz.pk/mens-t-shirts/?page=2"
# url = "https://www.daraz.pk/mens-t-shirts/?page=3"
url = "https://www.daraz.pk/mens-polo-shirts/"
# url = "https://www.daraz.pk/mens-polo-shirts/?page=2"
# url = "https://www.daraz.pk/mens-polo-shirts/?page=3"
# url = "https://www.daraz.pk/mens-jeans/"
# url = "https://www.daraz.pk/mens-jeans/?page=2"
# url = "https://www.daraz.pk/mens-jeans/?page=3"
# url = "https://www.daraz.pk/mens-sweat-pants/"
# url = "https://www.daraz.pk/mens-sweat-pants/?page=2"
# url = "https://www.daraz.pk/mens-sweat-pants/?page=3"

# Hoodies/Sweatshirts Urls to scrape
# url = "https://www.daraz.pk/mens-hoodies/"
# url = "https://www.daraz.pk/mens-hoodies/?page=2"
# url = "https://www.daraz.pk/mens-hoodies/?page=3"

# Clothes Urls to scrape
# url = "https://www.daraz.pk/mens-unstitched-fabric/"
# url = "https://www.daraz.pk/mens-unstitched-fabric/?page=2"
# url = "https://www.daraz.pk/mens-unstitched-fabric/?page=3"
# url = "https://www.daraz.pk/mens-shawls/"
# url = "https://www.daraz.pk/mens-shawls/?page=2"
# url = "https://www.daraz.pk/mens-shawls/?page=3"


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
outer_div = soup.find("div", class_="_17mcb")
# product_cards = soup.find_all("div", class_="Bm3ON")

# Initialize list to store product data
product_data = []

# Loop through each product card
for card in outer_div.find_all("div", class_="Bm3ON"):
    # Get basic product info from the card
    product_div = card.find("div", class_="qmXQo")
    if not product_div:
        continue
        
    product_link = product_div.find("a")
    if not product_link:
        continue
        
    product_url = "https:" + product_link["href"] if not product_link["href"].startswith("http") else product_link["href"]
    product_title = product_div.find("div", class_="RfADt").text.strip() if product_div.find("div", class_="RfADt") else None
    product_location_div = product_div.find("div", class_="_6uN7R") if product_div else None
    product_location = product_location_div.find("span", class_="oa6ri").text.strip() if product_location_div.find("span", class_="oa6ri") else None
    
    # Get image URL
    img_div = card.find("div", class_="picture-wrapper jBwCF")
    img_url = img_div.find("img")["src"] if img_div and img_div.find("img") else None
    
    # Now visit the product page to get more details
    driver.get(product_url)
    time.sleep(3)  # Wait for page to load
    
    # Get the product page source
    product_soup = BeautifulSoup(driver.page_source, "html.parser")

    product_outer_div1 = product_soup.find("div", class_="pdp-block pdp-block__main-information")
    if product_outer_div1:
        product_outer_div2 = product_outer_div1.find("div", class_="pdp-block pdp-block__main-information-detail")
        if product_outer_div2:
            product_outer_div3 = product_outer_div2.find("div", class_="pdp-block pdp-block__product-detail")
            if product_outer_div3:
                # Get product rating count and prices
                rating_outer_div = product_outer_div3.find("div", class_="pdp-block pdp-block__rating-questions-summary")
                if rating_outer_div:
                    rating_inner_div1 = rating_outer_div.find("div", class_="pdp-block pdp-block__rating-questions")
                    if rating_inner_div1:
                        rating_inner_div2 = rating_inner_div1.find("div", class_="pdp-block module")
                        if rating_inner_div2:
                            rating_count = rating_inner_div2.find("a", class_="pdp-link pdp-link_size_s pdp-link_theme_blue pdp-review-summary__link").text.strip() if rating_inner_div2.find("a", class_="pdp-link pdp-link_size_s pdp-link_theme_blue pdp-review-summary__link") else None
                            print(f"Rating Count: {rating_count}")
                # Get Product Brand
                brand_outer_div = product_outer_div3.find("div", id="module_product_brand_1", class_="pdp-block module")
                if brand_outer_div:
                    brand_inner_div = brand_outer_div.find("div", class_="pdp-product-brand")
                    if brand_inner_div:
                        brand_name = brand_inner_div.find("a", class_="pdp-link pdp-link_size_s pdp-link_theme_blue pdp-product-brand__brand-link").text.strip() if brand_inner_div.find("a", class_="pdp-link pdp-link_size_s pdp-link_theme_blue pdp-product-brand__brand-link") else None
                        print(f"Brand Name: {brand_name}")
                # Get product prices
                prices_outer_div = product_outer_div3.find("div", id="module_product_price_1", class_="pdp-block module")
                if prices_outer_div:
                    # Get current price
                    prices_inner_div = prices_outer_div.find("div", class_="pdp-product-price")
                    current_price = prices_outer_div.find("span", class_="notranslate pdp-price pdp-price_type_normal pdp-price_color_orange pdp-price_size_xl").text.strip() if prices_inner_div and prices_inner_div.find("span", class_="notranslate pdp-price pdp-price_type_normal pdp-price_color_orange pdp-price_size_xl") else None
                    # Get original price
                    prices_inner_div2 = prices_inner_div.find("div", class_="origin-block")
                    original_price = prices_inner_div2.find("span", class_="notranslate pdp-price pdp-price_type_deleted pdp-price_color_lightgray pdp-price_size_xs").text.strip() if prices_inner_div2 and prices_inner_div2.find("span", class_="notranslate pdp-price pdp-price_type_deleted pdp-price_color_lightgray pdp-price_size_xs") else None
                    # Get discounted rate
                    discount = prices_inner_div2.find("span", class_="pdp-product-price__discount").text.strip() if prices_inner_div2 and prices_inner_div2.find("span", class_="pdp-product-price__discount") else None
                    print(f"Current Price: {current_price}, Original Price: {original_price}, Discounted Rate: {discount}")

                stats_div = product_outer_div3.find("div", id="module_sku-select", class_="pdp-block module")
                if stats_div:
                    product_stats_div1 = stats_div.find("div", class_="sku-selector")
                    if product_stats_div1:
                        sku_props = product_stats_div1.find_all("div", class_="sku-prop")
                        if len(sku_props) >= 2:
                            product_stats_div2 = sku_props[1]; # Get the second SKU prop
                            if product_stats_div2:
                                product_stats_div3 = product_stats_div2.find("div", class_="pdp-mod-product-info-section sku-prop-selection")
                                if product_stats_div3:
                                    product_stats_div4 = product_stats_div3.find("div", class_="section-content")
                                    if product_stats_div4:
                                        product_stats_div5 = product_stats_div4.find("div", class_="sku-prop-content sku-prop-content-")
                                        if product_stats_div5:
                                            sizes = []
                                            # Get all available sizes and selected size
                                            for size_item in product_stats_div5.find_all("span", class_=["sku-variable-size", "sku-variable-size-selected"]):
                                                size_text = size_item.text.strip()
                                                if size_text:
                                                    sizes.append(size_text)
                                            print(f"All available sizes: {sizes}")
                                        else:
                                            print("No Product Stats Div 5 found")
                                    else:
                                        print("No Product Stats Div 4 found")
                                else:
                                    print("No Product Stats Div 3 Text found")
                            else:
                                print("No Product Stats Div 2 found")
                        else:
                            print("Not enough SKU Props found")
                    else:
                        print("No Product Stats Div 1 found")
                else:
                    print("No Stats Div found")

    # Get product description
    description = None
    description_outer_div1 = product_soup.find("div", class_="pdp-block pdp-block__additional-information")
    description_outer_div2 = description_outer_div1.find("div", class_="pdp-block pdp-block__product-description") if description_outer_div1 else None
    description_div_1 = description_outer_div2.find("div", class_="pdp-block fixed-width-full background-2") if description_outer_div2 else None 
    description_div_2 = description_div_1.find("div", id="module_product_detail", class_="pdp-block module") if description_div_1 else None 
    description_div_3 = description_div_2.find("div", class_="lazzyload-wrapper") if description_div_2 else None  
    description_div_4 = description_div_3.find("div", class_="pdp-product-detail") if description_div_3 else None  
    description_div_5 = description_div_4.find("div", class_="pdp-product-desc") if description_div_4 else None  
    description_div_6 = description_div_5.find("div", class_="html-content pdp-product-highlights") if description_div_5 else None  
    # Find the first <li> inside the <ul> (assuming <ul> exists)
    ul_tag = description_div_6.find("ul", class_="") if description_div_6 else None 
    if ul_tag:
        print("ul_tag found")
        li_tags = ul_tag.find_all("li", class_="")
        if li_tags:
            print(f"Found {len(li_tags)} li tags")
            # Multiple <li> or just one <li> with big content?
            if len(li_tags) > 1:
                # Join all <li> texts
                description = " ".join(li.text.strip() for li in li_tags if li.text.strip())
            else:
                # Just one <li>, extract its full text
                description = li_tags[0].text.strip()
                # description = " ".join(description) if description else None
            print(f"✅ Extracted Description:\n{description}")
        else:
            print("No li tags found inside ul")
    else:
        print("ul_tag NOT found")
    
    rating_score = None
    reviews = []
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
        # First find the review section
        rating__div = driver.find_element(By.XPATH, '//*[@id="module_product_review"]/div/div/div[1]/div[2]/div/div')
        if rating__div:
            print("Rating div1 found")
            rating_div = rating__div.find_element(By.CLASS_NAME,"summary")
            if rating_div:
                print("Rating div found")
                rating_score = rating_div.find_element(By.CSS_SELECTOR, f"#module_product_review > div > div > div:nth-child(1) > div.mod-rating > div.content > div.left > div.summary > div.score > span.score-average").text
                if rating_score: 
                    print(f"Rating Score: {rating_score}")
    except Exception as e:
        print(f"Error while extracting rating: {str(e)}")
        print("Continuing with other product data...")
    
    # Append all product data
    product_data.append({
        "productUrl": product_url,
        "title": product_title,
        "brand": brand_name,
        "description": description,
        "category": "mens-shirts",
        "colors": "N/A",
        "location": product_location,
        "currentPrice": current_price,
        "discountRate": discount,
        "originalPrice": original_price,
        "imageUrl": img_url,
        "sizes": sizes,
        "ratingScore": rating_score,
        "ratingCount": rating_count,
        "reviews": reviews
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