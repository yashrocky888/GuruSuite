'use client';

/**
 * Guru Reading Component
 * Displays AI-generated interpretations
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { SparklesIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { getGuruInterpretation, GuruRequest } from '@/services/api';

interface GuruReadingProps {
  chartData?: any;
  question?: string;
}

export default function GuruReading({ chartData, question }: GuruReadingProps) {
  const [reading, setReading] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [userQuestion, setUserQuestion] = useState(question || '');

  const fetchReading = async () => {
    if (!userQuestion.trim() && !chartData) {
      setError('Please provide a question or chart data');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const request: GuruRequest = {
        message: userQuestion || 'Explain this chart',
        chart_data: chartData,
        context: 'You are a Vedic astrology guru providing spiritual guidance.',
      };

      const response = await getGuruInterpretation(request);
      setReading(response.response || response.message || 'No response received');
    } catch (err: any) {
      setError(err.message || 'Failed to get Guru reading');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-2xl p-6 md:p-8 border border-white/20"
    >
      <div className="flex items-center mb-6">
        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-amber-400 to-yellow-500 flex items-center justify-center mr-4">
          <SparklesIcon className="w-6 h-6 text-white" />
        </div>
        <h3 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
          Guru's Interpretation
        </h3>
      </div>

      {/* Question Input */}
      <div className="mb-6">
        <textarea
          value={userQuestion}
          onChange={(e) => setUserQuestion(e.target.value)}
          placeholder="Ask the Guru about your chart, predictions, or any astrological question..."
          className="w-full px-4 py-3 rounded-lg glass border border-white/20 focus:outline-none focus:ring-2 focus:ring-purple-500 text-gray-900 dark:text-gray-100 resize-none"
          rows={3}
        />
      </div>

      {/* Get Reading Button */}
      <motion.button
        onClick={fetchReading}
        disabled={loading}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className="w-full py-3 rounded-lg bg-gradient-to-r from-amber-500 to-yellow-500 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-smooth mb-6"
      >
        {loading ? (
          <>
            <ArrowPathIcon className="w-5 h-5 mr-2 animate-spin" />
            Getting Reading...
          </>
        ) : (
          <>
            <SparklesIcon className="w-5 h-5 mr-2" />
            Get Guru's Reading
          </>
        )}
      </motion.button>

      {/* Error */}
      {error && (
        <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 mb-6">
          {error}
        </div>
      )}

      {/* Reading Display */}
      {reading && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 rounded-lg bg-gradient-to-br from-amber-50/50 to-yellow-50/50 dark:from-amber-900/20 dark:to-yellow-900/20 border border-amber-200/30 dark:border-amber-800/30"
        >
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
              {reading}
            </p>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}

