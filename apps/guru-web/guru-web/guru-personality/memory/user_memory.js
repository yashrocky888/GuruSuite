/**
 * User Memory Manager
 * 
 * Manages user-specific memory for personalization
 * Stores preferences, interaction history, and insights
 */

/**
 * Load user memory
 */
export function loadUserMemory(userId) {
  if (typeof window === 'undefined' || !userId) {
    return getDefaultMemory();
  }
  
  const key = `guru_user_memory_${userId}`;
  const stored = localStorage.getItem(key);
  
  if (stored) {
    try {
      return JSON.parse(stored);
    } catch (error) {
      console.error('Error parsing user memory:', error);
      return getDefaultMemory();
    }
  }
  
  return getDefaultMemory();
}

/**
 * Save user memory
 */
export function saveUserMemory(userId, memory) {
  if (typeof window === 'undefined' || !userId) {
    return;
  }
  
  const key = `guru_user_memory_${userId}`;
  const updatedMemory = {
    ...memory,
    lastUpdated: new Date().toISOString(),
  };
  
  try {
    localStorage.setItem(key, JSON.stringify(updatedMemory));
  } catch (error) {
    console.error('Error saving user memory:', error);
  }
}

/**
 * Update user memory with new interaction
 */
export function updateUserMemory(userId, interaction) {
  const memory = loadUserMemory(userId);
  
  memory.interactions.totalSessions += 1;
  memory.interactions.lastInteraction = new Date().toISOString();
  
  if (interaction.topic) {
    if (!memory.interactions.favoriteTopics.includes(interaction.topic)) {
      memory.interactions.favoriteTopics.push(interaction.topic);
    }
  }
  
  if (interaction.question) {
    memory.interactions.askedQuestions.push({
      question: interaction.question,
      timestamp: new Date().toISOString(),
    });
  }
  
  saveUserMemory(userId, memory);
  return memory;
}

/**
 * Get default memory structure
 */
function getDefaultMemory() {
  return {
    userId: null,
    preferences: {
      communicationStyle: 'balanced',
      spiritualLevel: 'beginner',
      language: 'en',
    },
    interactions: {
      totalSessions: 0,
      lastInteraction: null,
      favoriteTopics: [],
      askedQuestions: [],
    },
    birthDetails: {
      stored: false,
      lastUpdated: null,
    },
    insights: {
      keyFindings: [],
      remediesSuggested: [],
      predictionsRequested: [],
    },
  };
}

/**
 * Store birth details in user memory
 */
export function storeBirthDetails(userId, birthDetails) {
  const memory = loadUserMemory(userId);
  
  memory.birthDetails = {
    ...birthDetails,
    stored: true,
    lastUpdated: new Date().toISOString(),
  };
  
  saveUserMemory(userId, memory);
  return memory;
}

