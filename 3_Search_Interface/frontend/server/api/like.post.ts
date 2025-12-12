export default defineEventHandler(async (event) => {
  const body = await readBody(event);
  const { productId } = body; // Remove action parameter

  if (!productId) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Product ID is required'
    });
  }

  try {
    // Update the likes field in Solr - only supports increment
    const updateResponse = await $fetch('http://localhost:8983/solr/fastfood_menu/update?commit=true', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify([{
        id: productId,
        likes: { inc: 1 } // Only supports increment
      }])
    });

    return { 
      success: true, 
      productId
    };
  } catch (error) {
    console.error('Solr update error:', error);
    throw createError({
      statusCode: 500,
      statusMessage: 'Like action failed'
    });
  }
});