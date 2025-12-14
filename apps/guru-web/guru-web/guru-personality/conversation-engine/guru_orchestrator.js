/**
 * Guru Orchestrator
 * 
 * Coordinates the Guru personality engine
 * Routes conversations based on context and intent
 * Manages prompt selection and response formatting
 */

import { formatGuruResponse } from '../formatters/format_guru_response.js';
import { injectSpiritualTone } from '../formatters/inject_spiritual_tone.js';
import { loadUserMemory } from '../memory/user_memory.js';

/**
 * Determine conversation context and select appropriate prompt template
 */
export function determineContext(userMessage, conversationHistory = []) {
  const message = userMessage.toLowerCase();
  
  // Context detection patterns
  const contexts = {
    chart: ['kundali', 'birth chart', 'chart', 'planets', 'houses', 'rasi'],
    daily: ['today', 'daily', 'day', 'today\'s prediction'],
    monthly: ['month', 'monthly', 'this month'],
    yearly: ['year', 'yearly', 'annual'],
    karma: ['karma', 'karmic', 'soul', 'past life', 'dharma'],
    remedy: ['remedy', 'remedies', 'gemstone', 'mantra', 'puja', 'solution'],
    dasha: ['dasha', 'mahadasha', 'antardasha', 'planetary period'],
    muhurtha: ['muhurtha', 'auspicious', 'timing', 'best time'],
    general: ['hello', 'hi', 'help', 'what can you do'],
  };
  
  // Find matching context
  for (const [context, keywords] of Object.entries(contexts)) {
    if (keywords.some(keyword => message.includes(keyword))) {
      return context;
    }
  }
  
  // Default to general if no specific context
  return 'general';
}

/**
 * Load appropriate prompt template based on context
 */
export async function loadPromptTemplate(context) {
  const templates = {
    chart: 'guru_chart_explain.txt',
    daily: 'guru_daily_message.txt',
    monthly: 'guru_daily_message.txt', // Can be customized
    yearly: 'guru_daily_message.txt',
    karma: 'guru_karmic_report.txt',
    remedy: 'guru_remedy_guide.txt',
    dasha: 'guru_default.txt',
    muhurtha: 'guru_default.txt',
    general: 'guru_default.txt',
  };
  
  const templateName = templates[context] || 'guru_default.txt';
  
  // TODO: Load from file system or API
  // For now, return template name
  return templateName;
}

/**
 * Orchestrate Guru response generation
 */
export async function orchestrateGuruResponse(userMessage, conversationHistory = [], userContext = {}) {
  try {
    // Determine conversation context
    const context = determineContext(userMessage, conversationHistory);
    
    // Load appropriate prompt template
    const templateName = await loadPromptTemplate(context);
    
    // Load user memory for personalization
    const userMemory = await loadUserMemory(userContext.userId);
    
    // TODO: Call AI/LLM service with:
    // - Selected prompt template
    // - User message
    // - Conversation history
    // - User memory/context
    // - API response data (if applicable)
    
    // For now, generate placeholder response
    let response = `I understand you're asking about ${context}. Let me provide guidance...`;
    
    // Format response with spiritual tone
    response = injectSpiritualTone(response, context);
    
    // Format final response
    response = formatGuruResponse(response, {
      context,
      userMemory,
      timestamp: new Date(),
    });
    
    return {
      message: response,
      context,
      template: templateName,
      timestamp: new Date(),
    };
  } catch (error) {
    console.error('Error orchestrating Guru response:', error);
    return {
      message: 'I apologize, but I encountered an issue. Please try again, and may the cosmic forces guide you.',
      context: 'error',
      timestamp: new Date(),
    };
  }
}

/**
 * Process API response and generate Guru explanation
 */
export async function processApiResponse(apiData, context, userMessage) {
  // TODO: Transform API response into Guru's explanation
  // This will format raw astrological data into spiritual guidance
  
  return {
    explanation: 'Guru explanation of API data will be generated here',
    insights: [],
    recommendations: [],
  };
}

