
export const useSolr = () => {
  const SOLR_BASE_URL = '/solr/solr/fastfood_menu'
  
  // Search products
  const searchProducts = async (query, options = {}) => {
    try {
      const params = new URLSearchParams({
        q: query || '*:*',
        wt: 'json',
        rows: options.rows || 50,
        defType: 'edismax',
        qf: 'product_name^6.0 category_main^4.0 category_sub^3.0 description^2.5 ingredients_text^2.0',
        bf: 'log(sum(1,popularity_score))^1.5',
        ...options
      })
      
      const response = await fetch(`${SOLR_BASE_URL}/fastfood_search?${params}`)
      if (!response.ok) {
        throw new Error(`Solr search failed: ${response.status}`)
      }
      
      const data = await response.json()
      return data.response?.docs || []
    } catch (error) {
      console.error('Search error:', error)
      return []
    }
  }
  
  // Like function - Direct atomic update to Solr
  const likeProduct = async (productId) => {
    try {
      const updateUrl = `${SOLR_BASE_URL}/update?commit=true`
      const updateData = [{
        id: productId,
        popularity_score: { inc: 1 }  // Atomic update!
      }]
      
      const response = await fetch(updateUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updateData)
      })
      
      if (!response.ok) {
        throw new Error('Like update failed')
      }
      
      return true
    } catch (error) {
      console.error('Like error:', error)
      return false
    }
  }

  // Get list of brands
  const getBrands = async () => {
    try {
      const params = new URLSearchParams({
        q: '*:*',
        wt: 'json',
        rows: '0',
        'facet': 'true',
        'facet.field': 'brand'
      })
      
      const response = await fetch(`${SOLR_BASE_URL}/select?${params}`)
      const data = await response.json()
      return data.facet_counts?.facet_fields?.brand || []
    } catch (error) {
      console.error('Get brands error:', error)
      return []
    }
  }
  
  return {
    searchProducts,
    likeProduct,
    getBrands
  }
}