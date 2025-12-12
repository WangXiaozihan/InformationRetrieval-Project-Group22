import requests
from bs4 import BeautifulSoup
import json
import time
import csv
from urllib.parse import urljoin
import traceback
import re

class McDonaldsProductScraper:
    def __init__(self):
        self.base_url = "https://www.mcdonalds.com"
        self.menu_url = "https://www.mcdonalds.com/gb/en-gb/menu.html"
        self.api_url = "https://www.mcdonalds.com/dnaapp/itemDetails"  # API URL for regular items
        self.collection_api_url = "https://www.mcdonalds.com/dnaapp/itemCollectionDetails"  # API URL for collections (Happy Meals)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    # --- I. Page Scraping: Get Categories and Product IDs/Images ---

    def get_menu_categories(self):
        """Get all menu categories"""
        try:
            print("Accessing menu page to get all categories...")
            response = self.session.get(self.menu_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            categories = []
            menu_items = soup.find('ul', class_='menu-items')
            
            if menu_items:
                category_items = menu_items.find_all('li', class_='menu-item')
                for item in category_items:
                    category_data = {}
                    link = item.find('a', class_='link')
                    if link and link.get('href'):
                        category_data['url'] = urljoin(self.base_url, link['href'])
                        try:
                            data_json = json.loads(link.get('data-cmp-data-layer', '{}'))
                            category_data['name'] = data_json.get('dc:title', '')
                        except:
                            pass
                    
                    if not category_data.get('name'):
                        name_elem = item.find('span', class_='menu-text')
                        if name_elem:
                            category_data['name'] = name_elem.get_text(strip=True)
                    
                    if category_data.get('name') and category_data.get('url'):
                        categories.append(category_data)
            
            return categories
            
        except Exception as e:
            print(f"Error getting menu categories: {e}")
            return []
    
    def get_products_from_category(self, category_url, category_name):
        """
        Get all product IDs, names and image URLs from category page.
        This is the 【Page Scraping + Image Extraction】 part.
        """
        try:
            print(f"Getting product IDs and images from category '{category_name}'...")
            response = self.session.get(category_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            product_items = soup.find_all('li', class_='cmp-category__item')
            print(f"  Found {len(product_items)} products in category '{category_name}'")
            
            products = []
            
            for item in product_items:
                product_data = {'scraped_category': category_name, 'company': "McDonald's"}
                product_data['product_id'] = item.get('data-product-id', '')
                
                # Extract product URL and name (for logging and URL field)
                link = item.find('a', class_='cmp-category__item-link')
                if link and link.get('href'):
                    product_data['url'] = urljoin(self.base_url, link['href'])
                
                name_elem = item.find('div', class_='cmp-category__item-name')
                product_data['name'] = name_elem.get_text(strip=True) if name_elem else 'Unknown'

                # ⭐ Extract product image URL
                img_elem = item.find('img', class_='categories-item-img')
                if img_elem and img_elem.get('src'):
                    product_data['image_url'] = urljoin(self.base_url, img_elem['src'])
                else:
                    product_data['image_url'] = ''
                
                # Check if this is a Happy Meal (based on category name or product name)
                if 'happy meal' in category_name.lower() or 'happy meal' in product_data['name'].lower():
                    product_data['is_happy_meal'] = True
                else:
                    product_data['is_happy_meal'] = False
                
                if product_data.get('product_id') and product_data.get('product_id').isdigit():
                    products.append(product_data)
            
            return products
            
        except Exception as e:
            print(f"Error getting products from category '{category_name}': {e}")
            return []

    # --- II. API Data Retrieval and Parsing: Get Detailed Data ---
    
    def get_product_details_from_api(self, product_id, is_happy_meal=False):
        """Get product details via API (【API Extraction】 part, using robust logic)"""
        response = None 
        try:
            if is_happy_meal:
                # Use collection API for Happy Meals
                params = {
                    'country': 'UK', 
                    'language': 'en',
                    'showLiveData': 'true',
                    'item': product_id,
                    'specialCall': 'true'
                }
                api_url = self.collection_api_url
                print(f"  Using collection API for Happy Meal {product_id}")
            else:
                # Use regular API for other products
                params = {
                    'country': 'UK', 
                    'language': 'en',
                    'showLiveData': 'true',
                    'item': product_id
                }
                api_url = self.api_url
            
            response = self.session.get(api_url, params=params)
            response.raise_for_status() 
            data = response.json()
            
            if is_happy_meal:
                product_info = self.extract_happy_meal_info(data, product_id)
            else:
                product_info = self.extract_product_info(data, product_id)
            
            return product_info
            
        except requests.exceptions.HTTPError as http_err:
            print(f"API HTTP Error ({product_id}): {response.status_code}")
            return None
            
        except json.JSONDecodeError:
            print(f"API JSON Error ({product_id}): Response is not JSON")
            return None
            
        except Exception as e:
            print(f"API Unknown Error ({product_id}): {e}")
            return None

    def extract_product_info(self, api_data, product_id):
        """Extract useful product information from API response (using latest fixed logic)"""
        item_data = None
        
        # Try to extract product data from multiple common structures
        potential_items = api_data.get('item') or (api_data.get('items') and api_data['items'].get('item')) or api_data.get('items')

        # Safely extract product data
        if isinstance(potential_items, list) and len(potential_items) > 0:
            item_data = potential_items[0]
        # Fix for single product dictionary structure
        elif isinstance(potential_items, dict) and any(field in potential_items for field in ['item_name', 'item_marketing_name']):
            item_data = potential_items
        
        if not item_data:
            return None
        
        # Extract and merge information
        product_info = {
            'product_id': product_id,
            'marketing_name': item_data.get('item_marketing_name', ''),
            'description_api': item_data.get('description', ''), # Description from API
            'category_api': self.get_category(item_data),        # Category from API
            'company': "McDonald's"  # Add company field
        }
        
        # Extract detailed information
        product_info.update(self.extract_ingredients_info(item_data))
        product_info.update(self.extract_nutrition_info(item_data))
        product_info.update(self.extract_components_info(item_data))
        
        return product_info

    def extract_happy_meal_info(self, api_data, product_id):
        """Extract Happy Meal information from collection API response"""
        try:
            meal_data = api_data.get('meal_item', {})
            
            if not meal_data:
                return None
            
            # Extract basic information
            product_info = {
                'product_id': product_id,
                'marketing_name': meal_data.get('item_marketing_name', ''),
                'description_api': meal_data.get('description', ''),
                'category_api': self.get_category(meal_data),
                'company': "McDonald's",
                'is_happy_meal': True
            }
            
            # Extract nutrition information from collective_nutrition
            nutrition_info = self.extract_happy_meal_nutrition(meal_data)
            product_info.update(nutrition_info)
            
            # Extract ingredients from components
            ingredients_info = self.extract_happy_meal_ingredients(meal_data)
            product_info.update(ingredients_info)
            
            # Extract components count
            components_info = self.extract_happy_meal_components(meal_data)
            product_info.update(components_info)
            
            return product_info
            
        except Exception as e:
            print(f"Error extracting Happy Meal info: {e}")
            return None

    def extract_happy_meal_nutrition(self, meal_data):
        """Extract nutrition information for Happy Meal"""
        nutrition_info = {'calories': '', 'protein': '', 'carbs': '', 'fat': '', 'sugar': '', 'salt': ''}
        try:
            collective_nutrition = meal_data.get('collective_nutrition', {})
            if collective_nutrition and 'nutrient_facts' in collective_nutrition:
                nutrients = collective_nutrition['nutrient_facts'].get('nutrient', [])
                if not isinstance(nutrients, list): 
                    nutrients = [nutrients]
                    
                for nutrient in nutrients:
                    name = nutrient.get('name', '').lower()
                    value = nutrient.get('value', '')
                    uom = nutrient.get('uom', '')
                    
                    if 'energy kcal' in name: 
                        nutrition_info['calories'] = f"{value} {uom}"
                    elif 'protein' in name: 
                        nutrition_info['protein'] = f"{value} {uom}"
                    elif 'carbohydrates' in name: 
                        nutrition_info['carbs'] = f"{value} {uom}"
                    elif 'fat' in name and 'saturated' not in name: 
                        nutrition_info['fat'] = f"{value} {uom}"
                    elif 'sugars' in name: 
                        nutrition_info['sugar'] = f"{value} {uom}"
                    elif 'salt' in name: 
                        nutrition_info['salt'] = f"{value} {uom}"
        except Exception as e:
            print(f"Error extracting Happy Meal nutrition: {e}")
        
        return nutrition_info

    def extract_happy_meal_ingredients(self, meal_data):
        """
        Extract ingredients information for Happy Meal.
        Combines item name and ingredient statement.
        """
        ingredients_info = {
            'ingredient_statement': meal_data.get('item_ingredient_statement', ''),
            'components_ingredients': []
        }
        try:
            # Happy Meals have items within the meal
            items = meal_data.get('items', {}).get('item', [])
            if not isinstance(items, list):
                items = [items]
            
            for item in items:
                # Use item_name as the name of the Happy Meal sub-product.
                component_name = item.get('item_name', 'Unknown Component') 
                ingredient = item.get('item_ingredient_statement', '')
                
                if ingredient:
                    # Combined into a new format: name:\n ingredient_statement\n
                    formatted_ingredient = f"{component_name}:\n{ingredient}\n"
                    ingredients_info['components_ingredients'].append(formatted_ingredient)
                    
        except Exception as e:
            print(f"Error extracting Happy Meal ingredients: {e}")
        
        return ingredients_info

    def extract_happy_meal_components(self, meal_data):
        """Extract components information for Happy Meal"""
        components_info = {'component_names': [], 'total_components': 0}
        try:
            items = meal_data.get('items', {}).get('item', [])
            if not isinstance(items, list):
                items = [items]
            
            components_info['total_components'] = len(items)
            
            # Extract component names
            for item in items:
                name = item.get('item_name', '')
                if name:
                    components_info['component_names'].append(name)
        except Exception as e:
            print(f"Error extracting Happy Meal components: {e}")
        
        return components_info

    # --- III. Helper Extraction Methods (API Parsing) ---

    def get_category(self, item_data):
        """Extract category information from API response"""
        try:
            if 'default_category' in item_data and 'category' in item_data['default_category']:
                return item_data['default_category']['category'].get('name', '')
            return ''
        except:
            return ''
    
    def extract_ingredients_info(self, item_data):
        """
        Extract ingredients information.
        MODIFIED: Only uses 'imported_product_name' for component name in regular products.
        """
        ingredients_info = {
            'ingredient_statement': item_data.get('item_ingredient_statement', ''),
            'components_ingredients': []
        }
        try:
            if 'components' in item_data and 'component' in item_data['components']:
                components = item_data['components']['component']
                if not isinstance(components, list): components = [components]
                for component in components:
                    # ⭐ 关键修改：只使用 imported_product_name
                    component_name = component.get('imported_product_name', 'Unknown Component')
                    ingredient = component.get('ingredient_statement')
                    
                    if ingredient:
                        # 组合成新的格式: name:\n ingredient_statement\n
                        formatted_ingredient = f"{component_name}:\n{ingredient}\n"
                        ingredients_info['components_ingredients'].append(formatted_ingredient)
                        
        except:
            pass
        return ingredients_info
    
    def extract_nutrition_info(self, item_data):
        """Extract nutrition information"""
        nutrition_info = {'calories': '', 'protein': '', 'carbs': '', 'fat': '', 'sugar': '', 'salt': ''}
        try:
            if 'nutrient_facts' in item_data and 'nutrient' in item_data['nutrient_facts']:
                nutrients = item_data['nutrient_facts']['nutrient']
                if not isinstance(nutrients, list): nutrients = [nutrients]
                    
                for nutrient in nutrients:
                    name = nutrient.get('name', '').lower()
                    value = nutrient.get('value', '')
                    uom = nutrient.get('uom', '')
                    
                    if 'energy kcal' in name: nutrition_info['calories'] = f"{value} {uom}"
                    elif 'protein' in name: nutrition_info['protein'] = f"{value} {uom}"
                    elif 'carbohydrates' in name: nutrition_info['carbs'] = f"{value} {uom}"
                    elif 'fat' in name and 'saturated' not in name: nutrition_info['fat'] = f"{value} {uom}"
                    elif 'sugars' in name: nutrition_info['sugar'] = f"{value} {uom}"
                    elif 'salt' in name: nutrition_info['salt'] = f"{value} {uom}"
        except:
            pass
        return nutrition_info
    
    def extract_components_info(self, item_data):
        """Extract components information"""
        components_info = {'component_names': [], 'total_components': 0}
        try:
            if 'components' in item_data and 'component' in item_data['components']:
                components = item_data['components']['component']
                if not isinstance(components, list): components = [components]
                components_info['total_components'] = len(components)
        except:
            pass
        return components_info

    # --- IV. Complete Scraping Process (Hybrid Mode) ---

    def scrape_all_products(self):
        """Complete scraping process: Page gets IDs and images -> API gets details"""
        print("Starting to scrape all McDonald's category product information...")
        
        categories = self.get_menu_categories()
        if not categories:
            print("No categories found, stopping scraping.")
            return []
        
        all_products = []
        all_product_ids = set() 
        
        for i, category in enumerate(categories, 1):
            category_name = category['name']
            category_url = category['url']
            
            print(f"\n[{i}/{len(categories)}] Processing category: {category_name}")
            
            # 1. Get IDs and images from category page (Page Scraping)
            products_in_category = self.get_products_from_category(category_url, category_name)
            
            for j, product_page_data in enumerate(products_in_category, 1):
                product_id = product_page_data['product_id']
                product_name = product_page_data['name']
                is_happy_meal = product_page_data.get('is_happy_meal', False)
                
                if product_id in all_product_ids:
                    continue
                
                all_product_ids.add(product_id)
                
                print(f"  [{j}] Getting details for ID {product_id} ({product_name}) via API...")
                if is_happy_meal:
                    print(f"  (This is a Happy Meal, using collection API)")
                
                # 2. Get detailed information via API (API Extraction)
                api_info = self.get_product_details_from_api(product_id, is_happy_meal)
                
                if api_info:
                    # 3. Merge data: Page data + API data
                    final_product = {**product_page_data, **api_info}
                    all_products.append(final_product)
                    print(f"  ✓ Successfully got information for product {product_id}")
                else:
                    # Even if API fails, keep page data (ID/name/image)
                    all_products.append(product_page_data) 
                    print(f"  ✗ Failed to get information for product {product_id}, keeping only page data.")
                
                time.sleep(1)
            
            time.sleep(2) 
            
        print(f"\nScraping completed! Total {len(all_products)} products fetched")
        return all_products

    # --- V. Data Saving and Reporting ---
    
    def save_data(self, products, json_filename="mcdonalds_products_data.json", csv_filename="mcdonalds_products_data.csv"):
        """Save data to JSON and CSV files"""
        
        if not products:
            print("No data to save")
            return
        
        # Save as JSON
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print(f"Complete data saved to {json_filename}")
        
        # Save as CSV
        fieldnames = [
            'product_id', 'marketing_name', 'name', 'scraped_category', 'category_api', 
            'image_url', 'description_api', 'company',
            'calories', 'protein', 'carbs', 'fat', 'sugar', 'salt',
            'total_components', 'ingredient_statement_preview'
        ]
        
        with open(csv_filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore') # Ignore undefined keys
            writer.writeheader()
            
            for product in products:
                # Create ingredients preview
                # components_ingredients 现在是带名称的格式化字符串
                main_ingredients = product.get('ingredient_statement', '')
                if not main_ingredients and product.get('components_ingredients'):
                    # 如果有组件配料，使用第一个组件配料作为预览的基础
                    main_ingredients = product['components_ingredients'][0] if product['components_ingredients'] else ''
                
                # 预览仍然只取前100个字符
                ingredient_preview = BeautifulSoup(main_ingredients, 'html.parser').get_text(strip=True)[:100] + '...' if main_ingredients else ''
                
                csv_row = {
                    'product_id': product.get('product_id', ''),
                    'marketing_name': product.get('marketing_name', ''),
                    'name': product.get('name', ''),
                    'scraped_category': product.get('scraped_category', ''),
                    'category_api': product.get('category_api', ''),
                    'image_url': product.get('image_url', ''),
                    'description_api': product.get('description_api', ''),
                    'company': product.get('company', "McDonald's"),
                    'calories': product.get('calories', ''),
                    'protein': product.get('protein', ''),
                    'carbs': product.get('carbs', ''),
                    'fat': product.get('fat', ''),
                    'sugar': product.get('sugar', ''),
                    'salt': product.get('salt', ''),
                    'total_components': product.get('total_components', 0),
                    'ingredient_statement_preview': ingredient_preview
                }
                writer.writerow(csv_row)
        
        print(f"CSV data saved to {csv_filename}")
    
    def generate_report(self, products):
        """Generate statistical report"""
        if not products: return
        
        api_success_count = sum(1 for p in products if p.get('calories'))
        happy_meal_count = sum(1 for p in products if p.get('is_happy_meal'))
        
        print("\n=== Scraping Results Statistics ===")
        print(f"Total products: {len(products)}")
        print(f"Happy Meals: {happy_meal_count}")
        print(f"Successfully got detailed information via API: {api_success_count}")
        
        print("\nProduct information examples:")
        for i, product in enumerate(products[:3]):
            name = product.get('marketing_name', product.get('name', 'Unknown'))
            print(f"\n{i+1}. {name}")
            print(f"    Product ID: {product.get('product_id', 'N/A')}")
            print(f"    Scraped Category: {product.get('scraped_category', 'N/A')}")
            print(f"    Image URL: {product.get('image_url', 'N/A')}")
            print(f"    Calories: {product.get('calories', 'N/A')}")
            print(f"    Company: {product.get('company', 'N/A')}")
            if product.get('is_happy_meal'):
                print(f"    Type: Happy Meal")


def main():
    """Main function"""
    scraper = McDonaldsProductScraper()
    
    products = scraper.scrape_all_products()
    
    print(f"\nScraping completed! Total {len(products)} products fetched")
    
    if products:
        # Save data
        scraper.save_data(products)
        
        # Generate statistical report
        scraper.generate_report(products)
    else:
        print("No product data fetched")

if __name__ == "__main__":
    main()