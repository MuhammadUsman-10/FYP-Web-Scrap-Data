import time
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

driver = webdriver.Edge()
url='https://www.daraz.pk/products/white-black-markhor-printed-for-men-boys-soft-comfy-fabric-summer-printed-i471459201-s2223947046.html?c=&channelLpJumpArgs=&clickTrackInfo=query%253A%253Bnid%253A471459201%253Bsrc%253ALazadaMainSrp%253Brn%253A5491cbcf2fc1fe2ff5a0c2bbe5113537%253Bregion%253Apk%253Bsku%253A471459201_PK%253Bprice%253A649%253Bclient%253Adesktop%253Bsupplier_id%253A6005047944044%253Bbiz_source%253Ah5_external%253Bslot%253A0%253Butlog_bucket_id%253A470687%253Basc_category_id%253A4195%253Bitem_id%253A471459201%253Bsku_id%253A2223947046%253Bshop_id%253A1170895%253BtemplateInfo%253A1104_L%2523-1_A3_C%2523&freeshipping=0&fs_ab=1&fuse_fs=&lang=en&location=Punjab&price=649&priceCompare=skuId%3A2223947046%3Bsource%3Alazada-search-voucher%3Bsn%3A5491cbcf2fc1fe2ff5a0c2bbe5113537%3BoriginPrice%3A64900%3BdisplayPrice%3A64900%3BsinglePromotionId%3A50000026052007%3BsingleToolCode%3AflashSale%3BvoucherPricePlugin%3A0%3Btimestamp%3A1747337066254&ratingscore=4.396711202466598&request_id=5491cbcf2fc1fe2ff5a0c2bbe5113537&review=973&sale=7564&search=1&source=search&spm=a2a0e.searchlistcategory.list.0&stock=1'

driver.get(url)

temp = dict()
temp['Review text'] = []

#scrolling down the page to load reviews
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

#looping through review pages
for page in range(15,30):
    try:
        # Finding the container for reviews
        reviews_container = driver.find_element(By.XPATH, '//*[@id="module_product_review"]/div/div/div[3]/div[1]')
    except NoSuchElementException:
        print('No Reviews')
        break
        #finding all individual reviews on the current page
    reviews = reviews_container.find_elements(By.CLASS_NAME,'item')

    #looping through each review on the current page
    for i in range(len(reviews)):
        #checking if the review text is not empty
        if reviews[i].find_element(By.CSS_SELECTOR, f"#module_product_review > div > div > div:nth-child(3) > div.mod-reviews > div:nth-child({i+1}) > div.item-content > div.content").text != '':
            #extracting and appending review text
            temp['Review text'].append(reviews[i].find_element(By.CSS_SELECTOR, f"#module_product_review > div > div > div:nth-child(3) > div.mod-reviews > div:nth-child({i+1}) > div.item-content > div.content").text)
    try:
        #clicking the next button if it exists and not on the third page
        if(page != 2):
            nxt_button = driver.find_element(By.XPATH, '//*[@id="module_product_review"]/div/div/div[3]/div[2]/div/button[2]')
            driver.execute_script("arguments[0].click();", nxt_button)
            time.sleep(5)
    except NoSuchElementException:
        print('No More Pages')
        break
#converting to dataframe
reviews = pd.DataFrame(temp)
reviews.to_csv('reviews.csv')
reviews