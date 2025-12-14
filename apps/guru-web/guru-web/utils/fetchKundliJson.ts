/**
 * Utility to fetch and display Kundli JSON from API
 * For debugging and testing purposes
 */

import { getKundli } from '@/services/api';

/**
 * Fetch and log the complete Kundli JSON response
 * @param userId - Optional user_id to fetch specific birth details
 * @returns Object with jsonString and summary for display
 */
export async function fetchAndDisplayKundliJson(userId?: string) {
  try {
    console.log('🌐 Fetching kundli JSON from API...');
    console.log(`📋 User ID: ${userId || 'none (will use default)'}`);
    console.log('');
    
    const response = await getKundli(userId);
    const jsonString = JSON.stringify(response, null, 2);
    
    console.log('✅ Complete API Response:');
    console.log('='.repeat(80));
    console.log(jsonString);
    console.log('='.repeat(80));
    
    // Summary
    let summary = '';
    if (response && (response as any).success) {
      const kundli = (response as any).data?.kundli || {};
      summary = `Success: ${(response as any).success}\n` +
                `Ascendant: ${kundli.Ascendant?.sign_sanskrit || 'N/A'} ${kundli.Ascendant?.degree || 0}°\n` +
                `Planets: ${Object.keys(kundli.Planets || {}).length} planets\n` +
                `Houses: ${Array.isArray(kundli.Houses) ? kundli.Houses.length : 0} houses\n` +
                `System: ${kundli.system || 'N/A'}\n` +
                `Ayanamsa: ${kundli.ayanamsa || 'N/A'}`;
      
      // Divisional charts
      const divisionalCharts = Object.keys(kundli).filter(k => k.startsWith('D'));
      if (divisionalCharts.length > 0) {
        summary += `\nDivisional Charts: ${divisionalCharts.join(', ')}`;
      }
      
      console.log('\n📊 Response Summary:');
      console.log(summary);
    }
    
    return {
      jsonString,
      summary,
      data: response
    };
  } catch (error: any) {
    console.error('❌ Error fetching kundli JSON:', error.message);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    }
    throw error;
  }
}

/**
 * Copy JSON to clipboard (browser only)
 */
export async function copyKundliJsonToClipboard(userId?: string) {
  try {
    const response = await getKundli(userId);
    const jsonString = JSON.stringify(response, null, 2);
    await navigator.clipboard.writeText(jsonString);
    console.log('✅ JSON copied to clipboard!');
    return jsonString;
  } catch (error: any) {
    console.error('❌ Error copying to clipboard:', error.message);
    throw error;
  }
}

