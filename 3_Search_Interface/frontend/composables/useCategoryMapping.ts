
export const categoryMapping: Record<string, { main: string; sub: string }> = {
  'Breakfast Menu': { main: 'Breakfast', sub: 'Breakfast Sandwiches' },
  'Breakfast Sandwiches': { main: 'Breakfast', sub: 'Breakfast Sandwiches' },
  'Breakfast Wraps': { main: 'Breakfast', sub: 'Breakfast Wraps' },
  'Breakfast Combos': { main: 'Breakfast', sub: 'Breakfast Combos' },
  'Breakfast Saver Menu®': { main: 'Breakfast', sub: 'Breakfast Combos' },
  'Breakfast Sides': { main: 'Breakfast', sub: 'Breakfast Sides' },
  'Burgers': { main: 'Main', sub: 'Beef Burgers' },
  'Hamburgers': { main: 'Main', sub: 'Beef Burgers' },
  'Chicken Sandwiches': { main: 'Main', sub: 'Chicken Sandwiches' },
  'Twisters': { main: 'Main', sub: 'Wraps' },
  'Wraps': { main: 'Main', sub: 'Wraps' },
  'Wraps & Salads': { main: 'Main', sub: 'Wraps' },
  'Fresh-Made Salads': { main: 'Main', sub: 'Salads' },
  'Rice Bowls': { main: 'Main', sub: 'Bowls' },
  'Veggie Options': { main: 'Main', sub: 'Vegetarian' },
  'Vegetarian': { main: 'Main', sub: 'Vegetarian' },
  'Vegan': { main: 'Main', sub: 'Vegetarian' },
  'McNuggets®, Selects® & Veggie Dippers': { main: 'Main', sub: 'Chicken Pieces & Veggie Dippers' },
  'Just Chicken': { main: 'Main', sub: 'Chicken Pieces & Veggie Dippers' },
  'Chicken Nuggets & Tenders': { main: 'Main', sub: 'Chicken Pieces & Veggie Dippers' },
  'Kfc Sharing Buckets': { main: 'Main', sub: 'Chicken Buckets' },
  'Kids Buckets': { main: 'Main', sub: 'Chicken Buckets' },
  'Buckets For One': { main: 'Main', sub: 'Chicken Buckets' },
  'Combos': { main: 'Main', sub: 'Combos' },
  'Box Meals': { main: 'Main', sub: 'Combos' },
  'Biggie Deals': { main: 'Main', sub: 'Combos' },
  'Sharers & Bundles': { main: 'Main', sub: 'Combos' },
  'Fries & Sides': { main: 'Sides', sub: 'Potato Sides' },
  'Sides Dips': { main: 'Sides', sub: 'Dips & Sauces' },
  'Condiments And Sauces': { main: 'Sides', sub: 'Dips & Sauces' },
  'McCafé®': { main: 'Drinks', sub: 'Hot Drinks' },
  'Coffee & Beverages': { main: 'Drinks', sub: 'Hot Drinks' },
  'Milkshakes & Cold Drinks': { main: 'Drinks', sub: 'Cold Drinks' },
  'Frosty®': { main: 'Drinks', sub: 'Frozen Treats' },
  'Drinks': { main: 'Drinks', sub: 'Soft Drinks' },
  'Desserts': { main: 'Desserts', sub: 'Sweets & Bakery' },
  'Happy Meal®': { main: 'Kids', sub: 'Kids Meals' },
  "Wendy's Kids' Meal": { main: 'Kids', sub: 'Kids Meals' },
  'Saver Menu®': { main: 'Value', sub: 'Value Meals' },
  "What's New": { main: 'Promotional', sub: 'Limited Time' },
  'Whats New': { main: 'Promotional', sub: 'Limited Time' },
  'World Menu Heist': { main: 'Promotional', sub: 'Limited Time' },
}

// Get the main category and subcategory for a given original category
export function getCategoryMapping(originalCategory: string): { main: string; sub: string } {
  return categoryMapping[originalCategory] || { main: 'Other', sub: originalCategory }
}

// Get all main categories
export function getMainCategories(): string[] {
  const mainCats = new Set<string>()
  Object.values(categoryMapping).forEach(({ main }) => {
    mainCats.add(main)
  })
  return Array.from(mainCats).sort()
}

// Get subcategories based on the main category
export function getSubCategories(mainCategory: string): string[] {
  const subCats = new Set<string>()
  Object.values(categoryMapping).forEach(({ main, sub }) => {
    if (main === mainCategory) {
      subCats.add(sub)
    }
  })
  return Array.from(subCats).sort()
}

// Get the structure of all main categories and their subcategories
export function getCategoryStructure(): Record<string, string[]> {
  const structure: Record<string, string[]> = {}
  getMainCategories().forEach((main) => {
    structure[main] = getSubCategories(main)
  })
  return structure
}

