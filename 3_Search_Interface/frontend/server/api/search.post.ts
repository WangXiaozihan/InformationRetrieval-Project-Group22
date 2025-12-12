export default defineEventHandler(async (event) => {
  const body = await readBody(event);
  const { query = '', filters = {} } = body;

  try {
    // Solr Query Logic
    const solrQuery = buildSolrQuery(query, filters);
    const solrResponse = await $fetch('http://localhost:8983/solr/food/select', {
      method: 'GET',
      params: solrQuery
    });

    return normalizeSolrResponse(solrResponse);
  } catch (error) {
    console.error('Solr search error:', error);
    throw createError({
      statusCode: 500,
      statusMessage: 'Search failed'
    });
  }
});

function buildSolrQuery(query: string, filters: any) {
  const params: any = {
    q: query || '*:*',
    wt: 'json',
    rows: 1000
  };

  // Add filter conditions
  const fq = [];
  
  if (filters.category && filters.category !== 'All') {
    if (filters.category.includes(' > ')) {
      const [mainCat, subCat] = filters.category.split(' > ');
      fq.push(`category_main:"${mainCat}" AND category_sub:"${subCat}"`);
    } else {
      fq.push(`category_main:"${filters.category}"`);
    }
  }
  
  if (filters.company && filters.company !== 'All') {
    fq.push(`brand:"${filters.company}"`);
  }
  
  if (filters.salt) {
    fq.push(`salt_g:[0 TO ${filters.salt}]`);
  }
  
  if (filters.fat) {
    fq.push(`fat_g:[0 TO ${filters.fat}]`);
  }
  
  if (filters.calories) {
    fq.push(`calories_kcal:[0 TO ${filters.calories}]`);
  }

  if (fq.length > 0) {
    params.fq = fq;
  }

  return params;
}

function normalizeSolrResponse(solrResponse: any) {
  if (!solrResponse.response?.docs) return [];
  
  return solrResponse.response.docs.map((doc: any) => ({
    product_id: doc.id.toString(),
    name: doc.product_name,
    company: doc.brand,
    category: `${doc.category_main} > ${doc.category_sub}`,
    description: doc.description,
    image_url: doc.image_url,
    calories: doc.calories_kcal,
    fat: doc.fat_g,
    salt: doc.salt_g,
    protein: doc.protein_g,
    carbs: doc.carbs_g,
    sugar: doc.sugar_g,
    // Changed to likes and dislikes
    likes: doc.likes || 0,
    dislikes: doc.dislikes || 0,
    nutrition: {
      summary: {
        calories: doc.calories_kcal,
        protein: doc.protein_g,
        fat: doc.fat_g,
        carbohydrates: doc.carbs_g,
        sugar: doc.sugar_g,
        salt: doc.salt_g
      }
    },
    allergens_ingredients: {
      ingredients: doc.components_list || [],
      allergens_contains: [],
      allergens_may_contain: [],
      allergy_advice: '',
      preparation_notes: ''
    },
    url: doc.url
  }));
}