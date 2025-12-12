import json
import pandas as pd
import re
import numpy as np

# ==========================================
# Category Mapping Definition
# ==========================================

CATEGORY_MAP = {
    # Breakfast
    'Breakfast Menu': ('Breakfast', 'Breakfast Sandwiches'),
    'Breakfast Sandwiches': ('Breakfast', 'Breakfast Sandwiches'),
    'Breakfast Wraps': ('Breakfast', 'Breakfast Wraps'),
    'Breakfast Combos': ('Breakfast', 'Breakfast Combos'),
    'Breakfast Saver Menu®': ('Breakfast', 'Breakfast Combos'),
    'Breakfast Sides': ('Breakfast', 'Breakfast Sides'),
    # Main Courses
    'Burgers': ('Main', 'Beef Burgers'),
    'Hamburgers': ('Main', 'Beef Burgers'),
    'Chicken Sandwiches': ('Main', 'Chicken Sandwiches'),
    'Twisters': ('Main', 'Wraps'),
    'Wraps': ('Main', 'Wraps'),
    'Wraps & Salads': ('Main', 'Wraps'),
    'Fresh-Made Salads': ('Main', 'Salads'),
    'Rice Bowls': ('Main', 'Bowls'),
    'Veggie Options': ('Main', 'Vegetarian'),
    'Vegetarian': ('Main', 'Vegetarian'),
    'Vegan': ('Main', 'Vegetarian'),
    'McNuggets®, Selects® & Veggie Dippers': ('Main', 'Chicken Pieces & Veggie Dippers'),
    'Just Chicken': ('Main', 'Chicken Pieces & Veggie Dippers'),
    'Chicken Nuggets & Tenders': ('Main', 'Chicken Pieces & Veggie Dippers'),
    'Kfc Sharing Buckets': ('Main', 'Chicken Buckets'),
    'Kids Buckets': ('Main', 'Chicken Buckets'),
    'Buckets For One': ('Main', 'Chicken Buckets'),
    'Combos': ('Main', 'Combos'),
    'Box Meals': ('Main', 'Combos'),
    'Biggie Deals': ('Main', 'Combos'),
    'Sharers & Bundles': ('Main', 'Combos'),
    # Sides & Sauces
    'Fries & Sides': ('Sides', 'Potato Sides'),
    'Sides Dips': ('Sides', 'Dips & Sauces'),
    'Condiments And Sauces': ('Sides', 'Dips & Sauces'),
    # Drinks & Desserts
    'McCafé®': ('Drinks', 'Hot Drinks'),
    'Coffee & Beverages': ('Drinks', 'Hot Drinks'),
    'Milkshakes & Cold Drinks': ('Drinks', 'Cold Drinks'),
    'Frosty®': ('Drinks', 'Frozen Treats'),
    'Drinks': ('Drinks', 'Soft Drinks'),
    'Desserts': ('Desserts', 'Sweets & Bakery'),
    # Others
    'Happy Meal®': ('Kids', 'Kids Meals'),
    "Wendy's Kids' Meal": ('Kids', 'Kids Meals'),
    'Saver Menu®': ('Value', 'Value Meals'),
    'What\'s New': ('Promotional', 'Limited Time'),
    'Whats New': ('Promotional', 'Limited Time'),
    'World Menu Heist': ('Promotional', 'Limited Time'),
}

# ==========================================
# Load Data
# ==========================================

with open('mcdonalds_products_data.json', 'r', encoding='utf-8') as f: 
    mcd_data = json.load(f)
with open('kfc_menu_mapped.json', 'r', encoding='utf-8') as f: 
    kfc_data = json.load(f)
with open('wendys_menu_mapped.json', 'r', encoding='utf-8') as f: 
    wendys_data = json.load(f)

# ==========================================
# Helper Functions
# ==========================================

def clean_numeric(value):
    """Extract numeric values, handle ranges"""
    if pd.isna(value) or value == "" or value is None:
        return None
    value_str = str(value).lower().strip()
    if '-' in value_str:
        parts = value_str.split('-')
        try:
            nums = [float(re.sub(r'[^\d.]', '', p)) for p in parts]
            return sum(nums) / len(nums)
        except: 
            pass
    cleaned = re.sub(r'[^\d.]', '', value_str)
    try:
        return float(cleaned)
    except ValueError:
        return None

def get_categories(original_category):
    """Return (Main Category, Sub Category)"""
    cleaned_category = str(original_category).strip()
    return CATEGORY_MAP.get(cleaned_category, ('Main', 'Other'))

# ==========================================
# Core Data Processing Function
# ==========================================

def process_data_source(data, brand_name):
    processed_list = []
    
    # Handle categories that map to multiple subcategories
    multi_map_categories = {
        'Milkshakes & Cold Drinks': [('Drinks', 'Cold Drinks'), ('Drinks', 'Milkshakes')]
    }

    for item in data:
        name = item.get('name') or item.get('marketing_name', '')
        orig_cat = item.get('scraped_category') or item.get('category_api', '') 
        desc = item.get('description_api', '')
        
        maps_to_apply = []
        if orig_cat in multi_map_categories:
            maps_to_apply = multi_map_categories[orig_cat]
        else:
            main_cat, sub_cat = get_categories(orig_cat)
            maps_to_apply = [(main_cat, sub_cat)]

        for main_cat, sub_cat in maps_to_apply:
            raw_comp_list = item.get('components_ingredients')
            raw_ing_preview = item.get('ingredient_statement_preview')
            
            components_list = raw_comp_list if isinstance(raw_comp_list, list) else []
            
            if components_list:
                ingredients_text = "\n".join([str(comp) for comp in components_list])
            elif raw_ing_preview:
                ingredients_text = str(raw_ing_preview)
            else:
                ingredients_text = ""

            processed = {
                'url': item.get('url'),
                'product_name': name,
                'brand': brand_name,
                'original_category': orig_cat,
                'category_main': main_cat,
                'category_sub': sub_cat,
                'description': str(desc).strip(),
                'image_url': item.get('image_url'),
                'components_list': components_list,
                'ingredients_text': ingredients_text,
                'calories_kcal': clean_numeric(item.get('calories')),
                'protein_g': clean_numeric(item.get('protein')),
                'fat_g': clean_numeric(item.get('fat')),
                'carbs_g': clean_numeric(item.get('carbs')),
                'sugar_g': clean_numeric(item.get('sugar')),
                'salt_g': clean_numeric(item.get('salt')),
            }
            processed_list.append(processed)
    return processed_list

# ==========================================
# Execute Processing
# ==========================================

print("Starting data processing...")

mcd_processed = process_data_source(mcd_data, 'McDonald\'s')
mcd_df = pd.DataFrame(mcd_processed)

nutrients_cols = ['calories_kcal', 'protein_g', 'fat_g', 'carbs_g', 'sugar_g', 'salt_g']
sub_category_means = mcd_df.groupby('category_sub')[nutrients_cols].mean()
main_category_means = mcd_df.groupby('category_main')[nutrients_cols].mean()

def impute_missing(item):
    nutrients = nutrients_cols
    name = item['product_name']
    sub_cat = item['category_sub']
    main_cat = item['category_main']
    
    for nut in nutrients:
        if pd.isna(item[nut]) or item[nut] == 0.0: 
            match = mcd_df[mcd_df['product_name'].str.lower() == name.lower()]
            if not match.empty:
                imputed_value = match.iloc[0][nut]
                if not pd.isna(imputed_value):
                    item[nut] = round(imputed_value, 2)
                    continue

            if sub_cat in sub_category_means.index and not pd.isna(sub_category_means.loc[sub_cat, nut]):
                item[nut] = round(sub_category_means.loc[sub_cat, nut], 2)
            elif main_cat in main_category_means.index and not pd.isna(main_category_means.loc[main_cat, nut]):
                item[nut] = round(main_category_means.loc[main_cat, nut], 2)
            else:
                item[nut] = 0.0
    return item

wendys_processed = process_data_source(wendys_data, "Wendy's")
kfc_processed = process_data_source(kfc_data, "KFC")

wendys_imputed = [impute_missing(item) for item in wendys_processed]
kfc_imputed = [impute_missing(item) for item in kfc_processed]

# Combine all data
all_data = mcd_processed + wendys_imputed + kfc_imputed
final_df = pd.DataFrame(all_data)

# Reindex IDs
final_df['id'] = range(1, len(final_df) + 1)
final_df = final_df[['id'] + [col for col in final_df.columns if col != 'id']]

# ==========================================
# Export JSON File
# ==========================================

json_file_name = 'fast_food_menu_final.json'
json_output = final_df.to_dict('records')
with open(json_file_name, 'w', encoding='utf-8') as f:
    json.dump(json_output, f, indent=2, ensure_ascii=False)

print(f"Data processing completed!")
print(f"Total products: {len(final_df)}")
print(f"File exported: {json_file_name}")

# Display category statistics
print("\n Category Statistics:")
print(final_df['category_main'].value_counts())
print("\n ubcategory Statistics:")
print(final_df['category_sub'].value_counts().head(10))