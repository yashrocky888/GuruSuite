/**
 * Chat Memory Manager
 * 
 * Manages conversation history and context
 * Stores and retrieves user interactions
 * Maintains session state
 */

/**
 * Store message in conversation history
 */
export function storeMessage(sessionId, message) {
  // TODO: Implement storage (localStorage, IndexedDB, or backend)
  const history = getConversationHistory(sessionId);
  history.push({
    ...message,
    timestamp: new Date().toISOString(),
  });
  
  // Store updated history
  if (typeof window !== 'undefined') {
    const key = `guru_chat_${sessionId}`;
    localStorage.setItem(key, JSON.stringify(history));
  }
  
  return history;
}

/**
 * Get conversation history for a session
 */
export function getConversationHistory(sessionId) {
  if (typeof window === 'undefined') {
    return [];
  }
  
  const key = `guru_chat_${sessionId}`;
  const stored = localStorage.getItem(key);
  
  if (stored) {
    try {
      return JSON.parse(stored);
    } catch (error) {
      console.error('Error parsing conversation history:', error);
      return [];
    }
  }
  
  return [];
}

/**
 * Clear conversation history for a session
 */
export function clearConversationHistory(sessionId) {
  if (typeof window !== 'undefined') {
    const key = `guru_chat_${sessionId}`;
    localStorage.removeItem(key);
  }
}

/**
 * Get recent context from conversation (last N messages)
 */
export function getRecentContext(sessionId, messageCount = 10) {
  const history = getConversationHistory(sessionId);
  return history.slice(-messageCount);
}

/**
 * Extract key topics from conversation
 */
export function extractTopics(conversationHistory) {
  const topics = new Set();
  
  // Simple keyword extraction
  const keywords = [
    'kundali', 'chart', 'prediction', 'karma', 'dasha',
    'remedy', 'muhurtha', 'planet', 'house', 'rasi',
  ];
  
  conversationHistory.forEach((message) => {
    const text = message.content?.toLowerCase() || '';
    keywords.forEach((keyword) => {
      if (text.includes(keyword)) {
        topics.add(keyword);
      }
    });
  });
  
  return Array.from(topics);
}

/**
 * Generate conversation summary
 */
export function generateSummary(sessionId) {
  const history = getConversationHistory(sessionId);
  const topics = extractTopics(history);
  
  return {
    messageCount: history.length,
    topics,
    lastMessage: history[history.length - 1]?.timestamp,
    duration: history.length > 0
      ? new Date(history[history.length - 1].timestamp) - new Date(history[0].timestamp)
      : 0,
  };
}

