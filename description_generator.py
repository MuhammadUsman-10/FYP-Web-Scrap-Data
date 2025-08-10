import os
import openai
from pymongo import MongoClient
from dotenv import load_dotenv
import time
import json

# Load environment variables from .env file
load_dotenv()


# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# MongoDB connection
# Get MongoDB URI from environment variable, fallback to localhost if not set
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)  # Use environment variable for MongoDB connection
db = client["ShopSmart-Fyp"]
collection = db["products"]

def generate_product_description(title, category):
    """
    Generate a product description using GPT based on title and category
    """
    try:
        prompt = f"""
        Generate a realistic and minimal product description for the following product:
        
        Product Title: {title}
        Category: {category}
        
        Requirements:
        - Keep it concise (3-4 sentences)
        - Make it realistic and believable
        - Focus on key features and benefits
        - Use natural, marketing-friendly language
        - Don't be overly promotional
        - Include relevant details based on the title and category
        - Also can include any unique selling points or features or points that make the product stand out (3-4 points) other than that 1st paragraph of 3-4 sentences.
        - Avoid Starting with "Elevate your" instaed start with some realistic approach for every product
        
        Generate only the description text, nothing else.
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional product description writer. Generate concise, realistic product descriptions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        description = response.choices[0].message.content.strip()
        return description
        
    except Exception as e:
        print(f"Error generating description: {str(e)}")
        return None

def get_products_without_description():
    """
    Fetch products that have no description or empty description
    """
    try:
        # Find products where description is null, empty, or doesn't exist
        products = list(collection.find({
            "$or": [
                {"description": {"$exists": False}},
                {"description": None},
                {"description": ""},
                {"description": "N/A"},
                {"description": {"$regex": "^\\s*$"}}  # Only whitespace
            ]
        }))
        
        print(f"Found {len(products)} products without descriptions")
        return products
        
    except Exception as e:
        print(f"Error fetching products: {str(e)}")
        return []

def update_product_description(product_id, description):
    """
    Update the product with the generated description
    """
    try:
        result = collection.update_one(
            {"_id": product_id},
            {"$set": {"description": description}}
        )
        
        if result.modified_count > 0:
            print(f"✅ Successfully updated product {product_id}")
            return True
        else:
            print(f"❌ Failed to update product {product_id}")
            return False
            
    except Exception as e:
        print(f"Error updating product {product_id}: {str(e)}")
        return False

def main():
    """
    Main function to process products without descriptions
    """
    print("🚀 Starting product description generation...")
    
    # Get products without descriptions
    products = get_products_without_description()
    
    if not products:
        print("No products found without descriptions!")
        return
    
    print(f"Processing {len(products)} products...")
    
    success_count = 0
    error_count = 0
    
    for i, product in enumerate(products, 1):
        product_id = product["_id"]
        title = product.get("title", "Unknown Product")
        category = product.get("category", "General")
        
        print(f"\n[{i}/{len(products)}] Processing: {title}")
        print(f"Category: {category}")
        
        # Generate description
        description = generate_product_description(title, category)
        
        if description:
            print(f"Generated description: {description}")
            
            # Update the product in database
            if update_product_description(product_id, description):
                success_count += 1
            else:
                error_count += 1
        else:
            print("❌ Failed to generate description")
            error_count += 1
        
        # Add a small delay to avoid rate limiting
        time.sleep(1)
    
    print(f"\n🎉 Processing complete!")
    print(f"✅ Successfully updated: {success_count} products")
    print(f"❌ Errors: {error_count} products")
    print(f"📊 Total processed: {len(products)} products")

if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable is not set!")
        print("Please set your OpenAI API key in the .env file")
        exit(1)
    
    main() 