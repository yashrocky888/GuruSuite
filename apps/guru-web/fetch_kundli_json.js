/**
 * Fetch Kundli JSON from API for stored birth details
 * Usage: node fetch_kundli_json.js [user_id]
 */

const axios = require('axios');

const API_BASE_URL = process.env.API_URL || 'http://localhost:8000';

async function fetchKundliJson(userId) {
  try {
    const url = `${API_BASE_URL}/api/v1/kundli`;
    const params = userId ? { user_id: userId } : {};
    
    console.log(`🌐 Fetching kundli from: ${url}`);
    console.log(`📋 Parameters:`, params);
    console.log('');
    
    const response = await axios.get(url, { params });
    
    console.log('✅ API Response:');
    console.log(JSON.stringify(response.data, null, 2));
    
    return response.data;
  } catch (error) {
    console.error('❌ Error fetching kundli:', error.message);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    }
    throw error;
  }
}

// Get user_id from command line argument or use 'test'
const userId = process.argv[2] || 'test';

fetchKundliJson(userId)
  .then(() => {
    console.log('\n✅ Done!');
    process.exit(0);
  })
  .catch((error) => {
    console.error('\n❌ Failed!');
    process.exit(1);
  });

