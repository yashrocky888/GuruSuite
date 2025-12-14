/**
 * Format Guru Response
 * 
 * Formats raw Guru responses with proper structure,
 * spiritual elements, and visual formatting
 */

/**
 * Format a Guru response message
 */
export function formatGuruResponse(message, options = {}) {
  const {
    context = 'general',
    userMemory = null,
    timestamp = new Date(),
    includeGreeting = true,
  } = options;
  
  let formatted = message;
  
  // Add greeting if appropriate
  if (includeGreeting && !formatted.toLowerCase().startsWith('namaste') && 
      !formatted.toLowerCase().startsWith('hello') &&
      !formatted.toLowerCase().startsWith('welcome')) {
    formatted = addSpiritualGreeting(formatted, context);
  }
  
  // Add personalization based on user memory
  if (userMemory && userMemory.preferences) {
    formatted = personalizeResponse(formatted, userMemory.preferences);
  }
  
  // Add closing blessing if appropriate
  if (shouldAddBlessing(context)) {
    formatted = addClosingBlessing(formatted);
  }
  
  return formatted;
}

/**
 * Add spiritual greeting
 */
function addSpiritualGreeting(message, context) {
  const greetings = [
    'Namaste, seeker.',
    'Blessings to you.',
    'May the cosmic forces guide you.',
  ];
  
  const greeting = greetings[Math.floor(Math.random() * greetings.length)];
  return `${greeting} ${message}`;
}

/**
 * Personalize response based on user preferences
 */
function personalizeResponse(message, preferences) {
  // Adjust communication style
  if (preferences.communicationStyle === 'concise') {
    // Make message more concise
    return message.split('\n\n')[0] + '\n\n' + message.split('\n\n').slice(1).join(' ');
  } else if (preferences.communicationStyle === 'detailed') {
    // Ensure message has sufficient detail
    if (message.length < 200) {
      return message + '\n\nFor deeper insights, consider exploring your full chart analysis.';
    }
  }
  
  return message;
}

/**
 * Determine if closing blessing should be added
 */
function shouldAddBlessing(context) {
  const contextsWithBlessing = ['karma', 'remedy', 'chart', 'daily'];
  return contextsWithBlessing.includes(context);
}

/**
 * Add closing blessing
 */
function addClosingBlessing(message) {
  const blessings = [
    '\n\nMay the planets align in your favor. 🙏',
    '\n\nWishing you peace and prosperity on your journey. ✨',
    '\n\nMay the divine light guide your path. 🌟',
  ];
  
  const blessing = blessings[Math.floor(Math.random() * blessings.length)];
  
  // Only add if not already present
  if (!message.includes('🙏') && !message.includes('✨') && !message.includes('🌟')) {
    return message + blessing;
  }
  
  return message;
}

/**
 * Format response for display (add line breaks, emphasis)
 */
export function formatForDisplay(message) {
  // Add line breaks after sentences for better readability
  let formatted = message.replace(/\. /g, '.\n\n');
  
  // Preserve existing line breaks
  formatted = formatted.replace(/\n\n\n+/g, '\n\n');
  
  return formatted;
}

