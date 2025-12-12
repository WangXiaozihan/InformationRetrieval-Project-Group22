import pandas as pd
import json
import re

# 1. Load JSON Data
file_name = "fast_food_menu_final.json"
try:
    with open(file_name, 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"Error: File '{file_name}' not found. Please ensure the file is in the correct directory.")
    # Exit if file is missing
    exit()

df = pd.DataFrame(data)

# 2. HTML Cleaning Function - Used ONLY for building the search index field
def clean_html_and_whitespace(text):
    """Removes HTML tags and excessive whitespace from a string."""
    if pd.isna(text) or text is None:
        return ""
    text = str(text)
    # Remove HTML tags (e.g., <strong>, <br />, <span>)
    text = re.sub(r'<[^>]+>', '', text)
    # Remove excessive whitespace, newlines, and escape characters
    text = re.sub(r'[\n\r]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    # Remove common placeholders like "{}" and trim spaces
    text = text.replace('{}', '').strip()
    return text

# 3. Prepare cleaned text for the merged field
# Deep cleaning is applied primarily to the noisy ingredients text
cleaned_ingredients_text = df['ingredients_text'].apply(clean_html_and_whitespace)

# Clean and concatenate category fields to ensure clean indexing terms
cleaned_categories = (df['original_category'].fillna('') + ' ' + 
                      df['category_main'].fillna('') + ' ' + 
                      df['category_sub'].fillna('')).apply(clean_html_and_whitespace)


# 4. Create the "Catch-All" Search Field (catch_all_text)
# Concatenate fields: product_name (Original) + description (Original) + cleaned categories + cleaned ingredients text
df['catch_all_text'] = df['product_name'].fillna('') + ' ' + \
                      df['description'].fillna('') + ' ' + \
                      cleaned_categories.fillna('') + ' ' + \
                      cleaned_ingredients_text.fillna('')

# Final cleanup of excessive spaces in the merged field
df['catch_all_text'] = df['catch_all_text'].str.replace(r'\s+', ' ', regex=True).str.strip()


# 5. Add custom feature field (User Relevance Feedback)
# 'popularity_score' (Solr pint): Initialized to 0 for boosting/sorting
df['popularity_score'] = 0

# 6. Save the processed data to a new JSON file for Solr import
processed_file_name = "fast_food_menu_for_solr_V3.json"
# Use df.to_json to ensure proper JSON format for Solr
df.to_json(processed_file_name, orient='records', force_ascii=False, indent=2)

print(f"Data cleaning and preprocessing completed.")
print(f"The new Solr import file is: {processed_file_name}")
print("\n--- Key Fields Preview (Using built-in method to avoid 'tabulate' dependency) ---")
# Use to_string() to print the head to avoid the 'tabulate' dependency issue
print(df[['id', 'product_name', 'description', 'catch_all_text', 'popularity_score']].head().to_string(index=False))