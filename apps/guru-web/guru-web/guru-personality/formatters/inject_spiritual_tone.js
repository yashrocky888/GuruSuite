/**
 * Inject Spiritual Tone
 * 
 * Enhances messages with spiritual language,
 * Sanskrit terms, and Vedic wisdom
 */

/**
 * Inject spiritual tone into a message
 */
export function injectSpiritualTone(message, context = 'general') {
  let enhanced = message;
  
  // Add spiritual phrases based on context
  enhanced = addContextualPhrases(enhanced, context);
  
  // Replace technical terms with spiritual alternatives where appropriate
  enhanced = replaceWithSpiritualTerms(enhanced);
  
  // Add Sanskrit terms for emphasis
  enhanced = addSanskritTerms(enhanced, context);
  
  return enhanced;
}

/**
 * Add contextual spiritual phrases
 */
function addContextualPhrases(message, context) {
  const phrases = {
    chart: [
      'As the stars align in your chart',
      'The cosmic blueprint reveals',
      'Your birth chart, a map of destiny',
    ],
    daily: [
      'Today, the cosmic energies',
      'The planets today guide you',
      'On this auspicious day',
    ],
    karma: [
      'Your karmic journey unfolds',
      'The wheel of karma turns',
      'Dharma calls to you',
    ],
    remedy: [
      'To align with cosmic harmony',
      'These sacred practices',
      'Through these remedies, the planets',
    ],
  };
  
  const contextPhrases = phrases[context] || phrases.chart;
  // For now, just return message - can be enhanced later
  return message;
}

/**
 * Replace technical terms with spiritual alternatives
 */
function replaceWithSpiritualTerms(message) {
  const replacements = {
    'astrological chart': 'cosmic blueprint',
    'planetary positions': 'celestial alignments',
    'prediction': 'cosmic guidance',
    'unfavorable': 'challenging period for growth',
    'favorable': 'auspicious alignment',
  };
  
  let enhanced = message;
  for (const [technical, spiritual] of Object.entries(replacements)) {
    enhanced = enhanced.replace(new RegExp(technical, 'gi'), spiritual);
  }
  
  return enhanced;
}

/**
 * Add Sanskrit terms where appropriate
 */
function addSanskritTerms(message, context) {
  const sanskritTerms = {
    chart: ['Kundali', 'Rasi', 'Graha'],
    daily: ['Tithi', 'Nakshatra', 'Yoga'],
    karma: ['Karma', 'Dharma', 'Moksha'],
    remedy: ['Upaya', 'Mantra', 'Puja'],
  };
  
  // For now, return message as-is
  // Can be enhanced to intelligently insert Sanskrit terms
  return message;
}

/**
 * Add spiritual emphasis to key points
 */
export function addEmphasis(message, keyPoints) {
  // Add emphasis markers or formatting to key points
  let enhanced = message;
  
  keyPoints.forEach((point) => {
    const regex = new RegExp(`(${point})`, 'gi');
    enhanced = enhanced.replace(regex, '**$1**'); // Markdown bold
  });
  
  return enhanced;
}

