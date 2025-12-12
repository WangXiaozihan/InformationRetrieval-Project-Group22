import requests
from bs4 import BeautifulSoup
import time
import json
import csv
from urllib.parse import urljoin
import re
import traceback

class WendysProductScraper:
    def __init__(self):
        self.base_url = "https://www.wendys.com"
        # UK menu page as entry point
        self.menu_url = "https://www.wendys.com/en-gb/menu/our-menu" 
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.all_products = [] # For storing final results
    
    # --- I. Menu and Category Scraping (based on your original code) ---

    def get_categories(self):
        """Get all menu categories"""
        print("Getting menu categories...")
        try:
            response = self.session.get(self.menu_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            categories = []
            category_elements = soup.find_all('article', class_='node--food-menu-category')
            
            for element in category_elements:
                category_name = element.find('h3')
                category_link = element.find('a', class_='field-group-link')
                
                if category_name and category_link:
                    category_url = urljoin(self.base_url, category_link['href'])
                    categories.append({
                        'name': category_name.text.strip(),
                        'url': category_url,
                    })
            
            print(f"Found {len(categories)} categories")
            return categories
            
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []
    
    def get_products_from_category(self, category_url, category_name):
        """Get all product links, names and IDs from category page"""
        print(f"Getting products from category '{category_name}'...")
        try:
            response = self.session.get(category_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            products = []
            product_elements = soup.find_all('article', class_='node--food-menu-item')
            
            for element in product_elements:
                product_link = element.find('a', class_='field-group-link')
                product_name = element.find('h3')
                
                if product_link and product_name:
                    product_url = urljoin(self.base_url, product_link['href'])
                    products.append({
                        'name': product_name.text.strip(),
                        'url': product_url,
                        # Use itemId as product_id
                        'product_id': element.get('itemId', ''), 
                        'scraped_category': category_name,
                        'company': "Wendy's"  # Add company field
                    })
            
            print(f"Found {len(products)} products in category '{category_name}'")
            return products
            
        except Exception as e:
            print(f"Error getting products from category '{category_name}': {e}")
            return []
    
    # --- II. Detail Page Scraping and Mapping ---

    def get_product_details(self, product_page_data):
        """
        Get detailed product information and map to target structure.
        This is the core part of 【Web Scraping】.
        """
        product_url = product_page_data['url']
        product_name = product_page_data['name']
        
        try:
            response = self.session.get(product_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            final_data = product_page_data.copy()
            
            # --- 1. Image URL (image_url) ---
            image_element = soup.find('img', class_='media__element')
            image_url = ""
            if image_element and 'data-src' in image_element.attrs:
                image_url = urljoin(self.base_url, image_element['data-src'])
            elif image_element and 'src' in image_element.attrs:
                image_url = urljoin(self.base_url, image_element['src'])
            final_data['image_url'] = image_url

            # --- 2. Description (description_api) ---
            description = self._extract_description(soup)
            final_data['description_api'] = description

            # --- 3. Nutrition information (calories, protein, carbs, fat, sugar, salt) ---
            nutrition = self._extract_nutrition(soup)
            final_data.update(nutrition)
            
            # --- 4. Ingredients (components_ingredients and ingredient_statement_preview) ---
            components_ingredients = self._extract_ingredients(soup)
            # Save the list of formatted ingredient strings
            final_data['components_ingredients'] = components_ingredients 
            
            # Generate the preview string
            preview = "; ".join(components_ingredients)
            final_data['ingredient_statement_preview'] = preview[:250] + '...' if len(preview) > 250 else preview
            
            # --- 5. Map to final structure ---
            final_data['marketing_name'] = product_name
            final_data['name'] = product_name
            final_data['category_api'] = '' # Cannot accurately extract from single page
            # Calculate total components based on the extracted ingredient list
            final_data['total_components'] = len(components_ingredients) 
            final_data['company'] = "Wendy's"  # Add company field
            
            print(f"Product fetched: {product_name} | Calories: {final_data['calories']}")
            return final_data
            
        except Exception as e:
            print(f"Error getting details for product '{product_name}': {e}")
            return None
            
    # --- III. Helper Extraction Methods (Web Content) ---

    def _extract_description(self, soup):
        """Extract product description from summary area"""
        description = ""
        try:
            # Description is inside food-menu--menu-item--summary > div.field--name-body
            description_div = soup.select_one('.food-menu--menu-item--summary .field--name-body')
            if description_div:
                # Extract <p> tag content
                p_tag = description_div.find('p')
                if p_tag:
                    description = p_tag.get_text(strip=True)
        except:
            pass
        return description

    def _extract_nutrition(self, soup):
        """Extract structured nutrition data from Nutrition accordion block"""
        nutrition_data = {
            'calories': '', 'protein': '', 'carbs': '', 'fat': '', 
            'sugar': '', 'salt': ''
        }
        
        # Target div with class="field--name-nutrition-*"
        nutrition_block = soup.find('div', class_='brick--nutrition-block-uk')
        if not nutrition_block:
            # Try to extract from calorie info in summary
            calorie_element = soup.find('div', class_='field--name-calorie')
            if calorie_element:
                nutrition_data['calories'] = calorie_element.get_text(strip=True)
            return nutrition_data
        
        # Map field names to CSS class name parts
        field_map = {
            'calories': 'nutrition-energy',
            'fat': 'nutrition-fat',
            'protein': 'nutrition-protein',
            'carbs': 'nutrition-carbohydrate',
            'sugar': 'nutrition-sugars',
            'salt': 'nutrition-salt'
        }

        for key, css_suffix in field_map.items():
            field_div = nutrition_block.find('div', class_=re.compile(f'field--name-{css_suffix}'))
            if field_div:
                value_item = field_div.find('div', class_='field__item')
                if value_item:
                    value = value_item.get_text(strip=True)
                    # Add units (kcal/g), need to judge by label, but for simplicity we assume units
                    if key == 'calories':
                        nutrition_data[key] = f"{value} kcal"
                    else:
                        nutrition_data[key] = f"{value} g"
        
        return nutrition_data

    def _extract_ingredients(self, soup):
        """
        MODIFIED: Extracts ingredients and formats them as 'Name:\n Description\n'.
        Returns a list of these formatted strings, or an empty list on failure.
        """
        formatted_ingredients = []
        
        try:
            # Method 1: Find accordion header containing "Ingredients" text
            ingredients_header = None
            all_headers = soup.find_all(['h3', 'div', 'a'], string=re.compile(r'Ingredients', re.IGNORECASE))
            
            for header in all_headers:
                if 'ingredient' in header.get_text(strip=True).lower():
                    ingredients_header = header
                    break
            
            target_scope = soup # Default to search entire soup
            
            if ingredients_header:
                # Find corresponding accordion content
                accordion_content = ingredients_header.find_next('div', class_='accordion-content')
                if not accordion_content:
                    # If not found directly, header might be in parent element
                    parent_accordion = ingredients_header.find_parent('div', class_='accordion-item')
                    if parent_accordion:
                        accordion_content = parent_accordion.find('div', class_='accordion-content')
                
                if accordion_content:
                    target_scope = accordion_content

            # Search within the target scope (accordion content or entire soup)
            ingredient_articles = target_scope.find_all('article', class_='node--ingredients')
            
            for article in ingredient_articles:
                name_elem = article.find('h3')
                body_elem = article.find('div', class_='field--name-body')
                
                name = name_elem.get_text(strip=True) if name_elem else "Unknown Component"
                description = ""
                
                if body_elem:
                    p_tag = body_elem.find('p')
                    if p_tag:
                        description = p_tag.get_text(strip=True)
                
                # We only format and include if a description/ingredient statement exists
                if description:
                    # ⭐ Format as requested: name:\n ingredient_statement\n
                    formatted_ingredients.append(f"{name}:\n{description}\n")
            
        except Exception as e:
            print(f"Error extracting ingredients: {e}")
            # Return empty list on error
            return []

        return formatted_ingredients

    # --- IV. Complete Scraping Process ---

    def scrape_all(self):
        """Execute complete scraping process"""
        print("Starting Wendy's menu scraping...")
        
        categories = self.get_categories()
        if not categories:
            print("No categories found, scraping terminated")
            return
        
        for category in categories:
            products = self.get_products_from_category(category['url'], category['name'])
            
            for product_page_data in products:
                # Delay
                time.sleep(0.5) 
                
                # Get detailed information
                final_data = self.get_product_details(product_page_data)
                
                if final_data:
                    self.all_products.append(final_data)
        
        print(f"\nScraping completed! Total {len(self.all_products)} products fetched")
        
    # --- V. Data Saving and Reporting (mapped to target CSV structure) ---
    
    def save_to_json(self, filename="wendys_menu_mapped.json"):
        """Save data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.all_products, f, ensure_ascii=False, indent=2)
        print(f"Data saved to {filename}")
    
    def save_to_csv(self, filename="wendys_menu_mapped.csv"):
        """Save data to CSV file (using target structure)"""
        
        if not self.all_products:
            print("No data to save")
            return
        
        # Target CSV field list
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
                # Ensure all fields exist, default to empty string or 0 if not extracted
                csv_row = {
                    'product_id': product.get('product_id', ''),
                    'marketing_name': product.get('marketing_name', product.get('name', '')),
                    'name': product.get('name', ''),
                    'scraped_category': product.get('scraped_category', ''),
                    'category_api': product.get('category_api', ''),
                    'image_url': product.get('image_url', ''),
                    'description_api': product.get('description_api', ''),
                    'company': product.get('company', "Wendy's"),
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

    # --- VI. Test Methods ---
    
    def test_single_product(self, product_url):
        """Test single product URL and print mapping results"""
        # Simulate basic scraped data
        product_data = {
            'url': product_url,
            'product_id': product_url.split('/')[-1],
            'name': product_url.split('/')[-1].replace('-', ' ').title(),
            'scraped_category': 'Test Category',
            'company': "Wendy's"  # Add company field
        }
        
        print(f"--- Starting test: {product_data['name']} ---")
        final_data = self.get_product_details(product_data)

        if final_data:
            print("\n--- Extraction Results ---")
            print(f"Product ID: {final_data.get('product_id')}")
            print(f"Product Name: {final_data.get('name')}")
            print(f"Calories: {final_data.get('calories')}")
            print(f"Fat: {final_data.get('fat')}")
            print(f"Description: {final_data.get('description_api', '')[:50]}...")
            print(f"Image URL: {final_data.get('image_url', 'N/A')[:50]}...")
            print(f"Company: {final_data.get('company')}")
            print("\n--- Ingredients Preview (ingredient_statement_preview) ---")
            
            preview = final_data.get('ingredient_statement_preview')
            if not preview or preview == "Extraction Error":
                print("Extraction failed: ingredient information is empty")
            else:
                print(preview)
            
            print("\n--- Components Ingredients List (components_ingredients) ---")
            components_list = final_data.get('components_ingredients', [])
            if components_list:
                for item in components_list:
                    print(f"  - {item.strip()}")
            else:
                print("  (Empty)")

        else:
            print(f"Test failed: Could not extract product details. URL: {product_url}")

def main():
    scraper = WendysProductScraper()
    
    # Choose to run complete scraping or single test
    choice = input("Select mode: (1)Complete scraping (2)Single product test: ")
    
    if choice == "2":
        # Single product test
        test_url = "https://www.wendys.com/en-gb/grilled-cheese-cheeseburger-single"
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
            example = scraper.all_products[0] if scraper.all_products else {}
            if example:
                print("\nFirst product data example:")
                print(f"  Name: {example.get('name')}")
                print(f"  Calories: {example.get('calories')}")
                print(f"  Image: {example.get('image_url')[:50]}...")
                print(f"  Ingredients Preview: {example.get('ingredient_statement_preview')}")
                print(f"  Company: {example.get('company')}")
        else:
            print("No data fetched")

if __name__ == "__main__":
    main()