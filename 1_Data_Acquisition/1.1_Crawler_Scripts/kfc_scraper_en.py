import requests
from bs4 import BeautifulSoup
import time
import json
import csv
from urllib.parse import urljoin
import re
import traceback

class KFCProductScraper:
    def __init__(self):
        self.base_url = "https://www.kfc.co.uk"
        # Menu page as entry point
        self.menu_url = "https://www.kfc.co.uk/our-menu" 
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.all_products = [] # For storing final results
    
    # --- I. Menu and Category Scraping ---

    def get_categories(self):
        """Get all menu categories"""
        print("Fetching KFC menu categories...")
        try:
            response = self.session.get(self.menu_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            categories = []
            
            # Find category links from HTML - based on provided HTML structure
            # Find div elements containing categories
            category_sections = soup.find_all('div', class_='sc-501ccdbf-0')
            
            for section in category_sections:
                # Find category links
                category_link = section.find('a')
                if category_link and category_link.get('href'):
                    # Extract category name from link
                    href = category_link['href']
                    if href.startswith('/our-menu/'):
                        category_name = href.split('/')[-1].replace('-', ' ').title()
                        category_url = urljoin(self.base_url, href)
                        categories.append({
                            'name': category_name,
                            'url': category_url,
                        })
            
            # If no categories found, try to extract from JSON data
            if not categories:
                script_data = soup.find('script', id='__NEXT_DATA__')
                if script_data:
                    json_data = json.loads(script_data.string)
                    # Parse JSON to get category information
                    categories = self._extract_categories_from_json(json_data)
            
            print(f"Found {len(categories)} categories")
            return categories
            
        except Exception as e:
            print(f"Error fetching categories: {e}")
            traceback.print_exc()
            return []
    
    def _extract_categories_from_json(self, json_data):
        """Extract category information from JSON data"""
        categories = []
        try:
            # Based on provided HTML structure, category info might be in pageProps.data.mainContent
            main_content = json_data.get('props', {}).get('pageProps', {}).get('data', {}).get('mainContent', [])
            
            for content in main_content:
                if content.get('id') == 'four_column_cta':
                    children = content.get('data', {}).get('children', {})
                    # Check four columns
                    for col_key in ['first_column', 'second_column', 'third_column', 'forth_column']:
                        col_data = children.get(col_key, {})
                        button_link = col_data.get('button_link')
                        if button_link and button_link.startswith('/our-menu/'):
                            category_name = button_link.split('/')[-1].replace('-', ' ').title()
                            category_url = urljoin(self.base_url, button_link)
                            categories.append({
                                'name': category_name,
                                'url': category_url,
                            })
            
        except Exception as e:
            print(f"Error extracting categories from JSON: {e}")
        
        return categories

    def get_products_from_category(self, category_url, category_name):
        """Get all product links and names from category page"""
        print(f"Fetching products from category '{category_name}'...")
        try:
            response = self.session.get(category_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            products = []
            
            # Method 1: Find product links from HTML
            product_links = soup.find_all('a', href=re.compile(r'/our-menu/'))
            
            for link in product_links:
                href = link.get('href', '')
                # Filter out product page links (usually deeper than category links)
                if href and '/our-menu/' in href and href != category_url.replace(self.base_url, ''):
                    # Check if it's a product page (not category page)
                    if len(href.split('/')) >= 4:  # e.g., /our-menu/rice-bowls/kfc-original-ranch-rice-bowl
                        product_name = self._extract_product_name_from_url(href)
                        product_url = urljoin(self.base_url, href)
                        
                        products.append({
                            'name': product_name,
                            'url': product_url,
                            'product_id': href.split('/')[-1],
                            'scraped_category': category_name,
                            'company': 'kfc'  # Add company field
                        })
            
            # Method 2: Extract from JSON data
            if not products:
                script_data = soup.find('script', id='__NEXT_DATA__')
                if script_data:
                    json_data = json.loads(script_data.string)
                    json_products = self._extract_products_from_json(json_data, category_name)
                    products.extend(json_products)
            
            # Remove duplicates
            unique_products = []
            seen_urls = set()
            for product in products:
                if product['url'] not in seen_urls:
                    unique_products.append(product)
                    seen_urls.add(product['url'])
            
            print(f"Found {len(unique_products)} products in category '{category_name}'")
            return unique_products
            
        except Exception as e:
            print(f"Error fetching products from category '{category_name}': {e}")
            traceback.print_exc()
            return []
    
    def _extract_product_name_from_url(self, url):
        """Extract product name from URL"""
        parts = url.split('/')
        if len(parts) >= 2:
            name_part = parts[-1]
            # Clean name
            name = name_part.replace('kfc-', '').replace('-', ' ').title()
            return name
        return "Unknown Product"
    
    def _extract_products_from_json(self, json_data, category_name):
        """Extract product information from JSON data"""
        products = []
        try:
            # Here we need to parse product info based on actual JSON structure
            # Due to complex JSON structure, we mainly rely on HTML parsing
            pass
        except Exception as e:
            print(f"Error extracting products from JSON: {e}")
        
        return products

    # --- II. Detail Page Scraping and Mapping ---

    def get_product_details(self, product_page_data):
        """
        Get detailed product information and map to target structure.
        Extract title and description content from product page.
        """
        product_url = product_page_data['url']
        product_name = product_page_data['name']
        
        try:
            response = self.session.get(product_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            final_data = product_page_data.copy()
            
            # --- 1. Extract title ---
            title_element = soup.find('title')
            title_text = ""
            if title_element:
                title_text = title_element.get_text(strip=True)
                # Clean title, remove KFC | etc. prefix
                if '|' in title_text:
                    title_parts = title_text.split('|')
                    if len(title_parts) > 1:
                        title_text = '|'.join(title_parts[1:]).strip()
            final_data['marketing_name'] = title_text if title_text else product_name
            final_data['name'] = product_name

            # --- 2. Extract description (meta description) ---
            description = ""
            meta_description = soup.find('meta', attrs={'name': 'description'})
            if meta_description and meta_description.get('content'):
                description = meta_description['content'].strip()
            final_data['description_api'] = description

            # --- 3. Image URL (image_url) ---
            image_url = self._extract_image(soup)
            final_data['image_url'] = image_url

            # --- 4. Nutrition information - Set as empty ---
            nutrition_data = {
                'calories': '', 'protein': '', 'carbs': '', 'fat': '', 
                'sugar': '', 'salt': ''
            }
            final_data.update(nutrition_data)
            
            # --- 5. Ingredients - Set as empty ---
            final_data['ingredient_statement_preview'] = ''
            
            # --- 6. Other fields ---
            final_data['category_api'] = '' 
            final_data['total_components'] = 0
            final_data['company'] = 'kfc'  # Add company field
            
            print(f"Product fetched: {product_name} | Title: {title_text[:30]}...")
            return final_data
            
        except Exception as e:
            print(f"Error getting details for product '{product_name}': {e}")
            traceback.print_exc()
            return None

    def _extract_image(self, soup):
        """Extract product image"""
        try:
            # Find product image - based on provided HTML structure
            image_elements = soup.find_all('img')
            for img in image_elements:
                src = img.get('src', '')
                if src and ('rice-bowl' in src.lower() or 'product' in src.lower() or 'menu' in src.lower()):
                    if src.startswith('http'):
                        return src
                    else:
                        return urljoin(self.base_url, src)
            
            # Find image from JSON data
            script_data = soup.find('script', id='__NEXT_DATA__')
            if script_data:
                json_data = json.loads(script_data.string)
                image_url = self._extract_image_from_json(json_data)
                if image_url:
                    return image_url
            
        except Exception as e:
            print(f"Error extracting image: {e}")
        
        return ""

    def _extract_image_from_json(self, json_data):
        """Extract image URL from JSON data"""
        try:
            # Find image based on provided HTML structure
            main_content = json_data.get('props', {}).get('pageProps', {}).get('data', {}).get('mainContent', [])
            
            for content in main_content:
                if content.get('id') == 'two_column_cta':
                    children = content.get('data', {}).get('children', [])
                    for child in children:
                        image_data = child.get('image', {})
                        if image_data:
                            original = image_data.get('original', {})
                            image_url = original.get('url')
                            if image_url:
                                return image_url
                
        except Exception as e:
            print(f"Error extracting image from JSON: {e}")
        
        return ""

    # --- III. Complete Scraping Process ---

    def scrape_all(self):
        """Execute complete scraping process"""
        print("Starting KFC menu scraping...")
        
        categories = self.get_categories()
        if not categories:
            print("No categories found, scraping terminated")
            return
        
        all_products = []
        
        for category in categories:
            print(f"\nProcessing category: {category['name']}")
            products = self.get_products_from_category(category['url'], category['name'])
            
            for product_page_data in products:
                # Delay to avoid too many requests
                time.sleep(0.5) 
                
                # Get detailed information
                final_data = self.get_product_details(product_page_data)
                
                if final_data:
                    all_products.append(final_data)
                    print(f"  ✓ Fetched: {final_data['name']}")
                else:
                    print(f"  ✗ Failed to fetch: {product_page_data['name']}")
        
        self.all_products = all_products
        print(f"\nScraping completed! Total {len(self.all_products)} products fetched")
        
    # --- IV. Data Saving and Reporting ---
    
    def save_to_json(self, filename="kfc_menu_mapped.json"):
        """Save data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.all_products, f, ensure_ascii=False, indent=2)
        print(f"Data saved to {filename}")
    
    def save_to_csv(self, filename="kfc_menu_mapped.csv"):
        """Save data to CSV file"""
        
        if not self.all_products:
            print("No data to save")
            return
        
        # CSV field list
        fieldnames = [
            'product_id', 'marketing_name', 'name', 'scraped_category', 'category_api',
            'image_url', 'description_api', 'company',
            'calories', 'protein', 'carbs', 'fat', 'sugar', 'salt',
            'total_components', 'ingredient_statement_preview'
        ]
        
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            for product in self.all_products:
                # Ensure all fields exist
                csv_row = {
                    'product_id': product.get('product_id', ''),
                    'marketing_name': product.get('marketing_name', product.get('name', '')),
                    'name': product.get('name', ''),
                    'scraped_category': product.get('scraped_category', ''),
                    'category_api': product.get('category_api', ''),
                    'image_url': product.get('image_url', ''),
                    'description_api': product.get('description_api', ''),
                    'company': product.get('company', 'kfc'),
                    'calories': product.get('calories', ''),
                    'protein': product.get('protein', ''),
                    'carbs': product.get('carbs', ''),
                    'fat': product.get('fat', ''),
                    'sugar': product.get('sugar', ''),
                    'salt': product.get('salt', ''),
                    'total_components': product.get('total_components', 0),
                    'ingredient_statement_preview': product.get('ingredient_statement_preview', '')
                }
                writer.writerow(csv_row)
        
        print(f"Data saved to {filename}")

    # --- V. Test Methods ---
    
    def test_single_product(self, product_url):
        """Test single product URL and print mapping results"""
        # Simulate basic data
        product_data = {
            'url': product_url,
            'product_id': product_url.split('/')[-1],
            'name': product_url.split('/')[-1].replace('-', ' ').title(),
            'scraped_category': 'Test Category',
            'company': 'kfc'  # Add company field
        }
        
        print(f"--- Starting test: {product_data['name']} ---")
        final_data = self.get_product_details(product_data)

        if final_data:
            print("\n--- Extraction Results ---")
            print(f"Product ID: {final_data.get('product_id')}")
            print(f"Product Name: {final_data.get('name')}")
            print(f"Marketing Name: {final_data.get('marketing_name')}")
            print(f"Description: {final_data.get('description_api', '')[:100]}...")
            print(f"Image URL: {final_data.get('image_url', 'N/A')}")
            print(f"Category: {final_data.get('scraped_category')}")
            print(f"Company: {final_data.get('company')}")
        else:
            print(f"Test failed: Could not extract product details. URL: {product_url}")

def main():
    scraper = KFCProductScraper()
    
    # Choose to run complete scraping or single test
    choice = input("Select mode: (1)Complete scraping (2)Single product test: ")
    
    if choice == "2":
        # Single product test - using the provided rice bowl page
        test_url = "https://www.kfc.co.uk/our-menu/rice-bowls/kfc-original-ranch-rice-bowl"
        scraper.test_single_product(test_url)
    else:
        # Complete scraping
        scraper.scrape_all()
        
        if scraper.all_products:
            scraper.save_to_json()
            scraper.save_to_csv()
            
            # Print summary
            print("\n=== Scraping Summary ===")
            print(f"Total products: {len(scraper.all_products)}")
            if scraper.all_products:
                example = scraper.all_products[0]
                print("\nFirst product data example:")
                print(f"  Name: {example.get('name')}")
                print(f"  Marketing Name: {example.get('marketing_name')}")
                print(f"  Description: {example.get('description_api', '')[:50]}...")
                print(f"  Image: {example.get('image_url', 'N/A')[:50]}...")
                print(f"  Company: {example.get('company')}")
        else:
            print("No data fetched")

if __name__ == "__main__":
    main()