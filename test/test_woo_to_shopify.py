import unittest
import os
import sys
import pandas as pd
import csv
import tempfile
import json
import re

# Add parent directory to path to import the main module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from woo_to_shopify import convert_woo_to_shopify

class TestWooToShopify(unittest.TestCase):
    
    def setUp(self):
        # Create a sample WooCommerce CSV for testing
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(self.test_dir)
        
        # Define test file paths
        self.woo_test_file = os.path.join(self.test_dir, 'test_woo.csv')
        self.shopify_output_file = os.path.join(self.test_dir, 'test_shopify_output.csv')
        
        # Sample WooCommerce data with various test cases
        woo_data = [
            ['title', 'vendor', 'product_type', 'tags', 'Variant Price', 'additional_image_link', 'inventory_quantity', 'handle'],
            ['Test Product', 'Test Vendor', 'Test Type', 'test,tags', '19.99', 'https://example.com/image.jpg', '10', 'test-product'],
            # Test empty fields
            ['Empty Fields Product', 'Empty Vendor', 'Empty Type', '', '29.99', '', '', 'empty-fields-product'],
            # Test special characters
            ['Special & Chars Product!', 'Special&Vendor', 'Special Type', 'special,chars,test', '39.99', 'https://example.com/special.jpg', '5', 'special-chars-product'],
            # Test numeric vs string issues
            ['Numeric Product', 'Number Vendor', 'Gaming', 'numbers', 'not-a-number', 'https://example.com/numeric.jpg', 'invalid', 'numeric-product'],
            # Test various product types for category and weight mapping
            ['Smart Home Product', 'Smart Vendor', 'Smart Home', 'smart,home', '99.99', 'https://example.com/smart.jpg', '20', 'smart-home-product'],
            ['Gaming Product', 'Gaming Vendor', 'Gaming', 'gaming', '199.99', 'https://example.com/gaming.jpg', '15', 'gaming-product'],
            ['Music Product', 'Music Vendor', 'Music', 'music', '49.99', 'https://example.com/music.jpg', '30', 'music-product']
        ]
        
        # Extended test data for more complex cases
        self.extended_test_data = [
            ['title', 'vendor', 'product_type', 'tags', 'Variant Price', 'additional_image_link', 'inventory_quantity', 'handle', 'description', 'variant_sku', 'option1_name', 'option1_value', 'option2_name', 'option2_value'],
            # Product with variants
            ['Variant Product', 'Variant Vendor', 'Clothing', 'variant,clothing', '24.99', 'https://example.com/variant.jpg', '15', 'variant-product', 'Product with variants', 'VAR-001', 'Size', 'Small', 'Color', 'Red'],
            ['', '', '', '', '24.99', '', '10', 'variant-product', '', 'VAR-002', 'Size', 'Medium', 'Color', 'Red'],
            ['', '', '', '', '24.99', '', '5', 'variant-product', '', 'VAR-003', 'Size', 'Large', 'Color', 'Red'],
            ['', '', '', '', '29.99', '', '8', 'variant-product', '', 'VAR-004', 'Size', 'Small', 'Color', 'Blue'],
            ['', '', '', '', '29.99', '', '12', 'variant-product', '', 'VAR-005', 'Size', 'Medium', 'Color', 'Blue'],
            # International pricing and decimal formats
            ['International Product', 'Global Vendor', 'International', 'global,pricing', '1,999.00', 'https://example.com/international.jpg', '100', 'international-product', 'Product with international pricing', 'INT-001', '', '', '', ''],
            # Extremely long title and description
            ['Super Extremely Long Product Title That Exceeds Normal Limits And Should Be Properly Handled During Conversion Process Without Breaking Or Causing Errors' * 2, 
             'Long Vendor', 'Misc', 'long,text', '59.99', 'https://example.com/long.jpg', '3', 'long-product', 'This is an extremely long product description that contains a lot of text and should be handled properly. ' * 20, 'LONG-001', '', '', '', ''],
            # Product with HTML in description
            ['HTML Product', 'HTML Vendor', 'Digital', 'html,formatting', '15.99', 'https://example.com/html.jpg', '999', 'html-product', '<p>This is a <strong>formatted</strong> description with <a href="https://example.com">links</a> and <em>styling</em>.</p>', 'HTML-001', '', '', '', ''],
            # Product with zero price (free)
            ['Free Product', 'Free Vendor', 'Digital', 'free,digital', '0', 'https://example.com/free.jpg', '9999', 'free-product', 'This product is free', 'FREE-001', '', '', '', ''],
            # Product with very high price
            ['Expensive Product', 'Luxury Vendor', 'Luxury', 'expensive,luxury', '9999999.99', 'https://example.com/expensive.jpg', '1', 'expensive-product', 'Very expensive product', 'EXP-001', '', '', '', ''],
            # Product with special inventory settings
            ['Backorder Product', 'Inventory Vendor', 'Misc', 'backorder,inventory', '49.99', 'https://example.com/backorder.jpg', '-5', 'backorder-product', 'Product that can be backordered', 'BACK-001', '', '', '', ''],
        ]
        
        # Create template file for schema validation test
        template_file_path = os.path.join(self.project_root, 'csv', 'input', 'product_template.csv')
        if os.path.exists(template_file_path):
            self.shopify_template = pd.read_csv(template_file_path)
        
        with open(self.woo_test_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(woo_data)
    
    def tearDown(self):
        # Clean up test files
        if os.path.exists(self.woo_test_file):
            os.remove(self.woo_test_file)
        if os.path.exists(self.shopify_output_file):
            os.remove(self.shopify_output_file)
        
        # Clean up any additional test files
        pattern = re.compile(r'test_.*\.csv')
        for file in os.listdir(self.test_dir):
            if pattern.match(file) and os.path.isfile(os.path.join(self.test_dir, file)):
                os.remove(os.path.join(self.test_dir, file))
    
    def test_conversion_creates_valid_file(self):
        # Test that conversion creates a file
        convert_woo_to_shopify(self.woo_test_file, self.shopify_output_file)
        self.assertTrue(os.path.exists(self.shopify_output_file))
    
    def test_conversion_maps_basic_fields(self):
        # Test that basic fields are mapped correctly
        convert_woo_to_shopify(self.woo_test_file, self.shopify_output_file)
        
        shopify_df = pd.read_csv(self.shopify_output_file)
        
        # Check first row values for key fields
        self.assertEqual(shopify_df.loc[0, 'Title'], 'Test Product')
        self.assertEqual(shopify_df.loc[0, 'Vendor'], 'Test Vendor')
        self.assertEqual(shopify_df.loc[0, 'Type'], 'Test Type')
        self.assertEqual(shopify_df.loc[0, 'Tags'], 'test,tags')
        self.assertEqual(shopify_df.loc[0, 'Price'], 19.99)
        self.assertEqual(shopify_df.loc[0, 'Product image URL'], 'https://example.com/image.jpg')
        self.assertEqual(shopify_df.loc[0, 'Inventory quantity'], 10)
        self.assertEqual(shopify_df.loc[0, 'URL handle'], 'test-product')
    
    def test_required_shopify_columns_exist(self):
        # Test that all required Shopify columns exist in output
        convert_woo_to_shopify(self.woo_test_file, self.shopify_output_file)
        
        shopify_df = pd.read_csv(self.shopify_output_file)
        
        required_columns = [
            'Title', 'URL handle', 'Vendor', 'Type', 'Tags', 
            'Published on online store', 'Status', 'Price', 
            'Inventory quantity', 'Product image URL', 'Weight value (grams)',
            'SEO title', 'SEO description', 'Google Shopping / Google product category'
        ]
        
        for column in required_columns:
            self.assertIn(column, shopify_df.columns)
    
    def test_empty_fields_handled(self):
        # Test that empty fields are handled correctly
        convert_woo_to_shopify(self.woo_test_file, self.shopify_output_file)
        
        # Load the CSV content
        shopify_df = pd.read_csv(self.shopify_output_file)
        
        # Check that empty tags field is properly handled (row 1 is the second row in the CSV)
        # For some values, pandas might read empty strings as NaN, so we check both
        tags_value = shopify_df.loc[1, 'Tags']
        self.assertTrue(tags_value == '' or pd.isna(tags_value))
        
        # Check that empty image URL is handled
        image_url = shopify_df.loc[1, 'Product image URL']
        self.assertTrue(image_url == '' or pd.isna(image_url))
        
        # Make sure these have default values
        self.assertEqual(shopify_df.loc[1, 'Status'], 'active')
        # Check the published value (could be 'TRUE' or True depending on how pandas loads it)
        published_value = shopify_df.loc[1, 'Published on online store']
        self.assertTrue(published_value == 'TRUE' or published_value is True or published_value == True)

    def test_special_characters_handled(self):
        # Test that special characters are preserved
        convert_woo_to_shopify(self.woo_test_file, self.shopify_output_file)
        
        shopify_df = pd.read_csv(self.shopify_output_file)
        
        # The third row has special characters
        self.assertEqual(shopify_df.loc[2, 'Title'], 'Special & Chars Product!')
        self.assertEqual(shopify_df.loc[2, 'Vendor'], 'Special&Vendor')
        self.assertEqual(shopify_df.loc[2, 'Tags'], 'special,chars,test')
        
    def test_numeric_conversion_errors_handled(self):
        # Test that numeric conversion errors are handled gracefully
        convert_woo_to_shopify(self.woo_test_file, self.shopify_output_file)
        
        shopify_df = pd.read_csv(self.shopify_output_file)
        
        # The fourth row has invalid numeric data
        # Price should be NaN, and inventory quantity should be 0 for invalid numbers
        self.assertTrue(pd.isna(shopify_df.loc[3, 'Price']))
        self.assertEqual(shopify_df.loc[3, 'Inventory quantity'], 0)
        
    def test_product_type_mapping(self):
        # Test that product type mapping works correctly for weights and categories
        convert_woo_to_shopify(self.woo_test_file, self.shopify_output_file)
        
        shopify_df = pd.read_csv(self.shopify_output_file)
        
        # Check weight assignments based on product type
        # Row 4: Smart Home
        self.assertEqual(shopify_df.loc[4, 'Weight value (grams)'], 1000)
        # Row 5: Gaming
        self.assertEqual(shopify_df.loc[5, 'Weight value (grams)'], 5000)
        # Row 6: Music
        self.assertEqual(shopify_df.loc[6, 'Weight value (grams)'], 500)
        
        # Check category assignments
        self.assertEqual(shopify_df.loc[4, 'Product category'], 'Electronics > Smart Home Automation')
        self.assertEqual(shopify_df.loc[5, 'Product category'], 'Electronics > Video Game Consoles & Accessories')
        self.assertEqual(shopify_df.loc[6, 'Product category'], 'Electronics > Audio')
    
    def test_generated_fields(self):
        # Test that SEO fields and SKUs are generated correctly
        convert_woo_to_shopify(self.woo_test_file, self.shopify_output_file)
        
        shopify_df = pd.read_csv(self.shopify_output_file)
        
        # Check SEO title and description generation
        self.assertEqual(shopify_df.loc[0, 'SEO title'], 'Test Product - Buy Online')
        # Check that description contains the expected text
        seo_description = shopify_df.loc[0, 'SEO description']
        self.assertTrue('Shop Test Product' in str(seo_description))
        
        # Check SKU generation
        self.assertEqual(shopify_df.loc[0, 'SKU'], 'testproduc-sku')
    
    def test_complex_data_variants(self):
        """Test handling of product variants and more complex data structures"""
        # Create a more complex test file
        complex_test_file = os.path.join(self.test_dir, 'test_complex_woo.csv')
        complex_output_file = os.path.join(self.test_dir, 'test_complex_shopify.csv')
        
        with open(complex_test_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(self.extended_test_data)
        
        # Convert the complex file
        convert_woo_to_shopify(complex_test_file, complex_output_file)
        
        # Verify the file was created
        self.assertTrue(os.path.exists(complex_output_file))
        
        # Load and check results
        shopify_df = pd.read_csv(complex_output_file)
        
        # Test variant product title (first row is header, second row is first data row)
        self.assertEqual(shopify_df.loc[0, 'Title'], 'Variant Product')
        
        # Test handling of zero price
        free_product_index = 8  # 0-indexed, 9th row in extended data (8th data row)
        self.assertEqual(shopify_df.loc[8, 'Title'], 'Free Product')
        self.assertEqual(shopify_df.loc[8, 'Price'], 0)
        
        # Test handling of very high price
        expensive_product_index = 9
        self.assertEqual(shopify_df.loc[9, 'Title'], 'Expensive Product')
        self.assertEqual(shopify_df.loc[9, 'Price'], 9999999.99)
        
        # Clean up
        if os.path.exists(complex_test_file):
            os.remove(complex_test_file)
        if os.path.exists(complex_output_file):
            os.remove(complex_output_file)
    
    def test_long_text_fields(self):
        """Test handling of extremely long text fields"""
        # Create a test file with long text
        long_text_file = os.path.join(self.test_dir, 'test_long_text.csv')
        long_text_output = os.path.join(self.test_dir, 'test_long_text_output.csv')
        
        # Extract the long text product data (7th item in extended test data)
        long_text_data = [self.extended_test_data[0], self.extended_test_data[7]]
        
        with open(long_text_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(long_text_data)
        
        # Convert the file
        convert_woo_to_shopify(long_text_file, long_text_output)
        
        # Verify the file was created
        self.assertTrue(os.path.exists(long_text_output))
        
        # Load and check results
        shopify_df = pd.read_csv(long_text_output)
        
        # Just verify that the conversion completed successfully
        # and that the Title column exists in the output
        self.assertIn('Title', shopify_df.columns)
        
        # Clean up
        if os.path.exists(long_text_file):
            os.remove(long_text_file)
        if os.path.exists(long_text_output):
            os.remove(long_text_output)
    
    def test_boolean_values_consistency(self):
        """Test that boolean values are consistently formatted"""
        convert_woo_to_shopify(self.woo_test_file, self.shopify_output_file)
        
        # Read the CSV as text to check the actual string values
        with open(self.shopify_output_file, 'r') as f:
            csv_content = f.read()
        
        # Check that TRUE appears in the file (not True or other variations)
        self.assertIn('TRUE', csv_content)
        self.assertIn('FALSE', csv_content)
        
        # Confirm boolean columns have consistent formatting
        shopify_df = pd.read_csv(self.shopify_output_file)
        boolean_columns = ['Published on online store', 'Charge tax', 'Requires shipping', 'Gift card']
        
        for col in boolean_columns:
            # All values should be either 'TRUE' or 'FALSE' (pandas may load them as True/False, but we'll convert them to strings for comparison)
            for idx, val in enumerate(shopify_df[col]):
                val_str = str(val).upper()
                self.assertTrue(val_str in ['TRUE', 'FALSE'], f"Value {val} in column {col} at row {idx} is not 'TRUE' or 'FALSE'")
    
    def test_schema_validation(self):
        """Test that the output conforms to the Shopify product import schema"""
        # Skip this test if the template file wasn't found
        if not hasattr(self, 'shopify_template'):
            self.skipTest("Shopify template file not found")
        
        convert_woo_to_shopify(self.woo_test_file, self.shopify_output_file)
        shopify_df = pd.read_csv(self.shopify_output_file)
        
        # Check that all columns in the template are in the output
        template_columns = set(self.shopify_template.columns)
        output_columns = set(shopify_df.columns)
        
        # All template columns should be in the output
        missing_columns = template_columns - output_columns
        self.assertEqual(len(missing_columns), 0, f"Missing columns: {missing_columns}")
    
    def test_data_integrity(self):
        """Test that the data integrity is maintained during conversion"""
        convert_woo_to_shopify(self.woo_test_file, self.shopify_output_file)
        
        shopify_df = pd.read_csv(self.shopify_output_file)
        woo_df = pd.read_csv(self.woo_test_file)
        
        # Check that the row count is the same
        self.assertEqual(len(shopify_df), len(woo_df))
        
        # Check that key fields are transferred correctly
        for i in range(len(woo_df)):
            self.assertEqual(shopify_df.loc[i, 'Title'], woo_df.loc[i, 'title'])
            self.assertEqual(shopify_df.loc[i, 'Vendor'], woo_df.loc[i, 'vendor'])
            self.assertEqual(shopify_df.loc[i, 'Type'], woo_df.loc[i, 'product_type'])
            # URL handle should match the handle field
            self.assertEqual(shopify_df.loc[i, 'URL handle'], woo_df.loc[i, 'handle'])
    
    def test_negative_inventory(self):
        """Test handling of negative inventory values"""
        # Create a test file with negative inventory
        neg_inv_file = os.path.join(self.test_dir, 'test_neg_inv.csv')
        neg_inv_output = os.path.join(self.test_dir, 'test_neg_inv_output.csv')
        
        # Create test data with negative inventory
        neg_inv_data = [
            ['title', 'vendor', 'product_type', 'tags', 'Variant Price', 'additional_image_link', 'inventory_quantity', 'handle'],
            ['Negative Inventory Product', 'Test Vendor', 'Test Type', 'test', '19.99', 'https://example.com/image.jpg', '-10', 'neg-inv-product']
        ]
        
        with open(neg_inv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(neg_inv_data)
        
        # Convert the file
        convert_woo_to_shopify(neg_inv_file, neg_inv_output)
        
        # Verify the file was created
        self.assertTrue(os.path.exists(neg_inv_output))
        
        # Load and check results
        shopify_df = pd.read_csv(neg_inv_output)
        
        # Confirm negative inventory was handled properly
        # Should be preserved (some systems allow negative inventory for backorders)
        self.assertEqual(shopify_df.loc[0, 'Inventory quantity'], -10)
        
        # Clean up
        if os.path.exists(neg_inv_file):
            os.remove(neg_inv_file)
        if os.path.exists(neg_inv_output):
            os.remove(neg_inv_output)
    
    def test_multiple_runs_idempotence(self):
        """Test that running the conversion multiple times produces consistent results"""
        # First run
        convert_woo_to_shopify(self.woo_test_file, self.shopify_output_file)
        first_run_df = pd.read_csv(self.shopify_output_file)
        
        # Second run to a different file
        second_output_file = os.path.join(self.test_dir, 'test_shopify_output_second.csv')
        convert_woo_to_shopify(self.woo_test_file, second_output_file)
        second_run_df = pd.read_csv(second_output_file)
        
        # Check that both runs produced identical results
        pd.testing.assert_frame_equal(first_run_df, second_run_df)
        
        # Clean up
        if os.path.exists(second_output_file):
            os.remove(second_output_file)
    
    def test_real_woo_data_conversion(self):
        # Test with the actual woo.csv file if it exists
        woo_csv_path = os.path.join(self.project_root, 'csv', 'input', 'woo.csv')
        shopify_output_path = os.path.join(self.project_root, 'csv', 'output', 'test_shopify_output.csv')
        
        if os.path.exists(woo_csv_path):
            convert_woo_to_shopify(woo_csv_path, shopify_output_path)
            self.assertTrue(os.path.exists(shopify_output_path))
            
            # Test a few real conversions
            shopify_df = pd.read_csv(shopify_output_path)
            woo_df = pd.read_csv(woo_csv_path)
            
            # Check that row counts match
            self.assertEqual(len(shopify_df), len(woo_df))
            
            # Perform additional validation on real data:
            
            # 1. Check that handles exist (not checking uniqueness as real data might have duplicates)
            self.assertEqual(shopify_df['URL handle'].isna().sum(), 0)
            
            # 2. Check that all products have titles
            self.assertEqual(shopify_df['Title'].isna().sum(), 0)
            
            # 3. Check that all products have SEO titles and descriptions
            self.assertEqual(shopify_df['SEO title'].isna().sum(), 0)
            self.assertEqual(shopify_df['SEO description'].isna().sum(), 0)
            
            # 4. Check that all products have assigned weights
            self.assertEqual((shopify_df['Weight value (grams)'] <= 0).sum(), 0)
            
            # 5. Check that all boolean fields are properly formatted (as strings or Python booleans)
            boolean_columns = ['Published on online store', 'Charge tax', 'Requires shipping', 'Gift card']
            for col in boolean_columns:
                for val in shopify_df[col]:
                    val_str = str(val).upper()
                    self.assertTrue(val_str in ['TRUE', 'FALSE'], 
                        f"Found invalid boolean value: {val} in column {col}")
            
            # Clean up this test file
            if os.path.exists(shopify_output_path):
                os.remove(shopify_output_path)

if __name__ == '__main__':
    unittest.main() 