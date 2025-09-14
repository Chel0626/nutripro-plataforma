/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NUTRITION_API_URL: process.env.NUTRITION_API_URL || 'http://localhost:8001/api/v1',
  },
}

module.exports = nextConfig