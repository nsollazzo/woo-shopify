import pandas as pd
import numpy as np
import argparse
import os

def convert_woo_to_shopify(woo_csv_path, shopify_csv_path):
    """
    Convert a WooCommerce CSV file to Shopify CSV format.
    
    Args:
        woo_csv_path (str): Path to the WooCommerce CSV file
        shopify_csv_path (str): Path to save the converted Shopify CSV file
    """
    # Load WooCommerce data
    woo_df = pd.read_csv(woo_csv_path)
    
    # Handle NaN values in the input data to avoid issues
    woo_df = woo_df.fillna('')
    
    # Create an empty Shopify dataframe with all required columns
    shopify_columns = [
        'Title', 'URL handle', 'Description', 'Vendor', 'Product category', 
        'Type', 'Tags', 'Published on online store', 'Status', 'SKU', 
        'Barcode', 'Option1 name', 'Option1 value', 'Option2 name', 
        'Option2 value', 'Option3 name', 'Option3 value', 'Price', 
        'Price / International', 'Compare-at price', 'Compare-at price / International', 
        'Cost per item', 'Charge tax', 'Tax code', 'Inventory tracker', 
        'Inventory quantity', 'Continue selling when out of stock', 
        'Weight value (grams)', 'Weight unit for display', 'Requires shipping', 
        'Fulfillment service', 'Product image URL', 'Image position', 
        'Image alt text', 'Variant image URL', 'Gift card', 'SEO title', 
        'SEO description', 'Google Shopping / Google product category', 
        'Google Shopping / Gender', 'Google Shopping / Age group', 
        'Google Shopping / MPN', 'Google Shopping / AdWords Grouping', 
        'Google Shopping / AdWords labels', 'Google Shopping / Condition', 
        'Google Shopping / Custom product', 'Google Shopping / Custom label 0', 
        'Google Shopping / Custom label 1', 'Google Shopping / Custom label 2', 
        'Google Shopping / Custom label 3', 'Google Shopping / Custom label 4'
    ]
    
    # Initialize an empty dataframe with the correct number of rows
    shopify_df = pd.DataFrame(index=range(len(woo_df)), columns=shopify_columns)
    
    # Set default values for required fields - ensuring string capitalization for booleans
    shopify_df['Published on online store'] = 'TRUE'
    shopify_df['Status'] = 'active'
    shopify_df['Charge tax'] = 'TRUE'
    shopify_df['Requires shipping'] = 'TRUE'
    shopify_df['Continue selling when out of stock'] = 'deny'
    shopify_df['Weight unit for display'] = 'g'
    shopify_df['Fulfillment service'] = 'manual'
    shopify_df['Image position'] = 1
    shopify_df['Gift card'] = 'FALSE'
    
    # Map WooCommerce fields to Shopify fields
    shopify_df['Title'] = woo_df['title']
    shopify_df['URL handle'] = woo_df['handle']
    shopify_df['Vendor'] = woo_df['vendor']
    shopify_df['Type'] = woo_df['product_type']
    
    # Handle tags - ensure they're strings, not NaN
    shopify_df['Tags'] = woo_df['tags']
    
    # Convert price from string to float, handle any formatting issues
    shopify_df['Price'] = pd.to_numeric(woo_df['Variant Price'], errors='coerce')
    
    # Convert inventory quantity from string to integer, handle any formatting issues
    shopify_df['Inventory quantity'] = pd.to_numeric(woo_df['inventory_quantity'], errors='coerce').fillna(0).astype(int)
    
    # Set product image URL
    shopify_df['Product image URL'] = woo_df['additional_image_link']
    
    # Set a default weight based on product type
    # You might want to adjust these values based on your products
    def assign_weight(product_type):
        product_type = str(product_type).lower()
        if 'gaming' in product_type:
            return 5000  # Gaming products are heavier
        elif 'smart home' in product_type:
            return 1000  # Smart home products medium weight
        elif 'music' in product_type or 'hi-tech' in product_type:
            return 500   # Smaller tech items
        else:
            return 1500  # Default weight
    
    shopify_df['Weight value (grams)'] = woo_df['product_type'].apply(assign_weight)
    
    # Generate SKUs based on handle if they don't exist
    shopify_df['SKU'] = woo_df['handle'].apply(lambda x: f"{x.replace('-', '')[:10]}-sku")
    
    # Set SEO titles and descriptions based on product names
    shopify_df['SEO title'] = woo_df['title'].apply(lambda x: f"{x} - Buy Online")
    shopify_df['SEO description'] = woo_df['title'].apply(lambda x: f"Shop {x} at our store. Quality products with fast shipping and excellent customer service.")
    
    # Assign appropriate product category based on product type
    def assign_category(product_type):
        product_type = str(product_type).lower()
        if 'gaming' in product_type:
            return 'Electronics > Video Game Consoles & Accessories'
        elif 'smart home' in product_type:
            return 'Electronics > Smart Home Automation'
        elif 'outdoor' in product_type:
            return 'Sports & Outdoors > Outdoor Recreation'
        elif 'music' in product_type:
            return 'Electronics > Audio'
        else:
            return 'Electronics > Gadgets'
    
    shopify_df['Product category'] = woo_df['product_type'].apply(assign_category)
    shopify_df['Google Shopping / Google product category'] = shopify_df['Product category']
    
    # Set default Google Shopping values
    shopify_df['Google Shopping / Gender'] = 'Unisex'
    shopify_df['Google Shopping / Age group'] = 'Adult'
    shopify_df['Google Shopping / Condition'] = 'new'
    
    # Fill NaN values with empty strings to avoid errors in CSV
    shopify_df = shopify_df.fillna('')
    
    # Save to CSV - using string boolean representations
    # Ensure boolean-like columns are saved as 'TRUE'/'FALSE' strings
    for column in ['Published on online store', 'Charge tax', 'Requires shipping', 'Gift card']:
        shopify_df[column] = shopify_df[column].apply(lambda x: 'TRUE' if str(x).lower() in ('true', 't', 'yes', 'y', '1') else 'FALSE')
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(shopify_csv_path), exist_ok=True)
    
    shopify_df.to_csv(shopify_csv_path, index=False)
    
    return shopify_df

def main():
    """
    Main function to handle command line arguments and execute the conversion.
    """
    parser = argparse.ArgumentParser(description='Convert WooCommerce CSV to Shopify CSV format')
    parser.add_argument('--input', '-i', default='csv/input/woo.csv',
                        help='Path to the WooCommerce CSV file (default: csv/input/woo.csv)')
    parser.add_argument('--output', '-o', default='csv/output/shopify_output.csv', 
                        help='Path to save the converted Shopify CSV file (default: csv/output/shopify_output.csv)')
    parser.add_argument('--verbose', '-v', action='store_true', 
                        help='Print verbose output')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found")
        return 1
    
    try:
        if args.verbose:
            print(f"Converting '{args.input}' to Shopify format...")
        
        # Perform the conversion
        result_df = convert_woo_to_shopify(args.input, args.output)
        
        if args.verbose:
            print(f"Conversion complete! Output saved to '{args.output}'")
            print(f"Converted {len(result_df)} products")
        
        return 0
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main()) 