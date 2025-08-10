# Product Description Generator

This script automatically generates product descriptions for products that don't have descriptions in your MongoDB database using OpenAI's GPT model.

## Features

- Fetches products with no description from MongoDB
- Generates realistic, minimal product descriptions using GPT-3.5-turbo
- Updates the database with generated descriptions
- Provides progress tracking and error handling
- Rate limiting to avoid API limits

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure OpenAI API Key**
   - Create a `.env` file in the project root
   - Add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

3. **Ensure MongoDB is Running**
   - Make sure MongoDB is running on `localhost:27017`
   - The script connects to database `ShopSMart` and collection `products`

## Usage

Run the script:
```bash
python description_generator.py
```

## How it Works

1. **Finds Products**: Queries MongoDB for products with:
   - No description field
   - Null description
   - Empty description
   - Description with only whitespace

2. **Generates Descriptions**: For each product:
   - Uses the product title and category
   - Sends a prompt to GPT-3.5-turbo
   - Generates a concise, realistic description (2-3 sentences)

3. **Updates Database**: Saves the generated description back to MongoDB

4. **Progress Tracking**: Shows:
   - Number of products found
   - Current progress
   - Success/error counts
   - Final summary

## Example Output

```
🚀 Starting product description generation...
Found 15 products without descriptions
Processing 15 products...

[1/15] Processing: Women's Running Shoes
Category: womens-shoes
Generated description: These comfortable running shoes feature a lightweight design with excellent cushioning for daily workouts. The breathable mesh upper provides ventilation while the durable rubber outsole offers reliable traction on various surfaces.
✅ Successfully updated product 507f1f77bcf86cd799439011

[2/15] Processing: Casual Sneakers
Category: womens-shoes
Generated description: Perfect for everyday wear, these casual sneakers combine style and comfort. The soft fabric upper and cushioned insole provide all-day comfort while the classic design complements any casual outfit.
✅ Successfully updated product 507f1f77bcf86cd799439012

🎉 Processing complete!
✅ Successfully updated: 15 products
❌ Errors: 0 products
📊 Total processed: 15 products
```

## Configuration

You can modify the script to:
- Change the GPT model (currently `gpt-3.5-turbo`)
- Adjust description length (currently 150 max tokens)
- Modify the prompt for different description styles
- Change the delay between API calls (currently 1 second)

## Error Handling

The script handles:
- Missing OpenAI API key
- Network errors
- API rate limits
- Database connection issues
- Invalid product data

## Requirements

- Python 3.7+
- OpenAI API key
- MongoDB running locally
- Internet connection for API calls

## Dependencies

- `openai` - OpenAI API client
- `pymongo` - MongoDB client
- `python-dotenv` - Environment variable management 