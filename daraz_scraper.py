from selenium import webdriver
from selenium.webdriver.common.by import By
from openpyxl.workbook import Workbook
from bs4 import BeautifulSoup
import pandas as pd
import time
from pymongo import MongoClient

# Set up Selenium WebDriver
driver = webdriver.Edge()

# Define the URL
url = "https://www.daraz.pk/mens-clothing/"
driver.get(url)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")

db = client["Web-Scraping"]
collection = db["daraz_products"]

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
    # product_title = product_link.text.strip()
    
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
        print("Product Outer Div 1 found")
        product_outer_div2 = product_outer_div1.find("div", class_="pdp-block pdp-block__main-information-detail")
        if product_outer_div2:
            print("Product Outer Div 2 found")
            product_outer_div3 = product_outer_div2.find("div", class_="pdp-block pdp-block__product-detail")
            if product_outer_div3:
                print("Product Outer Div 3 found")
                # Get product stats
                prices_outer_div = product_outer_div3.find("div", id="module_product_price_1", class_="pdp-block module")
                if prices_outer_div:
                    print("Prices Outer Div found")
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
                    print("Stats Div found")
                    product_stats_div1 = stats_div.find("div", class_="sku-selector")
                    if product_stats_div1:
                        print("Product Stats Div 1 found")
                        sku_props = product_stats_div1.find_all("div", class_="sku-prop")
                        if len(sku_props) >= 2:
                            print("Multiple SKU Props found")
                            # Get product stats
                            product_stats_div2 = sku_props[1]; # Get the second SKU prop
                            print("SKU Props Div 2 found")
                            if product_stats_div2:
                                print("Product Stats Div 2 found")
                                # Get product stats
                                product_stats_div3 = product_stats_div2.find("div", class_="pdp-mod-product-info-section sku-prop-selection")
                                if product_stats_div3:
                                    print("Product Stats Div 3 found")
                                    # Get product stats
                                    product_stats_div4 = product_stats_div3.find("div", class_="section-content")
                                    if product_stats_div4:
                                        print("Product Stats Div4 found")
                                        # Get product stats text
                                        product_stats_div5 = product_stats_div4.find("div", class_="sku-prop-content sku-prop-content-")
                                        if product_stats_div5:
                                            print("Product Stats Div5 found")
                                            # Initialize empty list for sizes
                                            sizes = []
                                            # Get all available sizes and selected size
                                            for size_item in product_stats_div5.find_all("span", class_=["sku-variable-size", "sku-variable-size-selected"]):
                                                size_text = size_item.text.strip()
                                                if size_text:
                                                    print(f"Found size: {size_text}")
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
    description_outer_div1 = product_soup.find("div", class_="pdp-block pdp-block__additional-information")
    description_outer_div2 = description_outer_div1.find("div", class_="pdp-block pdp-block__product-description")
    description_div = description_outer_div2.find("div", class_="pdp-block fixed-width-full background-2")
    description = description_div.text.strip() if description_div else None
    
    # Get rating & reviews
    rating_score = None
    rating_count = None
    reviews = []
    
    try:
        # First find the review section
        review_outer_div1 = description_outer_div2.find("div", class_="pdp-block fixed-width-full block-margin-top background-2")
        if review_outer_div1:
            print("Review Outer Div 1 found")
            review_outer_div2 = review_outer_div1.find("div", id="module_product_review", class_="pdp-block module")

            if review_outer_div2:
                print("Review Outer Div 2 found")
                review_outer_div3 = review_outer_div2.find("div", class_="lazyload-wrapper")

                if review_outer_div3:
                    print("Review Outer Div 3 found")
                    review_outer_div4 = review_outer_div3.find("div", lazada_pdp_review="expose", itemid="391702503", class_="pdp-mod-review")
                    print("Review Outer Div 4 searching")
                    print(review_outer_div4)

                    if review_outer_div4:
                        print("Review Outer Div 4 found")
                        divs = review_outer_div4.find_all("div")

                        if len(divs) >= 3:
                            print("Multiple Divs found")
                            # Get rating information
                            rating_outer_div = divs[1]

                            if rating_outer_div:
                                print("Rating Outer Div found")
                                rating_div = rating_outer_div.find("div", class_="mod-rating")

                                if rating_div:
                                    print("Rating Div found")
                                    # Get rating score and count
                                    rating_score = rating_div.find("span", class_="score-average").text.strip() if rating_div.find("span", class_="score-average") else None
                                    rating_count = rating_div.find("div", class_="count").text.strip() if rating_div.find("div", class_="count") else None
    except Exception as e:
        print(f"Error while extracting reviews: {str(e)}")
        print("Continuing with other product data...")
    
    # Append all product data
    product_data.append({
        "Product URL": product_url,
        "Title": product_title,
        "Description": description,
        "Current Price": current_price,
        "Discount Rate": discount,
        "Original Price": original_price,
        "Image URL": img_url,
        "Sizes": sizes,
        "Rating Score": rating_score,
        "Rating Count": rating_count,
        "Reviews": reviews
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

# Save to Excel
df = pd.DataFrame(product_data)
df.to_excel("daraz_products.xlsx", index=False)
print("Data saved to daraz_products.xlsx") 