'use client';

/**
 * Birth Details Form Component
 * Collects user birth information
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { CalendarIcon, ClockIcon, MapPinIcon } from '@heroicons/react/24/outline';
import { useBirthStore } from '@/store/useBirthStore';
import { submitBirthDetails, BirthDetails, LocationSuggestion } from '@/services/api';
import { FadeIn, SlideUp } from '@/frontend/animations';
import LocationAutocomplete from './LocationAutocomplete';

export default function BirthDetailsForm() {
  const router = useRouter();
  const { setBirthDetails, clearBirthDetails, birthDetails, setUserId, setLagna } = useBirthStore();
  
  // Local form state (includes 'place' for UI, but submits as city/country)
  const [formData, setFormData] = useState<{
    date?: string;
    time?: string;
    place?: string;
    city?: string;
    country?: string;
    latitude?: number;
    longitude?: number;
    timezone?: string;
  }>({
    date: birthDetails?.date || '',
    time: birthDetails?.time || '',
    place: birthDetails ? `${birthDetails.city}, ${birthDetails.country}` : '',
    city: birthDetails?.city || '',
    country: birthDetails?.country || '',
    latitude: birthDetails?.latitude || 0,
    longitude: birthDetails?.longitude || 0,
    timezone: birthDetails?.timezone || '',
  });
  
  const [selectedLocation, setSelectedLocation] = useState<LocationSuggestion | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Update coordinates when location is selected
  useEffect(() => {
    if (selectedLocation) {
      setFormData(prev => ({
        ...prev,
        latitude: selectedLocation.latitude,
        longitude: selectedLocation.longitude,
        place: selectedLocation.displayName,
      }));
    }
  }, [selectedLocation]);

  const handleClear = () => {
    clearBirthDetails();
    setFormData({
      date: '',
      time: '',
      place: '',
      latitude: 0,
      longitude: 0,
    });
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      // Validate form
      if (!formData.date || !formData.time || !formData.place) {
        throw new Error('Please fill in all required fields');
      }

      // Get coordinates from selected location or form data
      const details: BirthDetails = {
        date: formData.date!,
        time: formData.time!,
        city: formData.city!,
        country: formData.country!,
        latitude: formData.latitude || 0,
        longitude: formData.longitude || 0,
        timezone: formData.timezone,
      };

      // Submit to backend
      const response = await submitBirthDetails(details);
      
      // Store in Zustand
      setBirthDetails(details);
      
      // Store user_id and lagna from API response
      if (response.user_id) {
        setUserId(response.user_id);
      }
      if (response.lagna && response.lagnaSign) {
        setLagna(response.lagna, response.lagnaSign);
      }
      
      // Redirect to dashboard
      router.push('/dashboard');
    } catch (err: any) {
      // Better error handling
      let errorMessage = 'Failed to submit birth details';
      
      // Check if it's a 404 error (endpoint not found)
      if (err?.response?.status === 404) {
        // This is handled by the API service workaround, but just in case
        errorMessage = 'Birth details endpoint not available. Using local storage.';
      } else if (err.message) {
        errorMessage = err.message;
      } else if ((err as any).response?.data) {
        const errorData = (err as any).response.data;
        // Handle FastAPI error format
        if (typeof errorData === 'string') {
          errorMessage = errorData;
        } else if (errorData.detail) {
          if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          } else if (errorData.detail.message) {
            errorMessage = errorData.detail.message;
          } else {
            errorMessage = errorData.detail.error || JSON.stringify(errorData.detail);
          }
        } else if (errorData.message) {
          errorMessage = errorData.message;
        } else if (errorData.error) {
          errorMessage = errorData.error;
        }
      } else if ((err as any).code === 'ECONNREFUSED' || (err as any).message?.includes('Network Error')) {
        errorMessage = 'Cannot connect to server. Please ensure the backend is running on port 8000.';
      } else if ((err as any).response?.status === 404) {
        errorMessage = 'API endpoint not found. Please check backend configuration.';
      } else if ((err as any).response?.status >= 500) {
        errorMessage = 'Server error. Please try again later.';
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SlideUp>
      <div className="glass rounded-2xl p-8 md:p-12 border border-white/20 max-w-2xl mx-auto">
        <FadeIn>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-2">
            Enter Your Birth Details
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-8">
            Provide your birth information to generate your personalized astrological chart
          </p>
        </FadeIn>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              <CalendarIcon className="w-4 h-4 inline mr-2" />
              Birth Date
            </label>
            <input
              type="date"
              required
              value={formData.date}
              onChange={(e) => setFormData({ ...formData, date: e.target.value })}
              className="w-full px-4 py-3 rounded-lg glass border border-white/20 focus:outline-none focus:ring-2 focus:ring-purple-500 text-gray-900 dark:text-gray-100"
            />
          </div>

          {/* Time */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              <ClockIcon className="w-4 h-4 inline mr-2" />
              Birth Time
            </label>
            <input
              type="time"
              required
              value={formData.time}
              onChange={(e) => setFormData({ ...formData, time: e.target.value })}
              className="w-full px-4 py-3 rounded-lg glass border border-white/20 focus:outline-none focus:ring-2 focus:ring-purple-500 text-gray-900 dark:text-gray-100"
            />
          </div>

          {/* Place - Autocomplete */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              <MapPinIcon className="w-4 h-4 inline mr-2" />
              Birth Place
            </label>
            <LocationAutocomplete
              value={formData.place || ''}
              onChange={(location) => {
                setSelectedLocation(location);
                if (location) {
                  setFormData(prev => ({
                    ...prev,
                    place: location.displayName,
                    city: location.city,
                    country: location.country,
                    latitude: location.latitude,
                    longitude: location.longitude,
                    timezone: location.timezone,
                  }));
                }
              }}
              placeholder="Search city (e.g., bangalore, ban...)"
              className="w-full"
            />
          </div>

          {/* Coordinates (auto-filled from location selection) */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Latitude
              </label>
              <input
                type="number"
                step="any"
                readOnly
                value={formData.latitude || ''}
                className="w-full px-4 py-3 rounded-lg glass border border-white/20 bg-gray-50 dark:bg-gray-800/50 text-gray-900 dark:text-gray-100 cursor-not-allowed"
                placeholder="Auto-filled"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Longitude
              </label>
              <input
                type="number"
                step="any"
                readOnly
                value={formData.longitude || ''}
                className="w-full px-4 py-3 rounded-lg glass border border-white/20 bg-gray-50 dark:bg-gray-800/50 text-gray-900 dark:text-gray-100 cursor-not-allowed"
                placeholder="Auto-filled"
              />
            </div>
          </div>

          {error && (
            <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400">
              {error}
            </div>
          )}

          <div className="flex gap-4">
            <motion.button
              type="submit"
              disabled={loading}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="flex-1 py-4 rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition-smooth"
            >
              {loading ? 'Processing...' : 'Generate Chart'}
            </motion.button>
            
            {birthDetails && (
              <motion.button
                type="button"
                onClick={handleClear}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="px-6 py-4 rounded-lg glass border border-white/20 hover:border-red-500/50 text-gray-700 dark:text-gray-300 font-semibold transition-smooth"
              >
                Clear & Reset
              </motion.button>
            )}
          </div>
        </form>
      </div>
    </SlideUp>
  );
}

