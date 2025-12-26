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
import { submitBirthDetails, BirthDetails, LocationSuggestion, handleError } from '@/services/api';
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
      if (process.env.NODE_ENV === 'development') {
        console.log('📍 Location selected:', {
          displayName: selectedLocation.displayName,
          city: selectedLocation.city,
          country: selectedLocation.country,
          latitude: selectedLocation.latitude,
          longitude: selectedLocation.longitude,
          timezone: selectedLocation.timezone,
        });
      }
      
      setFormData(prev => ({
        ...prev,
        latitude: selectedLocation.latitude,
        longitude: selectedLocation.longitude,
        place: selectedLocation.displayName,
        city: selectedLocation.city,
        country: selectedLocation.country,
        timezone: selectedLocation.timezone,
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

      // Validate coordinates are present
      if (!formData.latitude || !formData.longitude || !selectedLocation?.latitude || !selectedLocation?.longitude) {
        throw new Error('Please select a location from the suggestions to get coordinates');
      }

      // Get coordinates from selected location (required)
      if (!selectedLocation?.latitude || !selectedLocation?.longitude) {
        throw new Error('Location not selected properly. Please select a location from the suggestions.');
      }

      const details: BirthDetails = {
        date: formData.date!,
        time: formData.time!,
        city: selectedLocation.city || formData.city || formData.place?.split(',')[0] || '',
        country: selectedLocation.country || formData.country || formData.place?.split(',')[1]?.trim() || '',
        latitude: selectedLocation.latitude,
        longitude: selectedLocation.longitude,
        timezone: selectedLocation.timezone || formData.timezone || 'UTC',
      };

      // Development mode: Log the payload
      if (process.env.NODE_ENV === 'development') {
        console.log('📤 Submitting birth details:', {
          date: details.date,
          time: details.time,
          city: details.city,
          country: details.country,
          latitude: details.latitude,
          longitude: details.longitude,
          timezone: details.timezone,
        });
      }

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
      // CRITICAL: router.push can throw runtime errors (navigation errors)
      // These are NOT Axios errors and must be handled separately
      try {
        router.push('/dashboard');
      } catch (navError: any) {
        // Navigation/runtime error - NOT an API error
        const { message } = handleError(navError, "BirthDetailsForm.navigation");
        setError(`Navigation error: ${message}`);
        return; // Don't continue if navigation fails
      }
    } catch (err: any) {
      // CRITICAL: Properly classify error (Axios vs runtime)
      // submitBirthDetails uses axios, so errors here are likely Axios errors
      // But we must check because router.push errors could bubble up
      const { message, isAxiosError } = handleError(err, "BirthDetailsForm.submit");
      
      // Extract user-friendly message
      let errorMessage = message;
      
      // If it's an Axios error, provide more context
      if (isAxiosError) {
        if (err?.response?.status === 404) {
          // This is handled by the API service workaround, but just in case
          errorMessage = 'Birth details endpoint not available. Using local storage.';
        } else if (err?.response?.status >= 500) {
          errorMessage = 'Server error. Please try again later.';
        }
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

