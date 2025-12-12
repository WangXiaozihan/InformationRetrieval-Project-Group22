// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  // Tailwind CSS Module
  modules: ['@nuxtjs/tailwindcss'],

  // Tailwind CSS Configuration
  tailwindcss: {
    cssPath: '~/assets/css/main.css',
    exposeConfig: false,
    viewer: true,
  },

  // PostCSS Configuration
  postcss: {
    plugins: {
      tailwindcss: {},
      autoprefixer: {},
    },
  },

  // App Configuration
  app: {
    head: {
      title: 'Foodle - Nutrition Explorer',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
        { href: 'https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;500;600;700&display=swap', rel: 'stylesheet' }
      ]
    }
  },

  // Development Server Configuration
  devServer: {
    port: 3000
  },

  // Nitro Configuration - Add Solr Proxy
  nitro: {
    devProxy: {
      '/solr': {
        target: 'http://localhost:8983',
        changeOrigin: true
      }
    }
  }
})