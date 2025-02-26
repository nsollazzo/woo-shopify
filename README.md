# WooCommerce to Shopify CSV Converter

This utility converts WooCommerce product CSV exports to Shopify's product import CSV format, making it easy to migrate your products from WooCommerce to Shopify.

## Directory Structure

```
woo-shopify/
├── csv/
│   ├── input/
│   │   ├── product_template.csv  # Shopify template file
│   │   └── woo.csv               # WooCommerce product data
│   └── output/
│       └── shopify_result.csv    # Converted Shopify format
├── test/
│   └── test_woo_to_shopify.py    # Comprehensive test suite
├── woo_to_shopify.py             # Main converter script
├── requirements.txt              # Dependencies
└── README.md                     # This file
```

## Features

- Converts basic product information (title, vendor, price, etc.)
- Handles empty fields and special characters
- Automatically generates SKUs based on product handles
- Maps product types to appropriate categories
- Assigns reasonable default weights based on product types
- Generates SEO titles and descriptions
- Sets up proper Google Shopping feed parameters
- Preserves complex data including variants and long text
- Properly handles negative inventory, decimal formats, and high price values
- Creates valid output that conforms to Shopify's import schema

## Requirements

- Python 3.6+
- Pandas
- NumPy

Install the required dependencies with:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python woo_to_shopify.py
```

This will convert the default input file (`csv/input/woo.csv`) and create a file called `csv/output/shopify_output.csv` with the converted products.

### Advanced Options

```bash
python woo_to_shopify.py --input csv/input/custom_woo.csv --output csv/output/custom_shopify.csv --verbose
```

- `--input` or `-i`: Specify a custom input filename (default: csv/input/woo.csv)
- `--output` or `-o`: Specify a custom output filename (default: csv/output/shopify_output.csv)
- `--verbose` or `-v`: Print progress information during conversion

## WooCommerce CSV Format

The converter expects a WooCommerce CSV with at least the following columns:

- `title` - Product title
- `vendor` - Vendor/manufacturer name
- `product_type` - Type of product
- `tags` - Product tags (comma-separated)
- `Variant Price` - Product price
- `additional_image_link` - URL to the product image
- `inventory_quantity` - Stock quantity
- `handle` - URL handle/slug

## Shopify Import Process

After generating the Shopify CSV:

1. Go to your Shopify admin panel
2. Navigate to Products > All Products
3. Click Import > Add file
4. Select your converted CSV file
5. Click Upload and import

## Testing

The converter includes a comprehensive test suite that verifies correct behavior in various scenarios:

```bash
python test/test_woo_to_shopify.py
```

The tests cover:
- Basic field mapping
- Empty fields handling
- Special characters preservation
- Numeric conversion handling (including invalid values)
- Product type mapping (weights and categories)
- Generated fields (SKUs, SEO titles, descriptions)
- Complex data structures (product variants)
- Long text fields
- Boolean value consistency
- Schema validation against Shopify's template
- Data integrity verification
- Negative inventory handling
- Process idempotence (consistent results across multiple runs)
- Real data conversion

## Customization

You can modify the `woo_to_shopify.py` file to customize:

- Default values for fields
- Weight assignments based on product types
- Category mappings
- SEO templates
- And more

Look for the appropriate sections in the code and adjust as needed for your specific product catalog.

## License

MIT 