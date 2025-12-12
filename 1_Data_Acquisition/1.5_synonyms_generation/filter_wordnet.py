#!/usr/bin/env python3
# save as generate_fastfood_synonyms_V3.py

import json
import re
from typing import Dict, List, Set
from collections import Counter
import string
import os

# ==============================================================================
# Dependency Library (NLTK)
# ==============================================================================
try:
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    lemmatizer = WordNetLemmatizer()
except ImportError:
    print("\n Error: NLTK library not found. Please install it first.")
    exit()

# Predefined custom rules (manually set semantic synonyms)
PREDEFINED_RULES: Dict[str, List[str]] = {
    'mcdonalds': ['mcd', "mcdonald's"],
    'kfc': ['kentucky_fried_chicken'],
    'wendys': ["wendy's"],
    'burger': ['hamburger', 'beefburger', 'cheeseburger', 'baconator', 'mac', 'stack'], 
    'fries': ['chips', 'french_fries', 'potato_sides', 'hash_browns'],
    'ketchup': ['tomato_ketchup', 'heinz_ketchup'],
    'wrap': ['tortilla', 'flatbread', 'bap', 'butty', 'twister'],
    'chicken': ['fowl', 'poultry', 'nugget', 'tender', 'select', 'mini_fillet', 'popcorn_chicken'],
    'beef': ['pure_beef', 'beef_patty', 'quarter_pounder'],
    'cheese': ['cheddar_cheese', 'american_cheese', 'gouda_cheese', 'milk_protein', 'cheesy'],
    'dessert': ['sundae', 'mcflurry', 'frosty', 'pie', 'brownie', 'cookie', 'muffin']
}

# ==============================================================================
# Core synonym generation logic (based on predefined rules only)
# ==============================================================================

def generate_strict_synonyms(initial_rules: Dict[str, List[str]]) -> List[str]:
    """
    Generate Solr-compatible multi-valued bidirectional synonym rules (A, B, C => A, B, C) based only on manually defined rules.
    """
    print("\nStarting strict synonym generation (disabling WordNet expansion)...")
    
    synonym_network = {} 
    
    # 1. Initialize and integrate predefined rules (forced connection)
    for standard_word, synonyms in initial_rules.items():
        group = {standard_word} | set(synonyms)
        for term in group:
            if term not in synonym_network:
                synonym_network[term] = set()
            synonym_network[term].update(group)
    
    # 2. Calculate transitive closures and generate final rules (logic remains unchanged, but the data source is clean).
    final_rules = []
    processed_words_in_groups = set()
    
    for word in sorted(synonym_network.keys()):
        if word in processed_words_in_groups:
            continue
        
        current_group = set()
        stack = [word]
        
        # Find all connected synonyms
        while stack:
            current = stack.pop()
            if current not in current_group:
                current_group.add(current)
                if current in synonym_network:
                    stack.extend(synonym_network[current] - current_group)
        
        if len(current_group) > 1:
            # Ensure vocabulary is cleaned and sorted
            clean_synonyms = sorted([s.replace('_', ' ').replace("'", "") for s in current_group if len(s) > 1])
            
            if len(clean_synonyms) > 1:
                # Solr's recommended multi-valued bidirectional format: A, B, C => A, B, C
                terms_string = ', '.join(clean_synonyms)
                rule_string = f"{terms_string} => {terms_string}"
                final_rules.append(rule_string)
                
                processed_words_in_groups.update(current_group) 


    final_output = sorted(list(set(final_rules)))
    
    print(f"✓ Final Solr-compatible synonym generation completed: {len(final_output)} rules created.")
    return final_output

# ==============================================================================
# 3. Main Function
# ==============================================================================

def main():
    """The main function generates synonyms and exports them to a file."""
    print("Starting: Data-driven Solr Synonym Generation (V3.0 - Strict Domain Only)...")
    
    final_rules = generate_strict_synonyms(PREDEFINED_RULES)
    
    output_filename = 'synonyms.txt'
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write("# Fast Food Domain Synonyms - FINAL Solr-Compatible Mapping (V3.0)\n")
        f.write("# NOTE: WordNet semantic expansion has been removed to prevent noise.\n")
        f.write("# This file only contains manually defined domain synonyms (e.g., burger <-> hamburger).\n\n")
        
        for rule in final_rules:
            f.write(rule + '\n')
    
    total_rules = len(final_rules)
    print(f"\n✓ Final synonym file generation completed: {output_filename}")
    print(f"✓ Total rule count: {total_rules}")

if __name__ == "__main__":
    main()